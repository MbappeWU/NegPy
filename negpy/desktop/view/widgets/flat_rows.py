"""Flat rows a delegate paints, for the History steps and the Library's rolls: a fill for the
hovered, selected or current row, a red bar on the current one, a pill, and ⋮ on hover."""

from typing import Optional

import qtawesome as qta
from PyQt6.QtCore import QPoint, QRect, QRectF, Qt
from PyQt6.QtGui import QColor, QFont, QFontMetrics, QPainter

from negpy.desktop.view.styles.theme import THEME

ICON = 16


def more_rect(row: QRect) -> QRect:
    """Where a row draws its ⋮."""
    return QRect(row.right() - THEME.space_lg - ICON, row.center().y() - ICON // 2, ICON, ICON)


def more_press(view, event) -> Optional[QPoint]:
    """The press position when it lands on a row's ⋮, which opens that row's menu instead of picking it."""
    pos = event.position().toPoint()
    item = view.itemAt(pos)
    return pos if item is not None and more_rect(view.visualItemRect(item)).contains(pos) else None


def paint_fill(p: QPainter, rect: QRect, *, current: bool, hover: bool, selected: bool = False) -> None:
    p.setPen(Qt.PenStyle.NoPen)
    if current or selected or hover:
        p.setBrush(QColor(THEME.bg_selected if current or selected else THEME.bg_hover))
        p.drawRoundedRect(QRectF(rect), THEME.radius_md, THEME.radius_md)
    if current:
        p.setBrush(QColor(THEME.accent_secondary))
        p.drawRoundedRect(QRectF(rect.left(), rect.top() + THEME.space_md, 3, rect.height() - 2 * THEME.space_md), 1.5, 1.5)


def paint_pill(p: QPainter, right: int, center_y: float, text: str, font: QFont, *, accent: bool) -> int:
    """A rounded tag that ends at right; returns its left edge."""
    metrics = QFontMetrics(font)
    width = metrics.horizontalAdvance(text) + 2 * THEME.space_md
    height = metrics.height() + 2
    pill = QRectF(right - width, center_y - height / 2, width, height)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(QColor(THEME.accent_primary if accent else THEME.border_color))
    p.drawRoundedRect(pill, height / 2, height / 2)
    p.setFont(font)
    p.setPen(QColor(THEME.text_primary if accent else THEME.text_hint))
    p.drawText(pill, Qt.AlignmentFlag.AlignCenter, text)
    return int(pill.left())


def paint_more(p: QPainter, row: QRect) -> None:
    qta.icon("mdi6.dots-vertical", color=THEME.text_hint).paint(p, more_rect(row))
