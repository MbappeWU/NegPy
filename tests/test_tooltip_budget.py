"""A tooltip is one short, plain sentence; the detail lives in the card's ⓘ guide."""

import html
import re

from conftest import FakeController, FakeRepo

MAX_WORDS = 25
# Shortcut chips render as a trailing table, and a slider appends its reset hint as a <div>.
_CHROME = re.compile(r"<table.*?</table>|<div[^>]*>.*?</div>", re.S)
_WORD = re.compile(r"[^\W\d_][\w'’.-]*")


def _plain(tip: str) -> str:
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", _CHROME.sub(" ", tip))).split())


def test_every_panel_tooltip_is_short_and_has_no_dash_aside(qapp):
    from PyQt6.QtWidgets import QWidget

    from negpy.desktop.view.sidebar.right_panel import RightPanel

    panel = RightPanel(FakeController(FakeRepo()))
    panel.apply_shortcut_tooltips()
    panel.controls_panel.apply_shortcut_tooltips()

    tips = {_plain(w.toolTip()) for w in panel.findChildren(QWidget)} - {""}
    long = sorted(t for t in tips if len(_WORD.findall(t)) > MAX_WORDS)
    dashed = sorted(t for t in tips if "—" in t)
    assert not long, f"Tooltips over {MAX_WORDS} words; move the detail to docs/USER_GUIDE.md:\n" + "\n".join(long)
    assert not dashed, "Tooltips with an em dash; use a period, colon or comma:\n" + "\n".join(dashed)
