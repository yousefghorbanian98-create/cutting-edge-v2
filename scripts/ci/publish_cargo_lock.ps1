# S-010 / BUG-17 — the authoring sandbox cannot read the runner's Cargo.lock:
# artifact zips and job logs live on blob storage (TLS reset from the sandbox),
# and the job-summary markdown is not in the REST API (summary_raw 404s).
# This step runs ON the runner that just resolved the lock and commits it
# through the contents API (readable, no blob). A later commit switches cargo
# to --locked. Idempotent: if the path is already tracked at HEAD, it no-ops.
#
# Also emits gzip+base64 as ::notice annotations (title "Cargo.lock i/n") so a
# failed PUT can still be reconstructed from the check-run annotations API.
# Those chunks are omitted once the lock is already tracked: they filled the
# 10-annotation step budget and dropped the evidence sidecar notice.

[CmdletBinding()]
param(
    [string]$LockPath = "apps/desktop/src-tauri/Cargo.lock",
    [int]$Chunk = 3500
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $LockPath)) {
    Write-Error "Cargo.lock not found at $LockPath (cargo has not resolved yet)"
    exit 1
}

$full = (Resolve-Path -LiteralPath $LockPath).Path
$bytes = [IO.File]::ReadAllBytes($full)
$sha = (Get-FileHash -LiteralPath $full -Algorithm SHA256).Hash
Write-Output "::notice title=Cargo.lock::$($bytes.Length) bytes sha256 $sha"

git ls-files --error-unmatch -- $LockPath *> $null
if ($LASTEXITCODE -eq 0) {
    Write-Output "::notice title=Cargo.lock::already tracked at HEAD; skip publish; base64 chunks omitted"
    exit 0
}

$ms = New-Object IO.MemoryStream
$gz = New-Object IO.Compression.GzipStream($ms, [IO.Compression.CompressionLevel]::Optimal)
$gz.Write($bytes, 0, $bytes.Length)
$gz.Dispose()
$packed = [Convert]::ToBase64String($ms.ToArray())
$n = [int][Math]::Ceiling($packed.Length / [double]$Chunk)
if ($n -lt 1) { $n = 1 }
Write-Output "::notice title=Cargo.lock parts::$n chunks sha256 $sha"
for ($i = 0; $i -lt $n; $i++) {
    $take = [Math]::Min($Chunk, $packed.Length - ($i * $Chunk))
    $part = $packed.Substring($i * $Chunk, $take)
    $idx = $i + 1
    Write-Output "::notice title=Cargo.lock ${idx}/${n}::$part"
}

if ($env:GITHUB_EVENT_NAME -and $env:GITHUB_EVENT_NAME -ne "push") {
    Write-Output "::notice title=Cargo.lock::skip publish on event $($env:GITHUB_EVENT_NAME)"
    exit 0
}

if (-not $env:GH_TOKEN) { $env:GH_TOKEN = $env:GITHUB_TOKEN }
if (-not $env:GH_TOKEN) {
    Write-Error "GH_TOKEN/GITHUB_TOKEN missing; cannot publish Cargo.lock"
    exit 1
}
if (-not $env:GITHUB_REPOSITORY -or -not $env:GITHUB_REF_NAME) {
    Write-Error "GITHUB_REPOSITORY / GITHUB_REF_NAME missing"
    exit 1
}

$content = [Convert]::ToBase64String($bytes)
$message = "chore(desktop): S-010 capture runner Cargo.lock sha256 $sha (BUG-17)"
# Base64 is [A-Za-z0-9+/=] — no JSON escaping required. Branch is a ref name.
$json = '{"message":"' + $message + '","content":"' + $content + '","branch":"' + $env:GITHUB_REF_NAME + '"}'
$tmp = Join-Path ([IO.Path]::GetTempPath()) "cargo-lock-put.json"
$utf8 = New-Object System.Text.UTF8Encoding $false
[IO.File]::WriteAllText($tmp, $json, $utf8)

Write-Output "::notice title=Cargo.lock publish::PUT contents API branch $($env:GITHUB_REF_NAME) $($bytes.Length) bytes"
gh api --method PUT "repos/$($env:GITHUB_REPOSITORY)/contents/$LockPath" --input $tmp
if ($LASTEXITCODE -ne 0) {
    Write-Error "contents API PUT failed (exit $LASTEXITCODE). Reconstruct from Cargo.lock i/n notices if needed."
    exit $LASTEXITCODE
}
Write-Output "::notice title=Cargo.lock published::branch $($env:GITHUB_REF_NAME) sha256 $sha"
