# S-010 — real installer smoke on the windows runner (no mocks):
#   1. locate the NSIS installer produced by `tauri build`
#   2. silent install (/S, per-user → no UAC) and verify files / registry / shortcut
#   3. launch the installed exe and wait for a top-level window titled "Cutting Edge"
#   4. silent uninstall and verify nothing is left behind (dir, registry, shortcut)
# Every check writes a JSON line to $Report so EVIDENCE.md can quote it verbatim.
# Exit code is non-zero on the first failed assertion; the uninstall still runs
# (finally) so a red run never leaves a stale install in the runner's cache.

[CmdletBinding()]
param(
    [string]$BundleDir = "apps/desktop/src-tauri/target/release/bundle/nsis",
    [string]$ProductName = "Cutting Edge",
    [string]$ExeName = "cutting-edge.exe",
    [string]$Report = "reports/installer-smoke.jsonl",
    [int]$WindowTimeoutSec = 60
)

$ErrorActionPreference = "Stop"
$failures = 0
New-Item -ItemType Directory -Force -Path (Split-Path $Report) | Out-Null
if (Test-Path $Report) { Remove-Item $Report -Force }

function Check([string]$name, [bool]$ok, [string]$detail = "") {
    $line = [ordered]@{ check = $name; ok = $ok; detail = $detail; at = (Get-Date).ToString("o") } | ConvertTo-Json -Compress
    Add-Content -Path $Report -Value $line
    if ($ok) { Write-Host "  ok   $name  $detail" } else { Write-Host "::error title=installer smoke::$name — $detail"; $script:failures++ }
}

$installDir = Join-Path $env:LOCALAPPDATA $ProductName
$installedExe = Join-Path $installDir $ExeName
$uninstaller = Join-Path $installDir "uninstall.exe"
$uninstKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\$ProductName"
$shortcut = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\$ProductName.lnk"
$desktopLnk = Join-Path ([Environment]::GetFolderPath("Desktop")) "$ProductName.lnk"

# ── 1. installer artifact ────────────────────────────────────────────────────
$setup = Get-ChildItem -Path $BundleDir -Filter "*_x64-setup.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
Check "installer-exists" ($null -ne $setup) ($(if ($setup) { "$($setup.Name) ($([math]::Round($setup.Length / 1MB, 1)) MB)" } else { "no *_x64-setup.exe in $BundleDir" }))
if ($null -eq $setup) { exit 1 }
$ver = (Get-Item $setup.FullName).VersionInfo
Check "installer-version-info" ($ver.ProductName -eq $ProductName -and $ver.FileVersion -match '^\d+\.\d+\.\d+') "ProductName='$($ver.ProductName)' FileVersion='$($ver.FileVersion)'"

try {
    # ── 2. silent install ────────────────────────────────────────────────────
    $p = Start-Process -FilePath $setup.FullName -ArgumentList "/S" -PassThru -Wait
    Check "install-exit-0" ($p.ExitCode -eq 0) "exit $($p.ExitCode)"
    Check "installed-exe" (Test-Path $installedExe) $installedExe
    Check "uninstaller-present" (Test-Path $uninstaller) $uninstaller
    Check "uninstall-registry-key" (Test-Path $uninstKey) $uninstKey
    if (Test-Path $uninstKey) {
        $reg = Get-ItemProperty $uninstKey
        Check "registry-display-name" ($reg.DisplayName -eq $ProductName) "DisplayName='$($reg.DisplayName)' DisplayVersion='$($reg.DisplayVersion)'"
    }
    Check "start-menu-shortcut" (Test-Path $shortcut) $shortcut
    if (Test-Path $installedExe) {
        $exeInfo = (Get-Item $installedExe).VersionInfo
        Check "exe-version-info" ($exeInfo.ProductName -eq $ProductName) "ProductName='$($exeInfo.ProductName)' FileVersion='$($exeInfo.FileVersion)'"
    }

    # ── 3. launch → window title ─────────────────────────────────────────────
    if (Test-Path $installedExe) {
        $app = Start-Process -FilePath $installedExe -PassThru -WorkingDirectory $installDir
        $sw = [Diagnostics.Stopwatch]::StartNew()
        $title = ""
        $deadline = (Get-Date).AddSeconds($WindowTimeoutSec)
        while ((Get-Date) -lt $deadline) {
            Start-Sleep -Milliseconds 500
            $proc = Get-Process -Id $app.Id -ErrorAction SilentlyContinue
            if ($null -eq $proc) { break }
            $proc.Refresh()
            if ($proc.MainWindowTitle) { $title = $proc.MainWindowTitle; break }
        }
        $alive = $null -ne (Get-Process -Id $app.Id -ErrorAction SilentlyContinue)
        Check "app-still-running" $alive "pid $($app.Id) after $([int]$sw.Elapsed.TotalSeconds)s"
        Check "window-title" ($title -eq $ProductName) "MainWindowTitle='$title' (waited ≤ ${WindowTimeoutSec}s)"
        if ($alive) {
            $ws = (Get-Process -Id $app.Id).WorkingSet64
            Check "shell-working-set-lt-400mb" ($ws -lt 400MB) ("{0:N0} MB" -f ($ws / 1MB))
            Stop-Process -Id $app.Id -Force
            Start-Sleep -Seconds 2
        }
        $orphans = @(Get-Process -Name ($ExeName -replace '\.exe$', '') -ErrorAction SilentlyContinue)
        Check "no-orphan-process" ($orphans.Count -eq 0) "$($orphans.Count) left"
    }
}
finally {
    # ── 4. silent uninstall (NSIS copies itself to %TEMP% and exits early → poll) ──
    if (Test-Path $uninstaller) {
        Start-Process -FilePath $uninstaller -ArgumentList "/S" -Wait
        $deadline = (Get-Date).AddSeconds(90)
        while ((Get-Date) -lt $deadline -and (Test-Path $installDir)) { Start-Sleep -Seconds 1 }
        Check "uninstall-dir-removed" (-not (Test-Path $installDir)) $installDir
        Check "uninstall-registry-removed" (-not (Test-Path $uninstKey)) $uninstKey
        Check "uninstall-shortcut-removed" (-not (Test-Path $shortcut)) $shortcut
        Check "uninstall-desktop-shortcut-removed" (-not (Test-Path $desktopLnk)) $desktopLnk
    }
    else {
        Check "uninstaller-ran" $false "uninstall.exe was never installed"
    }
}

$total = (Get-Content $Report | Measure-Object -Line).Lines
Write-Host "installer smoke: $($total - $failures)/$total checks ok → $Report"
if ($failures -gt 0) { exit 1 }
