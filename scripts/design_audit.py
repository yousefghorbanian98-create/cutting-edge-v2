"""design_audit.py — offline, deterministic Web Interface Guidelines checker (S-100).

Rules are a fixed subset of the snapshot in
`docs/integrations/web-guidelines/web-interface-guidelines.md` (Vercel Labs, MIT)
that can be decided from source text without a browser. Output is one line per
finding — `file:line rule message` — so agents and CI read it the same way.

    python scripts/design_audit.py apps/desktop/src            # --warn by default (exit 0)
    python scripts/design_audit.py apps/desktop/src --strict   # exit 1 on any finding (gate / CI)
    python scripts/design_audit.py file.tsx --json

Suppress a single finding with a justified comment on the line above the tag
(or at the end of the same line):

    // wig-ignore icon-button-label: decorative, real control lands in S-047 (S-047)
    {/* wig-ignore input-label: label is the wrapping <label> two levels up (S-084) */}

The reason must name a step `(S-xxx)`; an ignore without one is itself a finding
(`invalid-ignore`), and an ignore that suppresses nothing is `unused-ignore`.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

RULES: dict[str, str] = {
    "icon-button-label": "icon-only <button> needs aria-label (or aria-labelledby/title)",
    "outline-none-focus": "outline-none without a focus-visible: replacement",
    "transition-all": "transition-all / transition: all — list properties (transition-colors, -opacity, -transform)",
    "div-click": "<div>/<span> with onClick needs role, tabIndex and onKeyDown — or use <button>",
    "img-alt-dims": "<img> needs alt and explicit width + height",
    "hardcoded-format": "date/number formatted by hand — use Intl.DateTimeFormat / Intl.NumberFormat",
    "reduced-motion": "animation without prefers-reduced-motion handling (useReducedMotion / motion-reduce:)",
    "input-label": "form control without <label> (htmlFor/wrapping) or aria-label",
    "invalid-ignore": "wig-ignore must be `wig-ignore <rule>: <why> (S-xxx)` with a known rule",
    "unused-ignore": "wig-ignore comment suppresses nothing",
}

IGNORE_RE = re.compile(r"wig-ignore\s+([a-z-]+)\s*:\s*(.+?)\s*(?:\*/|-->|$)")
STEP_RE = re.compile(r"\(S-\d{3}\)")
TAG_START_RE = re.compile(r"<([A-Za-z][\w.]*)\b")  # every JSX element; rules pick by name
ICON_CHILD_RE = re.compile(r"^\s*(?:\{[^{}]*\}\s*)*<([A-Z][A-Za-z0-9]*)\b[^>]*/>\s*(?:\{[^{}]*\}\s*)*$", re.S)
LOCALE_NOARG_RE = re.compile(r"\.toLocale(?:Date|Time)?String\(\s*\)")
DATE_PARTS_RE = re.compile(r"\.get(?:FullYear|Month|Date|Hours|Minutes)\(\)\s*[}+]")
ANIMATION_RE = re.compile(r"\banimate-(?!none\b)[a-z-]+|<motion\.[a-z]+|\banimate=\{|@keyframes|\banimation:")
REDUCED_OK_RE = re.compile(r"useReducedMotion|motion-reduce:|prefers-reduced-motion|MotionConfig\b[^>]*reducedMotion")


@dataclass
class Finding:
    file: str
    line: int
    rule: str
    message: str

    def render(self) -> str:
        return f"{self.file}:{self.line} {self.rule} {self.message}"


@dataclass
class Tag:
    name: str
    attrs: str
    line: int
    start: int
    end: int  # index just after '>'
    self_closing: bool


def _line_of(text: str, idx: int) -> int:
    return text.count("\n", 0, idx) + 1


def extract_tags(text: str) -> list[Tag]:
    """Find JSX opening tags for the elements we care about, tolerant of `{...}` and quoted attrs."""
    tags: list[Tag] = []
    for m in TAG_START_RE.finditer(text):
        i = m.end()
        depth = 0
        quote: str | None = None
        while i < len(text):
            c = text[i]
            if quote:
                if c == quote and text[i - 1] != "\\":
                    quote = None
            elif c in "\"'`":
                quote = c
            elif c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
            elif c == ">" and depth == 0:
                break
            i += 1
        if i >= len(text):
            break
        attrs = text[m.end() : i]
        self_closing = attrs.rstrip().endswith("/")
        tags.append(Tag(m.group(1), attrs, _line_of(text, m.start()), m.start(), i + 1, self_closing))
    return tags


def _children(text: str, tag: Tag) -> str:
    """Return the raw children of a non-self-closing tag (first matching close tag; nesting-aware)."""
    if tag.self_closing:
        return ""
    name = tag.name
    open_re = re.compile(rf"<{re.escape(name)}\b")
    close_re = re.compile(rf"</{re.escape(name)}\s*>")
    depth = 1
    i = tag.end
    while depth and i < len(text):
        o = open_re.search(text, i)
        c = close_re.search(text, i)
        if not c:
            return text[tag.end :]
        if o and o.start() < c.start():
            depth += 1
            i = o.end()
        else:
            depth -= 1
            if depth == 0:
                return text[tag.end : c.start()]
            i = c.end()
    return text[tag.end :]


def _has(attrs: str, name: str) -> bool:
    return re.search(rf"(?<![\w-]){re.escape(name)}\s*=", attrs) is not None


def _class_value(attrs: str) -> str:
    """Return the raw className value: quoted string or the full `{…}` expression (brace-balanced)."""
    m = re.search(r"className\s*=\s*", attrs)
    if not m:
        return ""
    i = m.end()
    if i >= len(attrs):
        return ""
    if attrs[i] in "\"'":
        j = attrs.find(attrs[i], i + 1)
        return attrs[i + 1 : j] if j > 0 else attrs[i + 1 :]
    if attrs[i] == "{":
        depth = 0
        for j in range(i, len(attrs)):
            if attrs[j] == "{":
                depth += 1
            elif attrs[j] == "}":
                depth -= 1
                if depth == 0:
                    return attrs[i : j + 1]
        return attrs[i:]
    return ""


def _ignores(text: str) -> dict[int, tuple[str, str, int]]:
    """line -> (rule, reason, comment_line): an ignore applies to its own line and the next line."""
    out: dict[int, tuple[str, str, int]] = {}
    for ln, raw in enumerate(text.splitlines(), start=1):
        m = IGNORE_RE.search(raw)
        if m:
            out[ln] = (m.group(1), m.group(2).strip(), ln)
    return out


def audit_text(text: str, file: str) -> list[Finding]:
    findings: list[Finding] = []
    ignores = _ignores(text)
    used: set[int] = set()

    def add(line: int, rule: str, detail: str = "", span_end: int | None = None) -> None:
        msg = RULES[rule] + (f" — {detail}" if detail else "")
        # An ignore applies from two lines above the tag through the tag's last line
        # (multi-line JSX attributes may carry the comment inside the tag).
        last = span_end if span_end and span_end >= line else line
        for cand in (line - 2, line - 1, *range(line, last + 1)):
            ig = ignores.get(cand)
            if ig and ig[0] == rule:
                used.add(cand)
                if not STEP_RE.search(ig[1]):
                    findings.append(Finding(file, cand, "invalid-ignore", f"reason lacks (S-xxx): {ig[1]!r}"))
                return
        findings.append(Finding(file, line, rule, msg))

    tags = extract_tags(text)
    label_spans: list[tuple[int, int]] = []
    for lm in re.finditer(r"<label\b", text):
        close = text.find("</label>", lm.end())
        label_spans.append((lm.start(), close if close >= 0 else len(text)))
    label_for = set(re.findall(r"htmlFor\s*=\s*[\"']([\w-]+)[\"']", text))

    for tag in tags:
        cls = _class_value(tag.attrs)
        if tag.name == "button":
            kids = _children(text, tag)
            visible_text = re.sub(r"\{[^{}]*\}", "", re.sub(r"<[^>]+>", "", kids)).strip()
            icon_only = bool(kids.strip()) and not visible_text and ICON_CHILD_RE.match(kids) is not None
            expr_only = bool(kids.strip()) and not visible_text and "<" not in kids
            if (
                (icon_only or (not kids.strip() and not tag.self_closing))
                and not any(_has(tag.attrs, a) for a in ("aria-label", "aria-labelledby", "title"))
                or (
                    expr_only
                    and not any(_has(tag.attrs, a) for a in ("aria-label", "aria-labelledby", "title"))
                    # {isPlaying ? <Pause/> : <Play/>} — icon expression without any text literal
                    and re.search(r"<[A-Z]\w*\b[^>]*/>", kids)
                    and not re.search(r"['\"][^'\"<>]*\w[^'\"<>]*['\"]\s*[:}]", kids)
                )
            ):
                add(tag.line, "icon-button-label", span_end=_line_of(text, tag.end))
        if tag.name in ("div", "span", "motion.div", "motion.span") and _has(tag.attrs, "onClick"):
            missing = [a for a in ("role", "tabIndex", "onKeyDown") if not _has(tag.attrs, a)]
            if missing:
                add(tag.line, "div-click", f"missing {', '.join(missing)}", span_end=_line_of(text, tag.end))
        if tag.name == "img":
            missing = [a for a in ("alt", "width", "height") if not _has(tag.attrs, a)]
            if missing:
                add(tag.line, "img-alt-dims", f"missing {', '.join(missing)}", span_end=_line_of(text, tag.end))
        if tag.name in ("input", "textarea", "select"):
            if re.search(r"type\s*=\s*[\"']hidden[\"']", tag.attrs):
                continue
            wrapped = any(s <= tag.start <= e for s, e in label_spans)
            idm = re.search(r"\bid\s*=\s*[\"']([\w-]+)[\"']", tag.attrs)
            labelled = (idm is not None and idm.group(1) in label_for) or any(
                _has(tag.attrs, a) for a in ("aria-label", "aria-labelledby")
            )
            if not (wrapped or labelled):
                add(tag.line, "input-label", span_end=_line_of(text, tag.end))
        if cls:
            if re.search(r"\boutline-none\b", cls) and "focus-visible:" not in cls:
                add(tag.line, "outline-none-focus", span_end=_line_of(text, tag.end))
            if re.search(r"\btransition-all\b", cls):
                add(tag.line, "transition-all", span_end=_line_of(text, tag.end))

    # Non-tag rules (line based)
    for ln, raw in enumerate(text.splitlines(), start=1):
        if re.search(r"transition\s*:\s*['\"]?all\b", raw):
            add(ln, "transition-all", "inline style / CSS")
        if LOCALE_NOARG_RE.search(raw) or DATE_PARTS_RE.search(raw):
            add(ln, "hardcoded-format")

    # Reduced motion: one finding per file, at the first animation.
    if not REDUCED_OK_RE.search(text):
        m = ANIMATION_RE.search(text)
        if m and not re.search(r"animate-spin", m.group(0)):
            add(_line_of(text, m.start()), "reduced-motion")
        elif m:
            # animate-spin is a loading indicator; still flag other animations if any exist
            others = [x for x in ANIMATION_RE.finditer(text) if "animate-spin" not in x.group(0)]
            if others:
                add(_line_of(text, others[0].start()), "reduced-motion")

    for ln, (rule, _reason, _cl) in ignores.items():
        if rule not in RULES:
            findings.append(Finding(file, ln, "invalid-ignore", f"unknown rule {rule!r}"))
        elif ln not in used:
            findings.append(Finding(file, ln, "unused-ignore", rule))
    findings.sort(key=lambda f: (f.line, f.rule))
    return findings


def iter_files(paths: list[str]) -> list[Path]:
    out: list[Path] = []
    for p in paths:
        path = Path(p)
        if path.is_dir():
            out += sorted(x for x in path.rglob("*.tsx") if "node_modules" not in x.parts and ".next" not in x.parts)
        elif path.suffix in (".tsx", ".jsx"):
            out.append(path)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="+")
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--strict", action="store_true", help="exit 1 on any finding")
    mode.add_argument("--warn", action="store_true", help="report only (default)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--rules", action="store_true", help="list rules and exit")
    args = ap.parse_args(argv)
    if args.rules:
        for k, v in RULES.items():
            print(f"{k:20} {v}")
        return 0
    root = Path.cwd()
    files = iter_files(args.paths)
    findings: list[Finding] = []
    for f in files:
        try:
            rel = str(f.resolve().relative_to(root)).replace("\\", "/")
        except ValueError:
            rel = str(f).replace("\\", "/")
        findings += audit_text(f.read_text(encoding="utf-8"), rel)
    if args.json:
        print(json.dumps({"files": len(files), "findings": [asdict(x) for x in findings]}, ensure_ascii=False))
    else:
        for x in findings:
            print(x.render())
        print(
            f"design_audit: {len(findings)} finding(s) in {len(files)} file(s) [{'strict' if args.strict else 'warn'}]"
        )
    return 1 if (args.strict and findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
