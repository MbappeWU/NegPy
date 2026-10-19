from negpy.desktop.view.widgets.panel_tab import PanelTab


def test_an_icon_only_tab_keeps_its_name_for_the_menu_and_find(qapp):
    tab = PanelTab("mdi6.star-outline", "Favorites", icon_only=True)
    assert tab.text() == "Favorites" and not tab.icon().isNull()
    assert tab.minimumWidth() == tab.maximumWidth() == PanelTab.ICON_ONLY_WIDTH


def test_a_page_tab_is_wide_enough_for_its_icon_and_name(qapp):
    assert PanelTab.min_width(["Geometry"], stacked=False) > PanelTab.min_width(["Geometry"], stacked=True)


def test_a_mark_shows_edits_on_the_tab(qapp):
    tab = PanelTab("mdi6.crop", "Geometry")
    assert not tab.is_marked()
    tab.set_marked(True)
    assert tab.is_marked()
