"""
Browser-based end-to-end tests for drag-and-drop and reset functionality
Requires: playwright (install with: pip install pytest-playwright && playwright install)
"""
import pytest
import os
import sys
import json
from pathlib import Path
from playwright.sync_api import Page, expect

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from generate_html import generate_html

# Path to test HTML file
TEST_HTML_PATH = Path(__file__).parent.parent / 'yohoo.html'


@pytest.fixture(scope='session')
def ensure_html_exists():
    """Ensure yohoo.html exists before tests run"""
    if not TEST_HTML_PATH.exists():
        # Generate it if missing
        generate_html(str(TEST_HTML_PATH))
    return TEST_HTML_PATH


@pytest.fixture
def page_with_yohoo(page: Page, ensure_html_exists):
    """Load yohoo.html in browser and return page"""
    # Clear localStorage before each test
    page.goto(f'file://{ensure_html_exists.absolute()}')
    page.evaluate('localStorage.clear()')
    page.reload()
    return page


class TestDragAndDrop:
    """Test drag-and-drop functionality in actual browser"""

    def test_link_is_draggable(self, page_with_yohoo: Page):
        """Test that links have draggable attribute set"""
        page = page_with_yohoo

        # Find first link
        first_link = page.locator('.link-item').first
        assert first_link.get_attribute('draggable') == 'true', \
            "Link is not marked as draggable"

    def test_drag_link_between_sections(self, page_with_yohoo: Page):
        """Test dragging a link from one section to another"""
        page = page_with_yohoo

        # Get initial state
        norway_section = page.locator('[data-section="norway-essentials"]')
        developer_section = page.locator('[data-section="developer-tools"]')

        # Count initial links
        initial_norway_count = norway_section.locator('.link-item').count()
        initial_dev_count = developer_section.locator('.link-item').count()

        # Get first link from Norway section
        link_to_move = norway_section.locator('.link-item').first
        link_text = link_to_move.locator('.link-text').inner_text()

        # Drag the link to developer section
        developer_links_list = developer_section.locator('.links-list')

        link_to_move.drag_to(developer_links_list)

        # Wait for any animations
        page.wait_for_timeout(500)

        # Verify link moved
        new_norway_count = norway_section.locator('.link-item').count()
        new_dev_count = developer_section.locator('.link-item').count()

        assert new_norway_count == initial_norway_count - 1, \
            f"Link was not removed from source section (was {initial_norway_count}, now {new_norway_count})"
        assert new_dev_count == initial_dev_count + 1, \
            f"Link was not added to target section (was {initial_dev_count}, now {new_dev_count})"

        # Verify the specific link is now in developer section
        developer_link_texts = [
            loc.inner_text()
            for loc in developer_section.locator('.link-text').all()
        ]
        assert link_text in developer_link_texts, \
            f"Moved link '{link_text}' not found in target section"

    def test_drag_persists_after_reload(self, page_with_yohoo: Page):
        """Test that dragged links persist in localStorage after page reload"""
        page = page_with_yohoo

        # Move a link
        norway_section = page.locator('[data-section="norway-essentials"]')
        developer_section = page.locator('[data-section="developer-tools"]')

        link_to_move = norway_section.locator('.link-item').first
        link_url = link_to_move.get_attribute('data-url')

        developer_links_list = developer_section.locator('.links-list')
        link_to_move.drag_to(developer_links_list)

        page.wait_for_timeout(500)

        # Reload page
        page.reload()

        # Verify link is still in developer section
        developer_section_after = page.locator('[data-section="developer-tools"]')
        link_in_dev = developer_section_after.locator(f'[data-url="{link_url}"]')

        assert link_in_dev.count() == 1, \
            "Link position was not persisted after reload"

    def test_section_drag_and_drop(self, page_with_yohoo: Page):
        """Test dragging sections to reorder them"""
        page = page_with_yohoo

        # Get section IDs in original order
        original_order = [
            el.get_attribute('data-section')
            for el in page.locator('.section').all()
        ]

        # Drag first section to after second section
        first_section = page.locator('.section').first
        second_section = page.locator('.section').nth(1)

        # Drag by section header (not links)
        first_header = first_section.locator('.section-header')
        second_header = second_section.locator('.section-header')

        first_header.drag_to(second_header)

        page.wait_for_timeout(500)

        # Get new order
        new_order = [
            el.get_attribute('data-section')
            for el in page.locator('.section').all()
        ]

        # Verify order changed
        assert new_order != original_order, \
            "Section order did not change after drag and drop"

        # Verify first section is no longer first
        assert new_order[0] != original_order[0], \
            "First section is still in first position"


class TestResetFunctionality:
    """Test reset to defaults functionality"""

    def test_reset_button_exists(self, page_with_yohoo: Page):
        """Test that reset button is present and accessible"""
        page = page_with_yohoo

        # Open settings modal
        settings_btn = page.locator('#settingsBtn')
        settings_btn.click()

        # Wait for modal
        page.wait_for_selector('#settingsModal.show')

        # Find reset button
        reset_btn = page.locator('#resetBtn')
        assert reset_btn.is_visible(), "Reset button is not visible in settings modal"

    def test_reset_restores_defaults(self, page_with_yohoo: Page):
        """Test that reset restores the exact default state"""
        page = page_with_yohoo

        # Record default state
        default_sections = [
            el.get_attribute('data-section')
            for el in page.locator('.section').all()
        ]
        default_link_count = page.locator('.link-item').count()

        # Make changes
        # 1. Delete a link
        first_link = page.locator('.link-item').first
        first_link.hover()
        delete_icon = first_link.locator('.delete-icon')
        delete_icon.click()

        page.wait_for_timeout(300)

        # 2. Move a link
        norway_section = page.locator('[data-section="norway-essentials"]')
        developer_section = page.locator('[data-section="developer-tools"]')

        link_to_move = norway_section.locator('.link-item').first
        developer_links = developer_section.locator('.links-list')
        link_to_move.drag_to(developer_links)

        page.wait_for_timeout(300)

        # 3. Create custom section
        add_section_btn = page.locator('#addSectionBtn')
        add_section_btn.click()

        page.wait_for_selector('#addSectionModal.show')

        name_input = page.locator('#sectionNameInput')
        name_input.fill('Test Custom Section')

        add_btn = page.locator('#modalAddBtn')
        add_btn.click()

        page.wait_for_timeout(300)

        # 4. Change font size
        settings_btn = page.locator('#settingsBtn')
        settings_btn.click()

        page.wait_for_selector('#settingsModal.show')

        font_slider = page.locator('#fontSizeSlider')
        font_slider.evaluate('el => el.value = "1.2"')
        font_slider.dispatch_event('input')

        page.wait_for_timeout(300)

        # Verify changes were made
        current_link_count = page.locator('.link-item').count()
        assert current_link_count < default_link_count, \
            "Link deletion didn't work - test setup failed"

        current_sections = [
            el.get_attribute('data-section')
            for el in page.locator('.section').all()
        ]
        assert len(current_sections) > len(default_sections), \
            "Custom section wasn't added - test setup failed"

        # Now reset
        reset_btn = page.locator('#resetBtn')

        # Handle confirmation dialog
        page.on('dialog', lambda dialog: dialog.accept())
        reset_btn.click()

        page.wait_for_timeout(500)

        # Verify restoration
        restored_link_count = page.locator('.link-item').count()
        assert restored_link_count == default_link_count, \
            f"Reset did not restore all links (expected {default_link_count}, got {restored_link_count})"

        restored_sections = [
            el.get_attribute('data-section')
            for el in page.locator('.section').all()
        ]
        assert restored_sections == default_sections, \
            "Reset did not restore original section order"

        # Verify font size reset
        font_value = page.locator('#fontSizeValue').inner_text()
        assert font_value == '100%', \
            f"Font size was not reset (expected 100%, got {font_value})"

        # Verify custom section removed
        custom_section = page.locator('[data-section*="custom"]').count()
        expected_custom_sections = sum(1 for s in default_sections if 'custom' in s or s in ['my-work', 'my-projects', 'reading-list', 'personal', 'favorites'])
        assert custom_section == expected_custom_sections, \
            f"Custom section was not removed (found {custom_section}, expected {expected_custom_sections})"

    def test_reset_clears_trash(self, page_with_yohoo: Page):
        """Test that reset clears the trash"""
        page = page_with_yohoo

        # Delete a link
        first_link = page.locator('.link-item').first
        first_link.hover()
        delete_icon = first_link.locator('.delete-icon')
        delete_icon.click()

        page.wait_for_timeout(300)

        # Verify trash has items
        trash_count = page.locator('#trashCount').inner_text()
        assert '(1)' in trash_count, "Link was not added to trash"

        # Reset
        settings_btn = page.locator('#settingsBtn')
        settings_btn.click()

        reset_btn = page.locator('#resetBtn')
        page.on('dialog', lambda dialog: dialog.accept())
        reset_btn.click()

        page.wait_for_timeout(500)

        # Verify trash is empty
        trash_count_after = page.locator('#trashCount').inner_text()
        assert '(0)' in trash_count_after, \
            f"Trash was not cleared (shows {trash_count_after})"

    def test_reset_uses_embedded_data_not_reload(self, page_with_yohoo: Page):
        """Test that reset uses embedded DEFAULT_DATA, not page reload"""
        page = page_with_yohoo

        # Inject a marker into the DOM that would survive a reload but not a rebuild
        page.evaluate('''
            document.body.setAttribute('data-test-marker', 'should-be-removed-by-reset');
        ''')

        # Verify marker exists
        marker_before = page.get_attribute('body', 'data-test-marker')
        assert marker_before == 'should-be-removed-by-reset'

        # Perform reset
        settings_btn = page.locator('#settingsBtn')
        settings_btn.click()

        reset_btn = page.locator('#resetBtn')
        page.on('dialog', lambda dialog: dialog.accept())
        reset_btn.click()

        page.wait_for_timeout(500)

        # If reset uses location.reload(), the marker would still be there after reload
        # If reset rebuilds from DEFAULT_DATA, sections container is cleared and rebuilt
        # The body marker would remain with location.reload()

        # Actually, this test is flawed. Let me test differently.
        # Better: Check that the reset function was actually called
        reset_called = page.evaluate('''
            window.resetFunctionCalled = false;
            const originalReset = window.resetToDefaults;
            window.resetToDefaults = function() {
                window.resetFunctionCalled = true;
                return originalReset.apply(this, arguments);
            };
            false;
        ''')

        # Now click reset again
        page.reload()
        settings_btn = page.locator('#settingsBtn')
        settings_btn.click()

        page.evaluate('''
            window.resetFunctionCalled = false;
            const originalReset = window.resetToDefaults;
            window.resetToDefaults = function() {
                window.resetFunctionCalled = true;
                return originalReset.apply(this, arguments);
            };
        ''')

        reset_btn = page.locator('#resetBtn')
        page.on('dialog', lambda dialog: dialog.accept())
        reset_btn.click()

        page.wait_for_timeout(500)

        was_called = page.evaluate('window.resetFunctionCalled')
        assert was_called == True, \
            "resetToDefaults function was not called - reset might be using location.reload()!"


class TestRegressionDetection:
    """Tests specifically designed to catch the original bugs if they return"""

    def test_links_draggable_on_text_span(self, page_with_yohoo: Page):
        """REGRESSION: Test that links can be dragged even when grabbing the text span"""
        page = page_with_yohoo

        # This test simulates the Chrome/Windows bug where dragging the span wouldn't work
        # Get a link's text span specifically
        link_text_span = page.locator('.link-text').first

        # Check that pointer-events is none on the span
        pointer_events = link_text_span.evaluate('el => window.getComputedStyle(el).pointerEvents')
        assert pointer_events == 'none', \
            "REGRESSION: .link-text doesn't have pointer-events: none - drag-and-drop will break on Chrome/Windows!"

    def test_delete_icon_still_clickable(self, page_with_yohoo: Page):
        """Test that delete icon is still clickable despite pointer-events fix"""
        page = page_with_yohoo

        # Find first link and hover to show delete icon
        first_link = page.locator('.link-item').first
        first_link.hover()

        # Check delete icon has pointer-events: auto
        delete_icon = first_link.locator('.delete-icon')
        pointer_events = delete_icon.evaluate('el => window.getComputedStyle(el).pointerEvents')

        assert pointer_events == 'auto', \
            "Delete icon doesn't have pointer-events: auto - it won't be clickable!"

        # Try to click it
        initial_count = page.locator('.link-item').count()
        delete_icon.click()

        page.wait_for_timeout(300)

        new_count = page.locator('.link-item').count()
        assert new_count == initial_count - 1, \
            "Delete icon is not clickable despite pointer-events: auto"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
