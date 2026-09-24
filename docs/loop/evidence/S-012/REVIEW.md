# REVIEW — S-012 — round 1 — commit 93ede826c00a1bde298936ce6596a7c3f3f5d9df

> نوشته‌شده توسط **Reviewer تازه**؛ بررسی بر اساس CONTRACT مرحله، diff مرحله و وضعیت CI انجام شد.

CI: passed ([run 35999861447](https://github.com/yousefghorbanian98-create/cutting-edge-v2/actions/runs/35999861447))
Evidence re-produced by reviewer: yes (all named S-012 tests reproduced locally; Windows CI and BUG-11 closure reproduced on the target SHA)

## Summary
S-012 پردازش سنگین را از event loop جدا می‌کند، مدل job و polling/cancel را نگه می‌دارد، و یک مسیر اختیاری `inference` با یک GPU slot، CPU fallback و وضعیت `unverified` فراهم می‌کند. API عمومی `JobView` ثابت نگه داشته شده است.

## 1. Must fix before GREEN
- None.

## 2. Should fix soon (non-blocking → کارت hotfix یا notes)
- مسیرهای فعلی heavy از `jobs.submit()` معمولی استفاده می‌کنند و هنوز `kind="inference"` نیستند؛ این با NG-7 که مدل‌های Style Match در S-012 ساخته نمی‌شوند سازگار است. وقتی اولین مدل Style Match اضافه شد، آن مسیر باید صریحاً از `submit_inference()` استفاده کند تا GPU lock واقعاً اعمال شود.

## 3. Verdict
approved — تمام تست‌های AC و scheduler محلی سبز هستند؛ CI کامل target SHA سبز است و BUG-11 با شواهد Windows بسته شده است.

## Reproduction notes

- `tests/unit/test_loop_tooling.py` + `tests/unit/test_ci_workflows.py` + `tests/unit/test_job_scheduler.py`: 24 passed.
- `tests/test_jobs.py -m real`: 2 passed, 1 warning مربوط به نبود fixture شبکه.
- `test_one_gpu_inference_at_a_time_cpu_job_still_runs`: passed.
- `test_missing_gpu_is_unverified_and_falls_back_to_cpu`: passed.
- `test_host_probe_does_not_report_gpu_pass`: passed.
- `test_forbidden_style_match_runtimes_are_absent`: passed.

## Independent review — dependency hold — target `ab409cd0d2ead26dc21b0ee10efab66397f80cda`

S-012 evidence and implementation were inspected; no new S-012 product regression was found. However, S-012 depends on S-006's artifact assertion layer, and S-006 remains REVIEW pending fresh evidence.

- Verdict: **REVIEW — dependency hold; not approved and not GREEN**.
- Do not change S-012 status until S-006 is independently approved and the existing S-012 CI evidence remains applicable.

## Independent review — dependency release — target `4b3204abe1ae6ee5ba98f7720be94de228177e3f`

S-006 is now independently approved for the next ledger decision. The same CI run passed the Windows pytest suite and the S-012 evidence remains valid; the health path no longer blocks on the GPU probe and the 0.2s budget was not relaxed.

Verdict: **approved for Builder's next ledger decision**. Status remains REVIEW; Overseer does not GREEN it.
