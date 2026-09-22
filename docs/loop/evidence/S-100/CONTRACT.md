# CONTRACT — S-100 — UI guidelines audit gate (offline Web Interface Guidelines checker) wired into gate static

> Builder: Supervisor session (autonomous chain). Deps: S-099 GREEN.

## Acceptance Criteria

| # | Criterion | Proof |
|---|-----------|-------|
| AC-1 | `scripts/design_audit.py <paths> [--warn|--strict] [--json]` implements 8 deterministic rules from the offline snapshot `docs/integrations/web-guidelines/web-interface-guidelines.md`: `icon-button-label`, `outline-none-focus`, `transition-all`, `div-click`, `img-alt-dims`, `hardcoded-format`, `reduced-motion`, `input-label`; fixture `tests/fixtures/ui/violations.tsx` with exactly 8 known violations → exactly 8 findings, each at the correct line | `tests/unit/test_design_audit.py::test_violations_fixture_exact` |
| AC-2 | `tests/fixtures/ui/clean.tsx` (same constructs done right + one justified `wig-ignore`) → 0 findings, exit 0 in `--strict` | `::test_clean_fixture_zero` |
| AC-3 | Output is one finding per line `file:line rule message`; default/`--warn` exits 0, `--strict` exits 1 on any finding; `--json` for tooling | `::test_output_format_and_modes` |
| AC-4 | Suppression only via `// wig-ignore <rule>: <why> (S-xxx)` on the line above / inside the tag; an ignore without a step id → `invalid-ignore`; unknown rule → `invalid-ignore`; an ignore that suppresses nothing → `unused-ignore` | `::test_ignore_grammar` |
| AC-5 | Run on the real `apps/desktop/src` reports the real findings of `page.tsx` / `CommandPalette.tsx` (17 before) and every one is **fixed in place** or referred with a justified ignore; `--strict` → 0 findings; gate `design-audit` PASS (`12 pass / 0 fail / 0 missing / 1 skip`); `next build` + `build-artifacts.spec.ts` still green; `pnpm design:audit` script | `::test_real_ui_tree_is_clean`, `::test_real_tree_ignores_are_justified`, `gate.py` |
| AC-6 | CI runs it: `ci / ubuntu` gate step already executes `gate.py --stage static --strict-missing` → includes `design-audit`; `gate.py` returns `MISSING` (not SKIP) if the script disappears | `tests/unit/test_gate.py` (strict-missing semantics), CI run on the pushed commit |

## Non-Goals
| # | Not in this step | Owner |
|---|------------------|-------|
| NG-1 | No browser-based checks (axe, contrast, focus order) | S-084 |
| NG-2 | No redesign of `page.tsx` beyond the WIG fixes (labels, focus ring, transition props, reduced-motion) — colours/tokens migration | S-013/S-015 |
| NG-3 | Rules that need type info or runtime (virtualisation of large lists, `autoFocus` justification, paste blocking) are not implemented; listed in the script docstring as future rules | S-084 |
| NG-4 | Native `<dialog>` for the Command Palette | S-084 (ignore recorded) |

## U-decisions
None.
