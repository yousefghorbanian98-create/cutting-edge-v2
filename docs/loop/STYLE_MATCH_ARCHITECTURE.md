# Style Match — implementation direction

> برنامه‌ریزی معماری؛ این فایل کد محصول یا تست اجرایی نیست. منبع تصمیم برای کارت‌های S-012، S-040، S-045، S-046، S-048، S-055 و S-056 است.

## هدف

Style Match باید یک دستیار قابل توضیح باشد، نه یک فیلتر یا یک `similarity score` مبهم:

```text
observe → explain → plan → execute → validate → revise
```

از ویدیوی مرجع و ویدیوی کاربر برای هرکدام یک `Style Signature` نسخه‌دار می‌سازیم و این محورها را جداگانه مقایسه می‌کنیم:

- semantic content
- composition و subject placement
- palette، lighting و contrast
- shot duration و cut density
- motion و temporal consistency
- pose و crop safety
- speech، silence و music energy

خروجی هر محور باید `score`، `confidence`، توضیح، و timestampهای evidence داشته باشد؛ خروجی نهایی فقط یک عدد نیست.

## معماری مرحله‌ای

1. **CPU-first baseline:** FFmpeg، OpenCV، PySceneDetect، color/histogram، shot duration، optical-flow محدود و audio energy.
2. **Feature adapters:** semantic encoder اختیاری مانند OpenCLIP و pose adapter؛ هر مدل با cache، version، license metadata، CPU fallback و memory estimate.
3. **Style Signature:** نتیجهٔ per-shot به یک signature قابل cache با hash فایل و نسخهٔ الگوریتم aggregate می‌شود.
4. **Planner:** مدل زبانی فقط JSON مطابق schema تولید می‌کند؛ هر action باید محدود، reversible و دارای دلیل و confidence باشد.
5. **Executor:** فقط actionهای allow-list شده را با FFmpeg/OpenCV اجرا می‌کند، checkpoint می‌سازد، progress/cancel دارد و خروجی را validate یا rollback می‌کند.
6. **Memory:** فقط signature، plan تأییدشده و preference کاربر ذخیره می‌شود؛ media خام بدون اجازه نگه‌داری نمی‌شود.

## محدودیت سخت‌افزار

هدف اولیه `GTX 1650 4GB / RAM 16GB` است. فقط یک GPU inference job هم‌زمان مجاز است؛ کارهای CPU می‌توانند هم‌زمان اجرا شوند. مدل‌ها پیش‌فرض داخل installer bundle نمی‌شوند. model swapping اختیاری است و باید با benchmark واقعی و حاشیهٔ امن VRAM اثبات شود، نه با تخمین weight size.

## تصمیم‌های منفی

- افزودن Kdenlive، Shotcut، Olive، Blender یا PySide6/Gradio به runtime ممنوع؛ frontend فعلی Next/Tauri مرجع است.
- Ollama وارد stack نمی‌شود؛ LLM باید از adapter/provider موجود استفاده کند.
- Ultralytics YOLO بدون تصمیم license مستقل وارد نمی‌شود؛ AGPL/Enterprise باید پیش از هر استفاده بررسی شود.
- BLIP/LAVIS، Demucs، madmom و مدل‌های بزرگ فقط بعد از benchmark و license audit قابل بررسی‌اند.
- raw command یا parameter از LLM اجرا نمی‌شود؛ plan باید schema-validated باشد.

## معیار کیفیت

هر پیشنهاد Style Match باید با before/after measurement، playable output، audio/video sync، resolution، frame rate، subject visibility و temporal stability بررسی شود. نبود مدل، audio یا GPU `MISSING`/`unverified` است و هرگز `PASS` محسوب نمی‌شود.

## وابستگی به مراحل

- `S-012`: job model، GPU lock، progress، cancel و عدم block شدن `/health`.
- `S-040`: ویژگی‌های زمانی و energy؛ پایهٔ مشترک Style Match و Content Strategy.
- `S-045`: Style DNA و signature قابل cache.
- `S-046`: مقایسه، diff، plan و Apply Style با تأیید کاربر.
- `S-048`: transition intelligence فقط بعد از validated plan.
- `S-055`: استفاده از featureهای ثبت‌شده برای hook و virality، بدون ادعای causal score.
- `S-056`: cache بر اساس content hash، offline UX و allow-list مدل/provider.

هر مرحله قرارداد، تست واقعی، شواهد و review مستقل خودش را دارد؛ این سند به‌تنهایی scope مرحلهٔ جاری را تغییر نمی‌دهد.
