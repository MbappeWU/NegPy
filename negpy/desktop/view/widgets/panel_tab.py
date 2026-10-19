"""The right panel's tabs."""

from PyQt6.QtCore import QPointF, QRect, QRectF, Qt
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QIcon, QPainter
from PyQt6.QtWidgets import QAbstractButton
import qtawesome as qta

from negpy.desktop.view.styles.fonts import ui_font_family
from negpy.desktop.view.styles.theme import THEME

_STACKED_ICON = 21
_ICON = 17
_DOT = 6


def _font(checked: bool) -> QFont:
    font = QFont(ui_font_family())
    font.setPixelSize(THEME.font_size_base)
    font.setWeight(QFont.Weight(THEME.weight_semibold if checked else THEME.weight_medium))
    return font


class PanelTab(QAbstractButton):
    """A right-panel tab. A main tab sits on a header strip with its name under a large icon. A
    page's tab has its name beside the icon, or shows only the icon and keeps the name for the
    tooltip and the » menu. A dot marks a tab with edits."""

    ICON_ONLY_WIDTH = 38

    def __init__(self, icon: str, text: str, *, stacked: bool = False, icon_only: bool = False, divider: bool = False, parent=None) -> None:
        super().__init__(parent)
        self.setCheckable(True)
        self.setText(text)
        self.setFocusPolicy(Qt.FocusPolicy.TabFocus)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover)
        self._stacked = stacked
        self._icon_only = icon_only
        self._divider = divider
        self._marked = False
        on = THEME.accent_secondary if stacked else THEME.text_primary
        self.setIcon(qta.icon(icon, color=THEME.text_hint, color_active=THEME.text_primary, color_on=on, color_on_active=on))
        if icon_only:
            self.setFixedWidth(self.ICON_ONLY_WIDTH)

    @staticmethod
    def min_width(labels: list[str], *, stacked: bool) -> int:
        """Widest name at the checked weight, so a tab spills into » before its name clips."""
        text = max(QFontMetrics(_font(True)).horizontalAdvance(label) for label in labels)
        return text + 2 * THEME.space_md if stacked else text + _ICON + THEME.space_md + 2 * THEME.space_sm

    def set_marked(self, marked: bool) -> None:
        if marked != self._marked:
            self._marked = marked
            self.update()

    def is_marked(self) -> bool:
        return self._marked

    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        checked, hover = self.isChecked(), self.underMouse()
        if self._stacked:
            p.fillRect(self.rect(), QColor(THEME.bg_panel if checked else THEME.bg_selected if hover else THEME.bg_header))
        p.fillRect(0, h - 1, w, 1, QColor(THEME.border_primary))
        if self._divider:
            p.fillRect(0, THEME.space_xl, 1, h - 2 * THEME.space_xl, QColor(THEME.border_primary))

        font = _font(checked)
        fm = QFontMetrics(font)
        text_w = 0 if self._icon_only else fm.horizontalAdvance(self.text())
        if self._stacked:
            size = _STACKED_ICON
            top = (h - size - THEME.space_xs - fm.height()) // 2
            icon_rect = QRect((w - size) // 2, top, size, size)
            text_rect = QRect((w - text_w) // 2, top + size + THEME.space_xs, text_w, fm.height())
        else:
            size = _ICON
            left = (w - size - (THEME.space_md + text_w if text_w else 0)) // 2
            icon_rect = QRect(left, (h - size) // 2, size, size)
            text_rect = QRect(left + size + THEME.space_md, (h - fm.height()) // 2, text_w, fm.height())
        mode = QIcon.Mode.Active if hover else QIcon.Mode.Normal
        self.icon().paint(p, icon_rect, Qt.AlignmentFlag.AlignCenter, mode, QIcon.State.On if checked else QIcon.State.Off)
        if text_w:
            p.setFont(font)
            p.setPen(QColor(THEME.text_primary if checked or hover else THEME.text_hint))
            p.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, self.text())

        p.setPen(Qt.PenStyle.NoPen)
        if checked:
            bar, inset = (3, THEME.space_xl) if self._stacked else (2, THEME.space_lg)
            p.setBrush(QColor(THEME.accent_secondary))
            # Twice the bar's height, cut by the bottom edge: only the top corners round.
            p.drawRoundedRect(QRectF(inset, h - bar, w - 2 * inset, 2 * bar), bar, bar)
        if self._marked:
            anchor = text_rect if text_w else icon_rect
            p.setBrush(QColor(THEME.channel_red))
            p.drawEllipse(QPointF(anchor.right() + THEME.space_md, anchor.top() + THEME.space_xs), _DOT / 2, _DOT / 2)
        if self.hasFocus():
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(QColor(THEME.accent_secondary))
            p.drawRect(QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5))
