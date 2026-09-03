"""Integration tests for Cutting Edge Pipeline"""
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "ai-engine" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import pytest, cv2, numpy as np, tempfile, os

@pytest.fixture
def sample_video():
    p = tempfile.mktemp(suffix=".mp4")
    out = cv2.VideoWriter(p, cv2.VideoWriter_fourcc(*"mp4v"), 30, (320, 240))
    for _ in range(90): out.write(np.random.randint(0,255,(240,320,3),dtype=np.uint8))
    out.release(); yield p; os.unlink(p)

def test_video_validation(sample_video):
    from reheal.pipeline_validator import PipelineValidator
    r = PipelineValidator().validate_input(sample_video)
    assert r.valid

def test_muscle_enhancer(sample_video):
    from muscle.muscle_enhancer import MuscleEnhancer
    e = MuscleEnhancer()
    cap = cv2.VideoCapture(sample_video); ret, f = cap.read(); cap.release()
    if ret:
        out = e.enhance_frame(f)
        assert out.shape == f.shape
        assert not np.array_equal(out, f)

def test_health_monitor():
    from reheal.health_monitor import HealthMonitor
    h = HealthMonitor().check_health()
    assert 0 <= h.ram_percent <= 100

def test_crash_recovery():
    from reheal.crash_recovery import CrashRecovery
    r = CrashRecovery(tempfile.mkdtemp())
    r.save({"stage":"test","progress":50})
    s = r.load()
    assert s and s["progress"] == 50
