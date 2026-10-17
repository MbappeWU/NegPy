import numpy as np

from negpy.features.exposure import print_lut
from negpy.features.exposure.print_lut import load_print_lut, save_print_lut, tetra_lookup


def _linear_table(n=5):
    g = np.linspace(0.0, 1.0, n, dtype=np.float32)
    c, m, y = np.meshgrid(g, g, g, indexing="ij")
    return np.ascontiguousarray(np.stack([0.2 + 0.5 * c, 0.1 + 0.3 * m + 0.2 * c, 0.9 - 0.4 * y], -1).astype(np.float32))


def test_tetra_exact_at_nodes():
    t, e_max = _linear_table(), np.ones(3, np.float32)
    for idx in [(0, 0, 0), (4, 4, 4), (1, 3, 2)]:
        np.testing.assert_allclose(tetra_lookup(t, e_max, *(np.array(idx) / 4)), t[idx], atol=1e-6)


def test_tetra_exact_for_linear_function():
    t, e_max = _linear_table(), np.full(3, 2.0, np.float32)
    for e in np.random.default_rng(0).uniform(0, 2, (200, 3)):
        u = e / 2
        expected = (0.2 + 0.5 * u[0], 0.1 + 0.3 * u[1] + 0.2 * u[0], 0.9 - 0.4 * u[2])
        np.testing.assert_allclose(tetra_lookup(t, e_max, *e), expected, atol=1e-5)


def test_tetra_clamps_outside_range():
    t, e_max = _linear_table(), np.ones(3, np.float32)
    np.testing.assert_allclose(tetra_lookup(t, e_max, -0.5, 9.0, 0.3), tetra_lookup(t, e_max, 0.0, 1.0, 0.3))


def test_save_load_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(print_lut, "LUT_DIR", tmp_path)
    load_print_lut.cache_clear()
    save_print_lut(tmp_path / "t.npz", _linear_table(), np.ones(3, np.float32), "test")
    lut = load_print_lut("t")
    load_print_lut.cache_clear()
    assert lut.source == "test" and lut.table.flags.c_contiguous
    np.testing.assert_array_equal(lut.table, _linear_table())
