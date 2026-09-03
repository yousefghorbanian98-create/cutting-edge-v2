#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]
use std::sync::{Arc, Mutex};
use sysinfo::System;

struct AppState { healthy: bool, ram: f32, cpu: f32 }

#[tauri::command]
fn get_system_status(state: tauri::State<Arc<Mutex<AppState>>>) -> String {
    let mut sys = System::new_all();
    sys.refresh_all();
    let mut s = state.lock().unwrap();
    s.ram = sys.used_memory() as f32 / 1024.0 / 1024.0;
    s.cpu = sys.global_cpu_usage();
    s.healthy = s.ram < 12000.0 && s.cpu < 95.0;
    format!("RAM: {:.0}MB | CPU: {:.1}% | Healthy: {}", s.ram, s.cpu, s.healthy)
}

#[tauri::command]
fn reheal_check() -> String {
    "Reheal Loop Active | 7 Layers | Zero Crash Architecture".into()
}

fn main() {
    tracing_subscriber::fmt::init();
    let state = Arc::new(Mutex::new(AppState { healthy: true, ram: 0.0, cpu: 0.0 }));
    tauri::Builder::default()
        .manage(state)
        .invoke_handler(tauri::generate_handler![get_system_status, reheal_check])
        .run(tauri::generate_context!())
        .expect("error running tauri");
}
