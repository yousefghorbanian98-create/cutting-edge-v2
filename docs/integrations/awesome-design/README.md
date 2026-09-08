# Awesome Design Integration

> **Source:** `VoltAgent/awesome-design-md` — 114K stars, Global #99, MIT
> Repo: https://github.com/VoltAgent/awesome-design-md — Format: https://stitch.withgoogle.com/docs/design-md/format/

## چیست؟
مجموعه 73 فایل `DESIGN.md` استخراج شده از سایت‌های واقعی (Linear, Vercel, Stripe, Notion, Apple, Tesla...) به صورت markdown ساده که عامل AI مستقیم می‌خواند. هر فایل 500-700 خط + `preview.html` دارد.

- **v. کلاسیک** `alexpate/awesome-design-systems` (25.9K) فقط لیست لینک است — برای AI به کار نمی‌آید و وارد نشد.

## کجا نصب شد؟
```
design-md/DESIGN.linear.md  (548 lines — near-black #010102 + blurple #5E6AD2)
design-md/DESIGN.vercel.md  (736 lines — Swiss grid, Geist)
design-md/DESIGN.stripe.md  (487 lines — gradient, marketing)
DESIGN.md                   (ROOT — Hybrid اختصاصی cutting-edge-v2) ← مرجع اصلی Agent
```

## DESIGN.md ریشه چیست؟
یک سیستم هیبرید که از 3 تا الهام اصلی ترکیب شد:
- **Canvas:** Linear's #010102 (عمیق‌ترین مشکی)
- **Typography:** Vercel's Geist Sans
- **Accent:** Stripe/Linear's blurple #5E6AD2 (تک رنگ)

این فایل در ریشه است تا هر Agent آن را به عنوان **Single Source of Truth بصری** بخواند — دستور `Use DESIGN.md for all styling`.

## چگونه استفاده می‌شود؟
1. الهام: یکی از `design-md/DESIGN.*.md` را باز کن
2. مرجع: `DESIGN.md` ریشه را بخوان
3. ساخت: با Tailwind + shadcn بساز
4. چک: با Web Design Guidelines Skill audit کن

```bash
# انتخاب سریع الهام دیگر
./scripts/select-design.sh vercel   # اگر اسکریپت اضافه شد
# یا دستی:
cp design-md/DESIGN.vercel.md DESIGN.md
```

## چرا فقط 3 تا + هیبرید؟
کپی 73 فایل → سردرگمی. ما 3 تا متنوع را به عنوان مرجع نگه داشتیم و یک هیبرید اختصاصی ساختیم تا هویت cutting-edge-v2 یکپارچه بماند.

## Preview
هر DESIGN.md در ریپو اصلی VoltAgent یک `preview.html` و `preview-dark.html` دارد — برای دیدن کاتالوگ به https://github.com/VoltAgent/awesome-design-md برو.

## آپدیت
- `DESIGN.md` ریشه را با هر تصمیم برند جدید آپدیت کن (رنگ/تایپو)
- `design-md/` فقط مرجع است — تغییرش نده، مگر الهام جدید بخواهی
