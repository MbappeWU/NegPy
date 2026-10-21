import numpy as np
import pytest

from negpy.domain.models import WorkspaceConfig
from negpy.services.rendering import base_read


@pytest.fixture
def counted(monkeypatch):
    calls: list[int] = []
    monkeypatch.setattr(base_read, "measure_base_log", lambda image: calls.append(1) or (float(image.mean()), 0.0, 0.0))
    return calls


def _img(v: float) -> np.ndarray:
    return np.full((8, 8, 3), v, dtype=np.float32)


def test_base_log_for_measures_once_per_key(counted):
    first = base_read.base_log_for("a", _img(0.5))
    assert base_read.base_log_for("a", _img(0.9)) == first
    base_read.base_log_for("b", _img(0.5))
    assert len(counted) == 2


def test_base_log_for_evicts_the_oldest_past_its_capacity(counted):
    for i in range(base_read.CAPACITY + 1):
        base_read.base_log_for(i, _img(0.5))
    base_read.base_log_for(base_read.CAPACITY, _img(0.5))
    assert len(counted) == base_read.CAPACITY + 1
    base_read.base_log_for(0, _img(0.5))
    assert len(counted) == base_read.CAPACITY + 2


def test_a_source_with_no_base_is_cached_too(monkeypatch):
    calls: list[int] = []
    monkeypatch.setattr(base_read, "measure_base_log", lambda image: calls.append(1) or None)
    assert base_read.base_log_for("none", _img(0.5)) is None
    assert base_read.base_log_for("none", _img(0.5)) is None
    assert base_read.cached_base_log("none") is None
    assert calls == [1]


def test_a_lookup_never_measures(counted):
    assert base_read.cached_base_log("missing") is base_read.NOT_READ
    assert base_read.cached_base_log(None) is base_read.NOT_READ
    assert counted == []


def test_no_key_measures_without_caching(counted):
    base_read.base_log_for(None, _img(0.5))
    base_read.base_log_for(None, _img(0.5))
    assert len(counted) == 2


def test_a_prefetched_read_serves_the_render(counted):
    from negpy.services.rendering.image_processor import ImageProcessor, read_source_base

    img = np.random.default_rng(1).random((90, 60, 3), dtype=np.float32) * 0.5 + 0.2
    cfg = WorkspaceConfig()
    read_source_base(img, cfg, "frame")
    ImageProcessor(use_gpu=False).run_pipeline(img, cfg, "frame", render_size_ref=90, prefer_gpu=False, readback_metrics=True)
    assert counted == [1]


def test_a_render_without_readback_never_measures(counted):
    from negpy.services.rendering.image_processor import ImageProcessor

    img = np.random.default_rng(1).random((90, 60, 3), dtype=np.float32)
    ImageProcessor(use_gpu=False).run_pipeline(
        img, WorkspaceConfig(), "quiet", render_size_ref=90, prefer_gpu=False, readback_metrics=False
    )
    assert counted == []
