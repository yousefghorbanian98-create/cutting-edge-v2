"""S-010 — Tauri walking skeleton: everything that can be verified without cargo.

The compile/bundle/install half runs on the `ci / windows` job (cargo fmt/clippy/test,
`tauri build`, `scripts/ci/installer_smoke.ps1`). This file pins the static contract
so a broken manifest is caught locally, before a 30-minute Windows build.
"""

from __future__ import annotations

import json
import re
import struct
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
TAURI = ROOT / "apps" / "desktop" / "src-tauri"
sys.path.insert(0, str(ROOT / "scripts"))
import make_icons  # noqa: E402

# Keys of tauri-bundler/src/bundle/windows/nsis/languages/English.nsh (tauri-bundler 2.9.x).
ENGLISH_NSIS_KEYS = {
    "addOrReinstall", "alreadyInstalled", "alreadyInstalledLong", "appRunning", "appRunningOkKill",
    "chooseMaintenanceOption", "choowHowToInstall", "createDesktop", "dontUninstall",
    "dontUninstallDowngrade", "failedToKillApp", "installingWebview2", "newerVersionInstalled", "older",
    "olderOrUnknownVersionInstalled", "silentDowngrades", "unableToUninstall", "uninstallApp",
    "uninstallBeforeInstalling", "unknown", "webview2AbortError", "webview2DownloadError",
    "webview2DownloadSuccess", "webview2Downloading", "webview2InstallError", "webview2InstallSuccess",
    "deleteAppData",
}  # fmt: skip


def _conf() -> dict:
    return json.loads((TAURI / "tauri.conf.json").read_text(encoding="utf-8"))


def _cargo() -> dict:
    return tomllib.loads((TAURI / "Cargo.toml").read_text(encoding="utf-8"))


# ── AC-1: crate manifest is a compilable Tauri 2 app ──────────────────────────
def test_cargo_manifest_is_tauri2_shape() -> None:
    c = _cargo()
    assert c["package"]["name"] == "cutting-edge"
    assert c["package"]["edition"] == "2021"
    assert "tauri-build" in c["build-dependencies"], "build.rs needs tauri-build"
    tauri = c["dependencies"]["tauri"]
    assert tauri["version"].startswith("2")
    assert "shell-open" not in tauri.get("features", []), "Tauri 1 feature; v2 uses plugins (BUG-10)"
    assert c["lib"]["path"] == "src/lib.rs" and c["bin"][0]["path"] == "src/main.rs"
    assert (TAURI / "build.rs").read_text().strip().startswith("fn main()")
    assert "tauri_build::build()" in (TAURI / "build.rs").read_text()


def test_lib_exposes_the_two_commands_and_health_rule() -> None:
    src = (TAURI / "src" / "lib.rs").read_text(encoding="utf-8")
    assert "#[tauri::command]" in src
    assert re.search(r"fn system_status\(", src) and re.search(r"fn app_version\(", src)
    assert "generate_handler![system_status, app_version]" in src
    assert "generate_context!()" in src
    assert "#[cfg(test)]" in src and src.count("#[test]") >= 4
    main = (TAURI / "src" / "main.rs").read_text(encoding="utf-8")
    assert 'windows_subsystem = "windows"' in main and "cutting_edge_lib::run()" in main


# ── AC-2: tauri.conf.json — dev/build wiring, window, NSIS bundle ─────────────
def test_tauri_conf_wiring() -> None:
    conf = _conf()
    assert conf["identifier"] == "com.cuttingedge.app" and conf["identifier"] != "com.tauri.dev"
    assert conf["productName"] == "Cutting Edge"
    b = conf["build"]
    assert b["devUrl"] == "http://localhost:3000" and b["beforeDevCommand"] == "pnpm dev"
    assert b["beforeBuildCommand"] == "pnpm build" and b["frontendDist"] == "../out"
    win = conf["app"]["windows"][0]
    assert win["label"] == "main" and win["title"] == "Cutting Edge"
    assert win["minWidth"] >= 1024 and win["theme"] == "Dark"
    assert win["backgroundColor"] == "#09090b", "surface-0 from DESIGN.md (no white flash)"


def test_bundle_targets_nsis_per_user_with_persian() -> None:
    bundle = _conf()["bundle"]
    assert bundle["active"] is True and bundle["targets"] == ["nsis"]
    nsis = bundle["windows"]["nsis"]
    assert nsis["installMode"] == "currentUser", "no UAC (S-062 default)"
    # NSIS names the Persian locale "Farsi" (Farsi.nlf); Tauri's built-in "Persian" aborts makensis
    # (CI run 35707003767), so the Persian strings ship as a custom language file.
    assert nsis["languages"] == ["English", "Farsi"] and nsis["displayLanguageSelector"] is True
    farsi = TAURI / nsis["customLanguageFiles"]["Farsi"]
    assert farsi.exists()
    body = farsi.read_text(encoding="utf-8")
    keys = set(re.findall(r"^LangString (\w+) \$\{LANG_FARSI\}", body, re.M))
    assert keys == ENGLISH_NSIS_KEYS, sorted(keys ^ ENGLISH_NSIS_KEYS)
    assert "{{" not in body, "custom language files are not handlebars-rendered; use ${PRODUCTNAME}"
    lic = (TAURI / bundle["licenseFile"]).resolve()
    assert lic == ROOT / "LICENSE" and lic.exists()
    for rel in bundle["icon"]:
        assert (TAURI / rel).exists(), rel
    assert any(rel.endswith(".ico") for rel in bundle["icon"]), "Windows exe resource needs .ico"


def test_version_is_single_sourced_across_manifests() -> None:
    conf_v = _conf()["version"]
    cargo_v = _cargo()["package"]["version"]
    pkg_v = json.loads((ROOT / "apps" / "desktop" / "package.json").read_text())["version"]
    assert conf_v == cargo_v == pkg_v, (conf_v, cargo_v, pkg_v)


# ── AC-3: capabilities are minimal ───────────────────────────────────────────
def test_capabilities_minimal() -> None:
    caps = sorted((TAURI / "capabilities").glob("*.json"))
    assert [c.name for c in caps] == ["default.json"]
    cap = json.loads(caps[0].read_text(encoding="utf-8"))
    assert cap["identifier"] == "default" and cap["windows"] == ["main"]
    assert cap["permissions"] == ["core:default"], "S-059 adds dialog/opener/fs per feature"


# ── AC-4: icon set is deterministic and complete ──────────────────────────────
def test_icons_regenerate_identically(tmp_path: Path) -> None:
    out = tmp_path / "icons"
    assert make_icons.main(["--out", str(out)]) == 0
    for name in [*make_icons.PNG_SIZES, "icon.ico"]:
        assert (out / name).exists(), name
    assert make_icons.check(TAURI / "icons") == []


def test_icon_files_have_expected_dimensions_and_alpha() -> None:
    for name, size in make_icons.PNG_SIZES.items():
        w, h, rgba = make_icons.decode_png_rgba((TAURI / "icons" / name).read_bytes())
        assert (w, h) == (size, size), name
        corner_alpha = rgba[3]
        centre = (size // 2) * size + size // 2
        assert corner_alpha == 0, f"{name}: rounded corner must be transparent"
        assert rgba[centre * 4 + 3] == 255, f"{name}: centre must be opaque"
        assert rgba[centre * 4] > 200, f"{name}: star glyph should be near-white at centre"
    ico = (TAURI / "icons" / "icon.ico").read_bytes()
    _, kind, count = struct.unpack("<HHH", ico[:6])
    assert kind == 1 and count == len(make_icons.ICO_SIZES)
    sizes = sorted(w for w, _, _ in make_icons._ico_pixels(ico))
    assert sizes == sorted(make_icons.ICO_SIZES)


def test_make_icons_check_detects_drift(tmp_path: Path) -> None:
    out = tmp_path / "icons"
    make_icons.main(["--out", str(out)])
    blob = bytearray((out / "32x32.png").read_bytes())
    # flip one pixel of the 32px icon and re-encode through the same helper
    w, h, rgba = make_icons.decode_png_rgba(bytes(blob))
    rgba = bytearray(rgba)
    rgba[(16 * 32 + 16) * 4] ^= 0xFF
    (out / "32x32.png").write_bytes(make_icons.encode_png(32, bytes(rgba)))
    problems = make_icons.check(out)
    assert problems == ["32x32.png: pixels differ from generator output"]
    assert make_icons.main(["--out", str(out), "--check"]) == 1


# ── AC-5: CI installer smoke script is well-formed ───────────────────────────
def test_installer_smoke_script_covers_the_step_contract() -> None:
    ps = (ROOT / "scripts" / "ci" / "installer_smoke.ps1").read_text(encoding="utf-8")
    for check in [
        "installer-exists",
        "install-exit-0",
        "installed-exe",
        "uninstall-registry-key",
        "start-menu-shortcut",
        "window-title",
        "no-orphan-process",
        "uninstall-dir-removed",
        "uninstall-registry-removed",
        "uninstall-shortcut-removed",
    ]:
        assert f'"{check}"' in ps, check
    assert '"/S"' in ps and "MainWindowTitle" in ps
    assert "finally" in ps, "uninstall must run even when a check fails"
    assert "\r\n" not in ps


@pytest.mark.skipif(sys.platform != "win32", reason="pwsh parser check runs on the windows job")
def test_installer_smoke_script_parses_in_pwsh() -> None:
    script = ROOT / "scripts" / "ci" / "installer_smoke.ps1"
    cmd = (
        "$t=$null;$e=$null;[System.Management.Automation.Language.Parser]::ParseFile("
        f"'{script}',[ref]$t,[ref]$e)|Out-Null; if($e.Count){{$e|Out-String|Write-Error; exit 1}}"
    )
    proc = subprocess.run(["pwsh", "-NoProfile", "-Command", cmd], capture_output=True, text=True, check=False)
    assert proc.returncode == 0, proc.stderr
