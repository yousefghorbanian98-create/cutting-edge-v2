# ADR-0009 — CI is the outermost self-check: SHA-pinned actions, least privilege, Skip ≠ Pass, public annotations

## Status
Accepted — 2026-09-22

## Context
S-009 replaced a main-only Windows pytest workflow with a matrix. The first real run failed for reasons the sandbox could not see: job logs and artifacts require an authenticated token, and the Arena GitHub token expired mid-run (second occurrence, see `docs/learnings/`). The failure itself was a MISSING check (cargo) silently accepted locally but executed on runners that have cargo.

## Decision
- Three stable job ids — `ci / ubuntu`, `ci / windows`, `ci / loop-audit` — on push to `main` + `arena/**` and on PRs; CodeQL and Dependabot enabled; gitleaks over full history.
- Every third-party action pinned to a 40-char commit SHA with a `# vX` comment; top-level `permissions: contents: read`, elevated per job only where needed. Enforced by `tests/unit/test_ci_workflows.py`.
- The gate runs with `--strict-missing` in CI; a check that one job cannot own is `--skip`ped explicitly and owned by another job (cargo → windows). Tests that tolerate `MISSING` locally must pin the same behaviour in CI.
- Failures must be **public**: `scripts/ci/junit_annotate.py` and gate `::error` lines turn junit/gate failures into check-run annotations readable without a token; evidence artifacts (junit, Playwright report, screenshots, gate JSON) are uploaded with `if-no-files-found: error`.
- Ledger GREEN for environment-dependent ACs cites the CI run URL; `supervise.py` C11 treats in-progress runs as pending and completed non-success as FAIL.

## Consequences
- Positive: supply-chain hardening at no cost; the loop can diagnose CI from annotations alone; Windows-only behaviour (bash/signals/paths) is exercised before a step is GREEN.
- Negative: SHA pins need Dependabot PRs to stay current (grouped weekly); the Windows job costs ~6–10 min per push.
- Follow-ups: S-010 flips the cargo steps from advisory to hard (BUG-16); `release.yml` arrives with S-027; branch protection (requires admin) is a user action at publish time.
