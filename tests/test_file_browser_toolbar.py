from types import SimpleNamespace

import pytest

from negpy.desktop.view.styles.templates import TOOLBAR_BUTTON_HEIGHT
from negpy.desktop.session import AssetListModel
from negpy.desktop.view.sidebar.files import FileBrowser

from conftest import FakeController as _Controller, FakeRepo as _Repo


@pytest.fixture
def panel(qapp):
    controller = _Controller(_Repo())
    controller.session.asset_model = AssetListModel(controller.state)
    browser = FileBrowser(controller)
    browser.resize(300, 700)
    browser.show()
    browser.library_tree.resize(300, 400)
    browser.library_tree.show()
    qapp.processEvents()
    return SimpleNamespace(file_browser=browser, library_tree=browser.library_tree)


def test_each_section_toolbar_has_its_own_sort(panel):
    """The Film Strip's Sort orders the frames, the Library's the roll list; both sized like
    every other section-toolbar button."""
    browser = panel.file_browser
    tree = panel.library_tree

    assert browser.sort_btn in browser.film_strip_toolbar.buttons
    assert tree.sort_btn in tree.toolbar.buttons
    assert browser.sort_btn is not tree.sort_btn
    assert {browser.sort_btn.height(), tree.sort_btn.height()} == {TOOLBAR_BUTTON_HEIGHT}


def test_both_section_toolbars_size_their_buttons_the_same(panel):
    browser = panel.file_browser
    tree = panel.library_tree

    heights = {b.height() for b in tree.toolbar.buttons + browser.film_strip_toolbar.buttons}

    assert heights == {TOOLBAR_BUTTON_HEIGHT}


def test_film_strip_toolbar_holds_roll_scoped_actions(panel):
    browser = panel.file_browser
    expected = [
        browser.save_roll_btn,
        browser.add_btn,
        browser.hot_folder_btn,
        browser.apply_btn,
        browser.roll_settings_btn,
        browser.update_thumbnails_btn,
        browser.unload_btn,
        browser.sort_btn,
        browser.sheet_btn,
    ]
    assert browser.film_strip_toolbar.buttons == expected


def test_new_roll_lives_in_the_roll_row_menu(panel):
    """Not a toolbar button: the ⋮ menu at the end of the toolbar's Roll row."""
    browser = panel.file_browser
    assert not hasattr(browser, "new_roll_btn")
    labels = [action.text() for action in browser.roll_menu_btn.menu().actions()]
    assert labels == ["New Roll…", "Close Roll…", "Reset Roll to Defaults…"]


def test_update_thumbnails_button_refreshes_the_whole_roll(panel):
    panel.file_browser.update_thumbnails_btn.click()
    panel.file_browser.controller.request_thumbnail_refresh.assert_called_once_with("roll")


def test_update_thumbnails_button_cancels_instead_while_running(panel):
    panel.file_browser.controller.thumbnail_refresh_running = True

    panel.file_browser.update_thumbnails_btn.click()

    panel.file_browser.controller.cancel_thumbnail_refresh.assert_called_once_with()
    panel.file_browser.controller.request_thumbnail_refresh.assert_not_called()


def test_update_thumbnails_button_reflects_the_running_state(panel):
    browser = panel.file_browser
    idle_tip = browser.update_thumbnails_btn.toolTip()

    browser._on_thumbnail_refresh_state_changed(True)
    running_tip = browser.update_thumbnails_btn.toolTip()
    assert running_tip != idle_tip
    assert "Cancel" in running_tip

    browser._on_thumbnail_refresh_state_changed(False)
    assert browser.update_thumbnails_btn.toolTip() == idle_tip


def test_narrowing_the_panel_raises_a_populated_overflow_menu(panel, qapp):
    """QToolBar's native extension menu was tried first and came up empty: widgets added with
    addWidget() become QWidgetActions its popup cannot host."""
    toolbar = panel.file_browser.film_strip_toolbar
    row = panel.file_browser.roll_row
    row.resize(1400, 40)
    row.show()
    qapp.processEvents()
    assert not toolbar.overflow_btn.isVisible()

    row.resize(320, 40)
    qapp.processEvents()
    assert toolbar.overflow_btn.isVisible()

    labels = [action.text() for action in toolbar.build_overflow_menu().actions()]
    assert labels, "overflow button with an empty menu"
    assert "Sheet filter" in labels


def test_film_strip_toolbar_minimum_is_not_the_sum_of_its_buttons(panel):
    toolbar = panel.file_browser.film_strip_toolbar
    assert toolbar.minimumSizeHint().width() < toolbar.sizeHint().width()


def test_the_roll_row_shrinks_below_its_natural_width(panel):
    row = panel.file_browser.roll_row
    assert row.minimumSizeHint().width() < row.sizeHint().width()


def test_a_switched_off_toolbar_button_stays_off_across_a_resize(panel):
    """_relayout shows whatever fits, so an opt-in button hidden with a bare
    setVisible would come back on the next resize."""
    tree = panel.library_tree

    assert not tree.index_btn.isVisible()

    tree.toolbar.resize(600, tree.toolbar.height())

    assert not tree.index_btn.isVisible()
    assert [a.text() for a in tree.toolbar.build_overflow_menu().actions()] == []


def test_turning_an_opt_in_button_on_places_it(panel):
    tree = panel.library_tree

    tree.toolbar.set_button_visible(tree.index_btn, True)
    tree.toolbar.resize(600, tree.toolbar.height())

    assert tree.index_btn.isVisible()


def test_the_sheet_and_the_roll_list_sort_independently(panel):
    tree = panel.library_tree
    tree_before = (tree._sort_order, tree._sort_descending)

    panel.file_browser._apply_sort_direction(True)
    panel.file_browser._apply_sort_order("date")

    assert (tree._sort_order, tree._sort_descending) == tree_before
