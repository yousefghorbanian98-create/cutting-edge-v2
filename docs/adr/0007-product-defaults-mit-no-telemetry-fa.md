# ADR-0007 — Product defaults: MIT licence, "Cutting Edge", Persian-first RTL UI, no telemetry

## Status
Accepted — 2026-09-04

## Context
Several open questions in the roadmap (licence, product name, default language, telemetry, output formats) block cards but the user asked for minimum involvement. The loop's U3 rule lets the builder pick a documented default and record it in `docs/DECISIONS.md`, reversible by the user later.

## Decision
- Licence **MIT** (`LICENSE`, "Cutting Edge v2 contributors").
- Product name **"Cutting Edge"**, identifier `com.cuttingedge.app`; icon to be produced in S-063 from the design tokens.
- Default UI language **Persian (fa, RTL)** with English as second locale; `<html lang="fa" dir="rtl">`, logical CSS properties.
- **No telemetry, no crash upload, no analytics** by default; Reheal events stay on the user's disk.
- Default export **MP4 H.264 + AAC**; H.265/WebM/GIF optional later.

## Consequences
- Positive: every card can proceed; users see a coherent Persian product; privacy by default matches the offline-first design.
- Negative: any later change by the user (name, icon, licence) is a rename job across installer/metadata — kept cheap by centralising in `tauri.conf.json`, `package.json`, `DECISIONS.md`.
- Follow-ups: `docs/DECISIONS.md` rows S-050/S-063/S-085/S-089/S-091 flip from "pending" to the chosen value as those cards land; supervise C15 blocks telemetry libraries.
