from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import MagicMock

import numpy as np
import pytest
from PIL import Image
from PyQt6.QtCore import QRect, Qt
from PyQt6.QtGui import QColor, QIcon, QImage, QPainter, QPixmap, QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QListView, QStackedWidget, QStyle, QStyleOptionViewItem, QToolButton, QWidget

from negpy.desktop.session import DesktopSessionManager
from negpy.desktop.view.keyboard_shortcuts import _context_cancel
from negpy.desktop.view.main_window import MainWindow
from negpy.desktop.view.sidebar.files import LIGHT_TABLE_WHITE, FileBrowser, _FilmDelegate, print_dmax, roll_film, picture_in_thumbnail
from negpy.desktop.view.styles.theme import THEME
from negpy.domain.models import WorkspaceConfig
from negpy.features.geometry.models import GeometryConfig
from negpy.features.metadata.gear_models import FilmStock, GearLibrary
from negpy.infrastructure.storage.repository import StorageRepository
from negpy.kernel.image.logic import prepare_thumbnail
from negpy.services.assets.gear import GearProfiles
from negpy.services.film_edge.geometry import PERF_ACROSS, PERF_FROM_EDGE, SheetFormat, perforation_centers


class _Dock:
    def __init__(self, visible=True, floating=False):
        self.visible = visible
        self.floating = floating

    def isVisible(self):
        return self.visible

    def isFloating(self):
        return self.floating

    def setVisible(self, visible):
        self.visible = visible


def _window():
    stack = QStackedWidget()
    stack.addWidget(QWidget())
    grid = QListView()
    stack.addWidget(grid)
    button = QToolButton()
    button.setCheckable(True)
    win = SimpleNamespace(
        central_stack=stack,
        drawer=_Dock(),
        toolbar=SimpleNamespace(btn_light_table=button),
        file_browser=SimpleNamespace(light_table_view=grid),
        strip_open=True,
        _strip_open_before_light_table=True,
        controller=MagicMock(),
        state=SimpleNamespace(selected_file_idx=0),
    )
    win.film_strip_expanded = lambda: win.strip_open
    win.set_film_strip_expanded = lambda on, persist=True: setattr(win, "strip_open", on)
    win.controller.session.asset_model.actual_to_display.return_value = -1
    win.light_table_active = lambda: MainWindow.light_table_active(win)
    return win


def test_the_light_table_takes_the_canvas_and_strip_place_and_gives_it_back(qapp):
    win = _window()

    MainWindow.set_light_table(win, True)
    assert win.central_stack.currentIndex() == 1
    assert win.toolbar.btn_light_table.isChecked()
    assert not win.strip_open, "the strip folds under the grid; the toolbar stays"
    assert win.drawer.visible, "an open controls panel stays open"

    MainWindow.set_light_table(win, False)
    assert win.central_stack.currentIndex() == 0
    assert not win.toolbar.btn_light_table.isChecked()
    assert win.strip_open and win.drawer.visible


def test_leaving_the_light_table_keeps_a_folded_strip_folded(qapp):
    win = _window()
    win.strip_open = False

    MainWindow.set_light_table(win, True)
    MainWindow.set_light_table(win, False)

    assert not win.strip_open


def test_the_light_table_will_not_open_on_an_empty_grid(qapp):
    win = _window()
    win.controller.session.asset_model.rowCount.return_value = 0
    win.state.uploaded_files = [{"name": "a.tif"}]
    win.toolbar.btn_light_table.setChecked(True)

    MainWindow.set_light_table(win, True)

    assert win.central_stack.currentIndex() == 0
    assert win.strip_open
    assert not win.toolbar.btn_light_table.isChecked()
    win.controller.set_status.assert_called_once_with("No frames match the filter", 3000)


def test_the_light_table_closes_when_its_grid_empties(qapp):
    win = _window()
    MainWindow.set_light_table(win, True)
    win.set_light_table = lambda on: MainWindow.set_light_table(win, on)
    win.controller.session.asset_model.rowCount.return_value = 0
    win.state.uploaded_files = [{"name": "a.tif"}]

    MainWindow._leave_empty_light_table(win)

    assert win.central_stack.currentIndex() == 0
    assert win.strip_open


def test_the_light_table_leaves_a_hidden_controls_panel_hidden(qapp):
    win = _window()
    win.drawer.visible = False

    MainWindow.set_light_table(win, True)
    MainWindow.set_light_table(win, False)

    assert not win.drawer.visible


def test_escape_closes_the_light_table_before_anything_else(qapp):
    win = _window()
    MainWindow.set_light_table(win, True)
    win.set_light_table = lambda on: MainWindow.set_light_table(win, on)
    controller = MagicMock()

    _context_cancel(controller, win)

    assert not win.light_table_active()
    controller.cancel_active_tool.assert_not_called()


def test_one_key_hides_the_panel_and_collapses_the_strip_then_brings_both_back(qapp):
    win = _window()
    expanded = [True]
    win.film_strip_expanded = lambda: expanded[0]
    win.set_film_strip_expanded = lambda on: expanded.__setitem__(0, on)

    MainWindow.toggle_side_panels(win)
    assert not win.drawer.visible and not expanded[0]
    MainWindow.toggle_side_panels(win)
    assert win.drawer.visible and expanded[0]
    win.controller.session.repo.save_global_setting.assert_called_with("panel_right_visible", True)


@pytest.fixture
def browser(qapp):
    repo = MagicMock(spec=StorageRepository)
    repo.get_global_setting.return_value = None
    repo.load_file_settings.return_value = None
    repo.load_file_settings_by_path.return_value = None
    repo.load_file_settings_many.return_value = {}
    repo.get_max_history_index.return_value = 0
    session = DesktopSessionManager(repo)
    session.state.uploaded_files = [{"name": f"{i}.tif", "path": f"/r/{i}.tif", "hash": f"h{i}"} for i in range(3)]
    session.asset_model.refresh()
    controller = MagicMock()
    controller.session = session
    controller.thumbnail_refresh_running = False
    return FileBrowser(controller)


def test_the_strip_and_the_light_table_take_the_chosen_surface(browser):
    from negpy.desktop.view.canvas.toolbar import CANVAS_COLORS

    black = CANVAS_COLORS[0][0]
    browser.session.set_light_table_bg(0)

    for view in (browser.list_view, browser.light_table_view):
        assert f"background-color: {black}" in view.styleSheet()
    assert browser._light_table_delegate._film[2].no_film == QColor(black).getRgb()[:3]
    browser.session.repo.save_global_setting.assert_any_call("light_table_bg_index", 0)


def test_the_light_table_shares_the_strip_selection(browser):
    assert browser.light_table_view.model() is browser.list_view.model()
    assert browser.light_table_view.selectionModel() is browser.list_view.selectionModel()


def test_opening_a_frame_from_the_light_table_asks_for_the_canvas(browser, monkeypatch):
    opened, left = [], []
    monkeypatch.setattr(browser, "_activate_file", opened.append)
    browser.light_table_opened.connect(lambda: left.append(True))
    index = browser.light_table_view.model().index(1, 0)

    browser._open_from_light_table(index)

    assert opened == [index] and left == [True]


def _qimage(img: Image.Image) -> QImage:
    arr = np.ascontiguousarray(np.asarray(img.convert("RGB")))
    return QImage(arr.data, arr.shape[1], arr.shape[0], arr.strides[0], QImage.Format.Format_RGB888).copy()


@pytest.mark.parametrize("size", [(300, 200), (200, 300)])
def test_a_padded_thumbnail_gives_back_its_picture(qapp, size):
    thumb = prepare_thumbnail(Image.new("RGB", size, (200, 120, 40)), 120)

    rect = picture_in_thumbnail(_qimage(thumb))

    assert (rect.width(), rect.height()) == ((120, 80) if size[0] > size[1] else (80, 120))


def _print(black: tuple[int, int, int]) -> Image.Image:
    """A pale print with one patch at its D-max."""
    img = Image.new("RGB", (300, 200), (230, 225, 215))
    img.paste(black, (0, 0, 60, 40))
    return img


def test_a_prints_dmax_is_its_darkest_tone_not_the_thumbnail_padding(qapp):
    tone = print_dmax(_qimage(prepare_thumbnail(_print((30, 22, 12)), 120)))

    assert tone == pytest.approx((30, 22, 12), abs=3)


def test_the_rebate_takes_the_rolls_mean_print_dmax(browser):
    from negpy.services.assets.thumbnails import asset_thumbnail_key

    state = browser.session.state
    for info, black in zip(state.uploaded_files, ((30, 20, 10), (50, 40, 30), (40, 30, 20)), strict=True):
        state.thumbnails[asset_thumbnail_key(info)] = QIcon(QPixmap.fromImage(_qimage(prepare_thumbnail(_print(black), 120))))
    browser.controller.load_gear_library.return_value = _hp5()[1]

    browser._measure_rebate()

    assert browser._rebate_tone == pytest.approx((40, 30, 20), abs=3)
    palette = browser._light_table_delegate._film[2]
    assert palette.rebate == browser._rebate_tone
    assert palette.rim == tuple(c + 5 for c in browser._rebate_tone)


def _hp5(**meta) -> tuple[WorkspaceConfig, GearLibrary]:
    config = WorkspaceConfig()
    config = replace(config, metadata=replace(config.metadata, film_stock_id="film-hp5-400", **meta))
    return config, GearLibrary(film_stocks=GearProfiles._read_bundled_list("film_stocks.json", FilmStock))


def test_the_roll_film_is_the_rolls_stock_on_white(qapp):
    config, library = _hp5()

    geometry, style, palette = roll_film({}, config, library, half_frame=False)

    assert geometry.format == SheetFormat.FULL_FRAME
    assert (style.maker, style.text) == ("ILFORD", "HP5 PLUS")
    assert palette.no_film == QColor(LIGHT_TABLE_WHITE).getRgb()[:3]
    assert roll_film({}, config, library, half_frame=True)[0].format == SheetFormat.HALF_FRAME
    assert roll_film({}, _hp5(format="120")[0], library, half_frame=False)[0].format == SheetFormat.MEDIUM


def test_the_gear_library_is_read_again_only_when_the_film_changes(browser):
    loads = browser.controller.load_gear_library
    loads.reset_mock()
    loads.return_value = _hp5()[1]
    browser._film_key = None

    browser.sync_ui()
    browser.sync_ui()
    assert loads.call_count == 1

    state = browser.session.state
    state.config = replace(state.config, metadata=replace(state.config.metadata, film_stock_id="film-hp5-400"))
    browser.sync_ui()
    assert loads.call_count == 2


def test_a_light_table_cell_is_one_frame_of_film(browser):
    view, delegate = browser.light_table_view, browser._light_table_delegate
    browser._film_key = None
    browser.sync_ui()
    view.resize(900, 600)
    view._relayout()
    cell = view.gridSize()
    s = cell.width() / 38.0
    assert cell.height() == round(35.0 * s) + view.STRIP_GAP

    canvas = QImage(cell.width(), cell.height(), QImage.Format.Format_RGB888)
    canvas.fill(QColor(LIGHT_TABLE_WHITE))
    option = QStyleOptionViewItem()
    option.rect = QRect(0, 0, cell.width(), cell.height())
    painter = QPainter(canvas)
    delegate.paint(painter, option, view.model().index(0, 0))
    painter.end()

    top = (cell.height() - round(35.0 * s)) // 2
    hole = canvas.pixelColor(round(perforation_centers(0.0, 38.0)[0] * s), top + round((PERF_FROM_EDGE + PERF_ACROSS / 2) * s))
    rebate = canvas.pixelColor(cell.width() // 2, top + round(4.5 * s))
    assert hole == QColor(LIGHT_TABLE_WHITE)
    assert max(rebate.red(), rebate.green(), rebate.blue()) < 40


@pytest.mark.parametrize(("rotation", "top_lies_left"), [(0, False), (3, True)])
def test_a_portrait_frame_lies_on_the_strip_as_on_the_film(qapp, rotation, top_lies_left):
    upright = Image.new("RGB", (200, 300), (0, 0, 200))
    upright.paste((220, 0, 0), (0, 0, 200, 150))
    icon = QIcon(QPixmap.fromImage(_qimage(prepare_thumbnail(upright, 120))))
    delegate = _FilmDelegate(frame_geometry=lambda asset: GeometryConfig(rotation=rotation))
    delegate.set_film(*roll_film({}, *_hp5(), half_frame=False))
    model = QStandardItemModel()
    model.appendRow(QStandardItem())

    picture = delegate._thumbnail(icon, model.index(0, 0)).toImage()

    assert picture.width() > picture.height()
    assert (picture.pixelColor(5, picture.height() // 2).red() > 150) == top_lies_left


@pytest.mark.parametrize("hover", [False, True])
def test_a_light_table_frame_is_never_dimmed_and_hover_rings_it_red(qapp, hover):
    delegate = _FilmDelegate()
    delegate.set_film(*roll_film({}, *_hp5(), half_frame=False))
    model = QStandardItemModel()
    item = QStandardItem()
    item.setData(
        QIcon(QPixmap.fromImage(_qimage(prepare_thumbnail(Image.new("RGB", (300, 200), (40, 160, 220)), 120)))),
        Qt.ItemDataRole.DecorationRole,
    )
    model.appendRow(item)
    canvas = QImage(380, 350, QImage.Format.Format_RGB888)
    canvas.fill(QColor(LIGHT_TABLE_WHITE))
    option = QStyleOptionViewItem()
    option.rect = QRect(0, 0, 380, 350)
    if hover:
        option.state |= QStyle.StateFlag.State_MouseOver
    painter = QPainter(canvas)
    delegate.paint(painter, option, model.index(0, 0))
    painter.end()

    _top, window = delegate._layout(delegate._film[0], option.rect)
    assert canvas.pixelColor(window.center()) == QColor(40, 160, 220)
    ring = canvas.pixelColor(window.center().x(), window.top() - delegate._SELECTION_OUTSET + 1)
    assert (ring == QColor(THEME.accent_primary)) == hover
