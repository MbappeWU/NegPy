from PyQt6.QtCore import QPoint
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QHBoxLayout, QWidget

from negpy.desktop.view.styles.templates import labeled_action, load_stylesheet, tool_toggle
from negpy.desktop.view.widgets.choice_button import ToggleMenuButton


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
