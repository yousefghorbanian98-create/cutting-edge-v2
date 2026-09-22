//! Cutting Edge desktop shell (S-010 walking skeleton).
//!
//! The shell only hosts the Next.js static export and exposes two read-only
//! commands used by the Reheal status bar. Native dialogs, the opener and the
//! Python sidecar arrive in S-059/S-060; nothing here touches the file system.

use std::sync::{Mutex, PoisonError};

use serde::Serialize;
use sysinfo::System;
use tracing_subscriber::EnvFilter;

/// RAM headroom the Reheal layer wants to keep free (the AI stack alone can
/// need ~1.5 GB; see `docs/loop/07_HARDWARE_LIMITS.md`).
pub const RAM_HEALTHY_MAX_PERCENT: f32 = 85.0;
/// Above this the host is saturated and background jobs should be paused.
pub const CPU_HEALTHY_MAX_PERCENT: f32 = 95.0;

/// Snapshot of host resources, mirrored by the FastAPI `/health` payload so the
/// UI can fall back to the shell while the sidecar is (re)starting.
#[derive(Debug, Clone, Copy, PartialEq, Serialize)]
pub struct SystemStatus {
    pub ram_used_mb: u64,
    pub ram_total_mb: u64,
    pub ram_percent: f32,
    pub cpu_percent: f32,
    pub healthy: bool,
}

/// Pure health rule so it can be unit-tested without a live `System`.
pub fn is_healthy(ram_percent: f32, cpu_percent: f32) -> bool {
    ram_percent.is_finite()
        && cpu_percent.is_finite()
        && ram_percent < RAM_HEALTHY_MAX_PERCENT
        && cpu_percent < CPU_HEALTHY_MAX_PERCENT
}

/// Builds a status from raw numbers (bytes / percent). Shared by the command
/// and the tests; never panics on a zero total.
pub fn status_from(used_bytes: u64, total_bytes: u64, cpu_percent: f32) -> SystemStatus {
    const MIB: u64 = 1024 * 1024;
    let ram_percent = if total_bytes == 0 {
        0.0
    } else {
        (used_bytes as f64 / total_bytes as f64 * 100.0) as f32
    };
    SystemStatus {
        ram_used_mb: used_bytes / MIB,
        ram_total_mb: total_bytes / MIB,
        ram_percent,
        cpu_percent,
        healthy: is_healthy(ram_percent, cpu_percent),
    }
}

/// Managed state: one `System` reused across polls (a fresh `System::new_all()`
/// per call costs ~100 ms and the first CPU sample is always 0 %).
pub struct Monitor {
    sys: Mutex<System>,
}

impl Default for Monitor {
    fn default() -> Self {
        let mut sys = System::new();
        sys.refresh_memory();
        sys.refresh_cpu_usage();
        Self { sys: Mutex::new(sys) }
    }
}

#[tauri::command]
fn system_status(monitor: tauri::State<'_, Monitor>) -> SystemStatus {
    let mut sys = monitor.sys.lock().unwrap_or_else(PoisonError::into_inner);
    sys.refresh_memory();
    sys.refresh_cpu_usage();
    status_from(sys.used_memory(), sys.total_memory(), sys.global_cpu_usage())
}

#[tauri::command]
fn app_version() -> &'static str {
    env!("CARGO_PKG_VERSION")
}

pub fn run() {
    let filter = EnvFilter::try_from_default_env().unwrap_or_else(|_| EnvFilter::new("info"));
    tracing_subscriber::fmt().with_env_filter(filter).init();

    tauri::Builder::default()
        .manage(Monitor::default())
        .invoke_handler(tauri::generate_handler![system_status, app_version])
        .run(tauri::generate_context!())
        .expect("error while running the Cutting Edge shell");
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn healthy_inside_both_limits() {
        assert!(is_healthy(40.0, 20.0));
        assert!(is_healthy(84.9, 94.9));
    }

    #[test]
    fn unhealthy_when_ram_or_cpu_saturated() {
        assert!(!is_healthy(85.0, 10.0));
        assert!(!is_healthy(10.0, 95.0));
        assert!(!is_healthy(f32::NAN, 10.0));
    }

    #[test]
    fn status_from_converts_bytes_and_guards_zero_total() {
        let s = status_from(3 * 1024 * 1024 * 1024, 16 * 1024 * 1024 * 1024, 12.5);
        assert_eq!((s.ram_used_mb, s.ram_total_mb), (3072, 16384));
        assert!((s.ram_percent - 18.75).abs() < 0.01);
        assert!(s.healthy);

        let z = status_from(0, 0, 0.0);
        assert!(z.ram_percent.abs() < f32::EPSILON);
        assert!(z.healthy);
    }

    #[test]
    fn status_serialises_to_the_health_shape() {
        let json = serde_json::to_value(status_from(1, 2, 3.0)).unwrap();
        for key in ["ram_used_mb", "ram_total_mb", "ram_percent", "cpu_percent", "healthy"] {
            assert!(json.get(key).is_some(), "missing {key}");
        }
    }

    #[test]
    fn version_matches_cargo_manifest() {
        assert_eq!(app_version(), env!("CARGO_PKG_VERSION"));
    }
}
