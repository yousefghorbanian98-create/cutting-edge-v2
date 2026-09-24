# REVIEW — S-012 — round 1 — commit 93ede826c00a1bde298936ce6596a7c3f3f5d9df

> نوشته‌شده توسط **Reviewer تازه**؛ بررسی بر اساس CONTRACT مرحله، diff مرحله و وضعیت CI انجام شد.

CI: not completed for target SHA (no CI run found for `93ede826c00a1bde298936ce6596a7c3f3f5d9df`)
Evidence re-produced by reviewer: partially (local AC tests reproduced; Windows CI and BUG-11 closure not reproduced for target SHA)

## Summary
S-012 پردازش سنگین را از event loop جدا می‌کند، مدل job و polling/cancel را نگه می‌دارد، و یک مسیر اختیاری `inference` با یک GPU slot، CPU fallback و وضعیت `unverified` فراهم می‌کند. API عمومی `JobView` ثابت نگه داشته شده است.

## 1. Must fix before GREEN
- [CI] برای target SHA هیچ run کامل CI پیدا نشد. AC-1 تا AC-6 و BUG-11 باید در `ci / windows` روی همین SHA اجرا و سبز شوند؛ نتیجهٔ CI روی commitهای قبلی برای این commit قابل انتقال نیست.

## 2. Should fix soon (non-blocking → کارت hotfix یا notes)
- مسیرهای فعلی heavy از `jobs.submit()` معمولی استفاده می‌کنند و هنوز `kind="inference"` نیستند؛ این با NG-7 که مدل‌های Style Match در S-012 ساخته نمی‌شوند سازگار است. وقتی اولین مدل Style Match اضافه شد، آن مسیر باید صریحاً از `submit_inference()` استفاده کند تا GPU lock واقعاً اعمال شود.

## 3. Verdict
changes-requested — تست‌های محلی نام‌برده و تست‌های scheduler سبز هستند، اما CI دقیق target SHA وجود ندارد و BUG-11 هنوز طبق قرارداد باز است.

## Reproduction notes

- `tests/unit/test_loop_tooling.py` + `tests/unit/test_ci_workflows.py` + `tests/unit/test_job_scheduler.py`: 24 passed.
- `tests/test_jobs.py -m real`: 2 passed, 1 warning مربوط به نبود fixture شبکه.
- `test_one_gpu_inference_at_a_time_cpu_job_still_runs`: passed.
- `test_missing_gpu_is_unverified_and_falls_back_to_cpu`: passed.
- `test_host_probe_does_not_report_gpu_pass`: passed.
- `test_forbidden_style_match_runtimes_are_absent`: passed.
