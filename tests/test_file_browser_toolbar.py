from types import SimpleNamespace

import pytest

from PyQt6.QtCore import Qt

from negpy.desktop.view.styles.templates import BAR_BUTTON_HEIGHT, TOOLBAR_BUTTON_HEIGHT
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
    """The Film Strip's Sort orders the frames, the Library's the roll list. The strip's sits
    in the canvas bar, at the bar's height."""
    browser = panel.file_browser
    tree = panel.library_tree

    assert browser.roll_row.isAncestorOf(browser.sort_btn)
    assert tree.sort_btn in tree.toolbar.buttons
    assert browser.sort_btn is not tree.sort_btn
    assert (browser.sort_btn.height(), tree.sort_btn.height()) == (BAR_BUTTON_HEIGHT, TOOLBAR_BUTTON_HEIGHT)


def test_the_roll_row_names_its_dropdowns_by_their_choice(panel):
    browser = panel.file_browser
    browser._apply_sort_order("date", save=False)
    browser._apply_sheet_filter("keepers", save=False)

    assert (browser.sort_btn.text(), browser.sheet_btn.text()) == ("Date", "Keepers Only")
    assert browser.apply_btn.text() == "Apply…"


def test_the_roll_menu_holds_the_actions_out_of_view(panel):
    browser = panel.file_browser
    labels = [action.text() for action in browser.roll_menu_btn.menu().actions() if not action.isSeparator()]
    assert [label.split("\t")[0] for label in labels] == [
        "Add Files…",
        "Add Folder…",
        "Save as Roll…",
        "Roll Settings…",
        "Update Thumbnails",
        "Hot Folder",
        "Unload…",
        "New Roll…",
        "Close Roll…",
        "Reset Roll to Defaults…",
        "Film Strip Guide…",
    ]


def test_the_hot_folder_shows_in_the_row_while_it_is_on(panel):
    browser = panel.file_browser
    assert browser.hot_folder_btn.isHidden()

    browser.hot_folder_action.setChecked(True)
    assert not browser.hot_folder_btn.isHidden() and browser.scan_timer.isActive()

    browser.hot_folder_btn.click()
    assert not browser.hot_folder_action.isChecked()
    assert browser.hot_folder_btn.isHidden() and not browser.scan_timer.isActive()


def test_update_thumbnails_refreshes_the_whole_roll(panel):
    panel.file_browser.update_thumbnails_action.trigger()
    panel.file_browser.controller.request_thumbnail_refresh.assert_called_once_with("roll")


def test_update_thumbnails_cancels_instead_while_running(panel):
    panel.file_browser.controller.thumbnail_refresh_running = True

    panel.file_browser.update_thumbnails_action.trigger()

    panel.file_browser.controller.cancel_thumbnail_refresh.assert_called_once_with()
    panel.file_browser.controller.request_thumbnail_refresh.assert_not_called()


def test_update_thumbnails_reflects_the_running_state(panel):
    browser = panel.file_browser
    idle = browser.update_thumbnails_action.text()

    browser._on_thumbnail_refresh_state_changed(True)
    assert browser.update_thumbnails_action.text() == "Cancel Thumbnail Update"

    browser._on_thumbnail_refresh_state_changed(False)
    assert browser.update_thumbnails_action.text() == idle


def test_a_narrow_row_drops_the_names_before_the_filter_gets_cramped(panel, qapp):
    browser = panel.file_browser
    row = browser.roll_row
    browser._show_save_roll(True)
    row.resize(1400, 40)
    row.show()
    qapp.processEvents()
    assert browser.apply_btn.toolButtonStyle() == Qt.ToolButtonStyle.ToolButtonTextBesideIcon
    assert not browser.save_roll_btn.isHidden()

    row.resize(400, 40)
    qapp.processEvents()
    assert all(btn.toolButtonStyle() == Qt.ToolButtonStyle.ToolButtonIconOnly for btn in browser._named_roll_buttons)
    assert browser.save_roll_btn.isHidden()

    row.resize(1400, 40)
    qapp.processEvents()
    assert browser.apply_btn.toolButtonStyle() == Qt.ToolButtonStyle.ToolButtonTextBesideIcon


def test_save_as_roll_leaves_the_row_before_the_names_do(panel, qapp):
    browser = panel.file_browser
    browser._show_save_roll(True)
    row = browser.roll_row
    row.show()
    states = []
    for width in range(1400, 380, -10):
        row.resize(width, 40)
        qapp.processEvents()
        states.append(
            (not browser.save_roll_btn.isHidden(), browser.apply_btn.toolButtonStyle() == Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        )

    assert states[0] == (True, True) and states[-1] == (False, False)
    assert (False, True) in states
    assert (True, False) not in states


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
