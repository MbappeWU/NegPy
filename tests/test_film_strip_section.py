from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton, QSplitter, QWidget

from negpy.desktop.view.main_window import MainWindow


@pytest.fixture
def win(qapp):
    splitter = QSplitter(Qt.Orientation.Vertical)
    strip = QWidget()
    header = QPushButton()
    header.setCheckable(True)
    header.setChecked(True)
    header.setFixedHeight(30)
    strip.frames_section = SimpleNamespace(toggle_button=header, set_expanded=header.setChecked)
    splitter.addWidget(QWidget())
    splitter.addWidget(strip)
    splitter.resize(400, 800)
    splitter.show()
    splitter.setSizes([500, 300])
    qapp.processEvents()
    yield SimpleNamespace(file_browser=strip, strip_splitter=splitter, _strip_open_height=300, controller=MagicMock())
    splitter.hide()


def test_a_collapsed_strip_is_its_header_and_the_canvas_takes_the_rest(win, qapp):
    before = win.strip_splitter.sizes()
    total = sum(before)

    MainWindow._apply_strip_constraints(win, False)
    qapp.processEvents()
    assert win.strip_splitter.sizes() == [total - 30, 30]

    MainWindow._apply_strip_constraints(win, True)
    qapp.processEvents()
    assert win.strip_splitter.sizes() == before


def test_only_an_open_strip_saves_its_height(win):
    save = win.controller.session.repo.save_global_setting
    win.file_browser.frames_section.toggle_button.setChecked(False)
    MainWindow._on_strip_splitter_moved(win)
    save.assert_not_called()

    win.file_browser.frames_section.toggle_button.setChecked(True)
    MainWindow._on_strip_splitter_moved(win)
    save.assert_called_once_with("film_strip_splitter_sizes", win.strip_splitter.sizes())


def test_the_strip_toggle_shows_a_hidden_strip_then_collapses_it(win):
    header = win.file_browser.frames_section.toggle_button
    win.file_browser.setVisible(False)
    header.setChecked(False)

    MainWindow.toggle_film_strip(win)
    assert win.file_browser.isVisible() and header.isChecked()
    win.controller.session.repo.save_global_setting.assert_called_once_with("film_strip_visible", True)

    MainWindow.toggle_film_strip(win)
    assert not header.isChecked()
