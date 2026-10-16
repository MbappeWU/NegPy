"""Language selection, format fallback and Chinese UI configuration boundaries."""

import json
import os
from collections.abc import Iterator
from pathlib import Path
import subprocess
import sys

import pytest

from negpy.kernel.system import i18n
from negpy.kernel.system.text import count_of
from scripts.extract_translations import CATALOG, ENGLISH_GUIDE, ROOT, extract


@pytest.fixture
def chinese() -> Iterator[None]:
    previous = i18n.language()
    i18n.configure("zh_CN")
    yield
    i18n.configure(previous)


@pytest.mark.parametrize(
    "choice,system,expected",
    [
        ("en", ["zh-CN"], "en"),
        ("zh_CN", ["en-US"], "zh_CN"),
        ("system", ["zh-Hans-CN"], "zh_CN"),
        ("system", ["en-US"], "en"),
        ("system", ["fr-FR"], "en"),
        ("system", ["zh-Hant-TW"], "en"),
        ("system", [], "en"),
        ("invalid", ["zh-CN"], "en"),
    ],
)
def test_language_resolution(choice: str, system: list[str], expected: str) -> None:
    assert i18n.resolve_language(choice, system) == expected


def test_catalog_covers_every_marked_message_and_preserves_formats() -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    assert catalog.keys() == extract().keys()
    for source, translated in catalog.items():
        assert translated, source
        assert i18n.fields(source) == i18n.fields(translated), source
    assert ENGLISH_GUIDE.read_bytes() == (ROOT / "docs" / "USER_GUIDE.md").read_bytes()


def test_templates_do_not_translate_or_reformat_user_data(chinese: None) -> None:
    name = "Print {filename} 中文.raw"
    assert i18n.tr("Export failed for {full_name}: {e}", full_name=name, e="{raw error}") == f"导出 {name} 失败：{{raw error}}"
    assert i18n.tr("{source}", source=name) == name
    assert i18n.tr("Missing source {name}", name=name) == f"Missing source {name}"
    assert count_of(1, "frame") == "1 帧"
    assert count_of(2, "frame") == "2 帧"


def test_format_signature_keeps_repeated_fields_and_conversions() -> None:
    assert i18n.fields("{name!r} {name}") == i18n.fields("{name} {name!r}")
    assert i18n.fields("{x:.1f}") != i18n.fields("{x:.2f}")
    assert i18n.fields("{x} {x}") != i18n.fields("{x}")


def test_bad_catalog_entries_fall_back_without_discarding_valid_entries(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    catalog = tmp_path / "catalog.json"
    catalog.write_text(json.dumps({"Good": "正确", "Bad {name}": "缺少参数", "Broken": "{broken", "Last": "最后"}), encoding="utf-8")
    with monkeypatch.context() as patch:
        patch.setattr(i18n, "get_resource_path", lambda _: str(catalog))
        try:
            i18n.configure("zh_CN")
            assert i18n.tr("Good") == "正确"
            assert i18n.tr("Bad {name}", name="test") == "Bad test"
            assert i18n.tr("Broken") == "Broken"
            assert i18n.tr("Last") == "最后"
        finally:
            i18n.configure("en")


def test_missing_catalog_keeps_the_application_usable(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(i18n, "get_resource_path", lambda _: str(tmp_path / "missing.json"))
    try:
        i18n.configure("zh_CN")
        assert i18n.tr("Preferences") == "Preferences"
    finally:
        i18n.configure("en")


def test_language_preference_is_saved_and_waits_for_restart() -> None:
    from negpy.desktop.view.widgets.preferences_dialog import PreferencesDialog
    from tests.conftest import FakeController, FakeRepo

    repo = FakeRepo()
    dialog = PreferencesDialog(FakeController(repo), None, pinned_keys=set())
    dialog.language_combo.setCurrentIndex(dialog.language_combo.findData("zh_CN"))
    assert repo.data["ui_language"] == "zh_CN"
    assert not dialog._restart_hint.isHidden()
    assert i18n.language() == "en"
    reopened = PreferencesDialog(FakeController(repo), None, pinned_keys=set())
    assert reopened.language_combo.currentData() == "zh_CN"


def test_localized_guides_cover_every_panel_and_fall_back(chinese: None) -> None:
    from negpy.desktop.view.widgets.section_help_dialog import _localized_guides, _read_guides, guide_markdown

    english = _localized_guides("en")
    translated = _read_guides("negpy/translations/USER_GUIDE.zh_CN.md")
    assert translated.keys() == english.keys()
    assert "密度" in guide_markdown("tone")
    assert _localized_guides("missing") == english
    assert _read_guides("negpy/translations/USER_GUIDE.en.md") == english


def test_chinese_command_search_keeps_english_aliases(chinese: None) -> None:
    from negpy.desktop.view.widgets.command_palette import make_entry, rank

    entry = make_entry("slider", i18n.tr("ISO-R Grade"), i18n.tr("Tone"), object())
    assert rank([entry], "对比度") == [entry]
    assert rank([entry], "contrast") == [entry]
    assert rank([entry], "反差") == [entry]


def test_fresh_chinese_ui_keeps_enum_and_metadata_keys(tmp_path: Path) -> None:
    # Module constants use the startup language; a fresh process tests the import order.
    result = subprocess.run(
        [sys.executable, "-c", _CHINESE_UI],
        cwd=CATALOG.parents[2],
        env={**os.environ, "NEGPY_USER_DIR": str(tmp_path), "QT_QPA_PLATFORM": "offscreen"},
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr


_CHINESE_UI = """
from dataclasses import replace
from negpy.kernel.system.i18n import configure, install_qt_translations, tr
configure('zh_CN')
from PyQt6.QtWidgets import QApplication, QDialogButtonBox
app = QApplication([])
install_qt_translations(app)
from negpy.desktop.view.widgets.preferences_dialog import PreferencesDialog
from negpy.desktop.view.widgets.roll_settings_dialog import RollSettingsDialog
from negpy.desktop.view.widgets.export_settings_form import ExportSettingsForm
from negpy.desktop.view.shortcut_registry import REGISTRY
from negpy.desktop.settings_catalog import NON_METADATA_SECTIONS
from negpy.domain.models import WorkspaceConfig
from negpy.features.metadata.gear_models import GearLibrary
from tests.conftest import FakeController, FakeRepo
prefs = PreferencesDialog(FakeController(FakeRepo(ui_language='zh_CN')), None, pinned_keys=set())
assert prefs.windowTitle() == '偏好设置'
assert prefs.language_combo.currentData() == 'zh_CN'
assert REGISTRY['open_preferences'].default_key == 'Ctrl+,'
assert REGISTRY['prev_file'].description == '上一个文件'
assert 'Metadata' not in NON_METADATA_SECTIONS
roll = RollSettingsDialog(None, WorkspaceConfig(), GearLibrary(), sel_count=1, roll_count=2)
roll.developer_edit.textEdited.emit('D-76')
assert roll._checks['Process'].isChecked()
roll.format_combo.setCurrentIndex(roll.format_combo.findData('Other'))
assert roll.format_combo.currentText() == '其他'
assert roll._meta.format == 'Other'
assert not roll.format_other_edit.isHidden()
assert roll.push_pull_combo.itemText(0) == '增感 +3'
form = ExportSettingsForm()
form.set_source_space('Adobe RGB')
assert form.ratio_combo.currentData() == 'Original'
assert form.ratio_combo.currentText() == '原始'
assert form.values()['paper_aspect_ratio'] == 'Original'
from negpy.desktop.view.sidebar.controls_panel import ControlsPanel
controller = FakeController(FakeRepo())
panel = ControlsPanel(controller)
controller.state.config = replace(controller.state.config, geometry=replace(controller.state.config.geometry, autocrop_ratio='6:7'))
panel.geometry_sidebar.sync_ui()
panel.autocrop_sidebar.sync_ui()
assert panel.geometry_sidebar.ratio_combo.currentData() == '6:7'
assert panel.autocrop_sidebar.ratio_combo.currentData() == '6:7'
buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
assert 'Cancel' not in buttons.button(QDialogButtonBox.StandardButton.Cancel).text()
"""
