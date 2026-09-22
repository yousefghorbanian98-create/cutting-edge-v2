# User-machine smoke (S-011 contract, S-027 fills the real probes).
# Always prints one JSON object, then exits. A failed probe is exit 1, never silence.
# -DryRun proves the JSON contract without claiming the machine passed (CI uses this).
[CmdletBinding()]
param(
    [string]$Report = "",
    [string]$BackendUrl = "",
    [string]$AppExe = "",
    [switch]$DryRun
)

$ErrorActionPreference = "Continue"
if (-not $BackendUrl) { $BackendUrl = $env:CE_BACKEND_URL }
if (-not $AppExe) { $AppExe = $env:CE_APP_EXE }

function New-Check([string]$Name, [bool]$Ok, [string]$Detail) {
    return [ordered]@{ name = $Name; ok = $Ok; detail = $Detail }
}

$checks = @()
$appLaunch = $false
$backendHealth = $false
$importOk = $false
$gpuName = $null
$vramMb = $null

if ($DryRun) {
    $checks += New-Check "schema" $true "dry-run: hardware and app were not probed"
} else {
    $smi = Get-Command nvidia-smi -ErrorAction SilentlyContinue
    if ($smi) {
        try {
            $q = & nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits 2>&1 | Select-Object -First 1
            if ($LASTEXITCODE -eq 0 -and $q) {
                $parts = "$q".Split(",")
                $gpuName = $parts[0].Trim()
                $vramMb = [int]($parts[1].Trim())
                $checks += New-Check "gpu" $true "$gpuName $vramMb MB"
            } else {
                $checks += New-Check "gpu" $false "nvidia-smi failed: $q"
            }
        } catch {
            $checks += New-Check "gpu" $false $_.Exception.Message
        }
    } else {
        $checks += New-Check "gpu" $false "nvidia-smi not on PATH"
    }

    if ($BackendUrl) {
        try {
            $resp = Invoke-WebRequest -Uri ($BackendUrl.TrimEnd("/") + "/health") -UseBasicParsing -TimeoutSec 5
            $backendHealth = ($resp.StatusCode -eq 200)
            $checks += New-Check "backend_health" $backendHealth "status $($resp.StatusCode)"
        } catch {
            $checks += New-Check "backend_health" $false $_.Exception.Message
        }
    } else {
        $checks += New-Check "backend_health" $false "CE_BACKEND_URL not set"
    }

    if ($AppExe -and (Test-Path -LiteralPath $AppExe)) {
        $checks += New-Check "app_launch" $true "exe exists: $AppExe"
        if ($env:CE_SMOKE_LAUNCH -eq "1") {
            $proc = Start-Process -FilePath $AppExe -PassThru
            Start-Sleep -Seconds 2
            if ($proc.HasExited) {
                $appLaunch = $false
                $checks += New-Check "app_launch" $false "exited $($proc.ExitCode)"
            } else {
                $appLaunch = $true
                Stop-Process -Id $proc.Id -Force
            }
        } else {
            $appLaunch = $true
        }
    } else {
        $checks += New-Check "app_launch" $false "CE_APP_EXE not set or missing"
    }

    $sample = $env:CE_SMOKE_IMPORT
    if ($sample -and (Test-Path -LiteralPath $sample)) {
        $importOk = $true
        $checks += New-Check "import_ok" $true $sample
    } else {
        $checks += New-Check "import_ok" $false "CE_SMOKE_IMPORT not set or missing"
    }
}

$failed = @($checks | Where-Object { -not $_.ok }).Count
$ok = (-not $DryRun) -and ($failed -eq 0) -and $appLaunch -and $backendHealth -and $importOk

$doc = [ordered]@{
    ok              = [bool]$ok
    dry_run         = [bool]$DryRun
    app_launch      = [bool]$appLaunch
    backend_health  = [bool]$backendHealth
    import_ok       = [bool]$importOk
    gpu_name        = $gpuName
    vram_mb         = $vramMb
    checks          = @($checks)
}

$json = $doc | ConvertTo-Json -Depth 6 -Compress
Write-Output $json
if ($Report) {
    $dir = Split-Path -Parent $Report
    if ($dir -and -not (Test-Path -LiteralPath $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    Set-Content -LiteralPath $Report -Value $json -Encoding utf8
}

if ($DryRun) { exit 0 }
if (-not $ok) { exit 1 }
exit 0
