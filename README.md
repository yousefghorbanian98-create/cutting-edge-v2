# Cutting Edge v2.0

یک فضای کاری مدرن برای تدوین ویدیو با **AI Copilot**، تایم‌لاین زنده، Media Bin و ابزار **Muscle Enhancer**. رابط کاربری با Next.js ساخته شده و موتور اختیاری Python برای پردازش ویدیو در `ai-engine/` قرار دارد.

## اجرای سریع رابط کاربری

پیش‌نیاز: Node.js نسخه LTS. در پوشه اصلی پروژه اجرا کنید:

```powershell
npm install
npm run dev
```

سپس آدرس `http://localhost:3000` را باز کنید. اگر pnpm ترجیح می‌دهید:

```powershell
npm install -g pnpm
pnpm install
pnpm dev
```

> نسخه فعلی رابط کاربری در مرورگر اجرا می‌شود. برای بسته‌بندی Tauri باید Rust و ابزارهای build ویندوز نیز نصب شوند.

## راه‌اندازی خودکار AI در ویندوز

برای اینکه کلید شما هرگز در چت، تاریخچه ترمینال یا Git نمایش داده نشود، PowerShell را در ریشه پروژه باز کنید و اجرا کنید:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\\scripts\\setup-ai.ps1
```

اسکریپت به‌صورت محلی محیط مجازی را می‌سازد، وابستگی‌ها را نصب می‌کند و کلید را به‌صورت مخفی دریافت می‌کند. کلید فقط در فایل `ai-engine/.env` ذخیره می‌شود و این فایل در Git نادیده گرفته شده است.

## فعال‌سازی Python AI Core در ویندوز

پیش‌نیازها: Python 3.10 یا 3.11 و (اختیاری) Rust برای نسخه دسکتاپ. در زمان نصب Python گزینه **Add Python to PATH** را فعال کنید.

```powershell
cd ai-engine
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m uvicorn src.main:app --host 127.0.0.1 --port 8001 --reload
```

اگر PyTorch/CUDA برای pipeline اختصاصی خود نیاز دارید، آن را جداگانه متناسب با درایور نصب کنید؛ health endpoint این نسخه به PyTorch وابسته نیست. تست موفقیت:

```text
http://127.0.0.1:8001/health
```

این endpoint درصد RAM و CPU و وضعیت Reheal را برمی‌گرداند.

## تست Muscle Enhancer روی ویدیو

فایل کوتاه MP4 را با نام `test_workout.mp4` داخل `ai-engine` قرار دهید، سپس در حالی که محیط مجازی فعال است:

```powershell
python src/muscle/muscle_enhancer.py
```

خروجی در `ai-engine/test_workout_enhanced.mp4` ساخته می‌شود. برای تنظیم شدت:

```powershell
python src/muscle/muscle_enhancer.py test_workout.mp4 --output preview.mp4 --intensity 0.7
```

این پردازش فقط کنتراست محلی و جزئیات نور را به‌صورت طبیعی تغییر می‌دهد و هندسه بدن را دستکاری نمی‌کند.

## ساخت production

```powershell
npm run build
```
