$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
$aiDir = Join-Path $root 'ai-engine'
$envPath = Join-Path $aiDir '.env'

Write-Host 'Cutting Edge - AI Core setup' -ForegroundColor Cyan
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
  throw 'Python پیدا نشد. Python 3.10 یا 3.11 را نصب کنید و دوباره اجرا کنید.'
}

$secureKey = Read-Host 'OpenRouter API key را وارد کنید (ورودی مخفی است)' -AsSecureString
$ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureKey)
try { $apiKey = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr) }
finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr) }
if ([string]::IsNullOrWhiteSpace($apiKey)) { throw 'کلید خالی است.' }

Push-Location $aiDir
try {
  if (-not (Test-Path 'venv\Scripts\python.exe')) {
    Write-Host 'در حال ساخت محیط مجازی Python...' -ForegroundColor Yellow
    python -m venv venv
  }
  Write-Host 'در حال نصب وابستگی‌های AI...' -ForegroundColor Yellow
  & '.\venv\Scripts\python.exe' -m pip install --upgrade pip
  & '.\venv\Scripts\python.exe' -m pip install -r requirements.txt
  Set-Content -Path $envPath -Value "OPENROUTER_API_KEY=$apiKey" -Encoding utf8
  Write-Host "فایل تنظیمات ساخته شد: $envPath" -ForegroundColor Green
  Write-Host 'برای اجرای سرور:' -ForegroundColor Cyan
  Write-Host '.\venv\Scripts\python.exe -m uvicorn src.main:app --host 127.0.0.1 --port 8001 --reload'
} finally { Pop-Location }
