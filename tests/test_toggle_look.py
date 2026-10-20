from PyQt6.QtCore import QPoint, QRect
from PyQt6.QtGui import QColor, QImage, QPainter
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QHBoxLayout, QMenu, QStyle, QStyleOptionViewItem, QWidget

from negpy.desktop.view.styles.templates import labeled_action, load_stylesheet, tool_toggle
from negpy.desktop.view.styles.theme import THEME
from negpy.desktop.view.widgets.choice_button import ToggleMenuButton
from negpy.desktop.view.widgets.collapsible import CollapsibleSection
from negpy.desktop.view.widgets.flat_rows import paint_fill
from negpy.desktop.view.widgets.step_combo import StepCombo


def _fill_at_rest_and_under_mouse(qapp, button) -> tuple[str, str]:
    host = QWidget()
    host.setStyleSheet(load_stylesheet())
    QHBoxLayout(host).addWidget(button)
    host.resize(240, 60)
    host.show()
    QTest.qWaitForWindowExposed(host)
    fills = []
    for target, pos in ((host, host.rect().bottomRight()), (button, button.rect().center())):
        QTest.mouseMove(target, pos)
        QTest.qWait(20)
        probe = button.geometry().topLeft() + QPoint(3, button.height() // 2)
        fills.append(host.grab().toImage().pixelColor(probe).name())
    host.close()
    return fills[0], fills[1]


def test_hover_on_a_toggle_that_is_off_draws_no_fill(qapp):
    """The fill means checked."""
    for button in (tool_toggle("fa5s.circle", "Oval", ""), ToggleMenuButton("fa5s.magic", "", "")):
        rest, hover = _fill_at_rest_and_under_mouse(qapp, button)
        assert rest == hover, type(button).__name__


def test_hover_on_an_action_fills(qapp):
    rest, hover = _fill_at_rest_and_under_mouse(qapp, labeled_action("fa5s.undo", "Reset", ""))
    assert rest != hover, (rest, hover)


def _paint(width: int, height: int, paint) -> QImage:
    image = QImage(width, height, QImage.Format.Format_ARGB32)
    image.fill(QColor(THEME.bg_panel))
    p = QPainter(image)
    paint(p)
    p.end()
    return image


def test_the_current_row_takes_the_chip_and_no_bar(qapp):
    """History, Library and preset rows: the chip of a checked toggle marks the current one."""
    image = _paint(200, 40, lambda p: paint_fill(p, QRect(0, 0, 200, 40), current=True, hover=False))
    names = {image.pixelColor(x, 20).name() for x in range(6)}

    assert image.pixelColor(100, 20).name() == QColor(THEME.bg_checked).name()
    assert QColor(THEME.border_checked).name() in names and QColor(THEME.accent_secondary).name() not in names


def test_a_checked_menu_item_takes_the_chip(qapp):
    menu = QMenu()
    menu.setStyleSheet(load_stylesheet())
    menu.addAction("Off").setCheckable(True)
    on = menu.addAction("On")
    on.setCheckable(True)
    on.setChecked(True)
    menu.popup(QPoint(0, 0))
    QTest.qWait(20)
    image = menu.grab().toImage()
    row = menu.actionGeometry(on)
    colors = {image.pixelColor(x, row.center().y()).name() for x in range(row.left(), row.right())}
    menu.close()

    assert QColor(THEME.bg_checked).name() in colors


def test_the_current_dropdown_row_takes_the_chip_and_lightens_on_hover(qapp):
    combo = StepCombo()
    combo.addItems(["Digital", "Paper"])
    combo.setCurrentIndex(1)
    delegate = combo.view().itemDelegate()

    def fill(state) -> str:
        option = QStyleOptionViewItem()
        option.rect = QRect(0, 0, 200, 24)
        option.state = QStyle.StateFlag.State_Enabled | state
        return _paint(200, 24, lambda p: delegate.paint(p, option, combo.model().index(1, 0))).pixelColor(3, 12).name()

    assert fill(QStyle.StateFlag.State_None) == QColor(THEME.bg_checked).name()
    assert fill(QStyle.StateFlag.State_Selected) == QColor(THEME.bg_checked_hover).name()


def test_an_edited_card_takes_a_dim_scope_stripe(qapp):
    for scope, token in (("frame", THEME.border_scope_frame), ("roll", THEME.border_checked_hover)):
        section = CollapsibleSection("Calibration")
        section.setStyleSheet(load_stylesheet())
        section.set_modified(1)
        section.set_scope_buttons(visible=True, scope=scope)
        header = section.toggle_button.grab().toImage()

        assert header.pixelColor(1, header.height() // 2).name() == QColor(token).name(), scope


def test_the_lit_scope_button_is_white(qapp):
    section = CollapsibleSection("Calibration")
    for scope, btn in (("frame", "frame_btn"), ("roll", "roll_btn")):
        section.set_scope_buttons(visible=True, scope=scope)
        image = getattr(section, btn).icon().pixmap(16, 16).toImage()
        white = QColor(THEME.text_primary)
        pixels = [image.pixelColor(x, y) for x in range(16) for y in range(16) if image.pixelColor(x, y).alpha() > 200]

        assert pixels and all(
            max(abs(c.red() - white.red()), abs(c.green() - white.green()), abs(c.blue() - white.blue())) <= 3 for c in pixels
        ), scope


def test_a_primary_button_is_a_dark_red_fill(qapp):
    host = QWidget()
    host.setStyleSheet(load_stylesheet())
    button = labeled_action("fa5s.check", "Export", "", primary=True)
    QHBoxLayout(host).addWidget(button)
    host.resize(240, 60)
    image = host.grab().toImage()
    probe = button.geometry().topLeft() + QPoint(4, button.height() // 2)

    assert image.pixelColor(probe).name() == QColor(THEME.bg_primary).name()
