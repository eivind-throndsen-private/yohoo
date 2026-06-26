"""
Test suite for drag-and-drop and reset functionality
Tests both HTML generation correctness and runtime behavior
"""
import pytest
import os
import sys
import json
import re
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from generate_html import generate_html, load_default_links, DEFAULT_LINKS_FILE


class TestHTMLGeneration:
    """Test that the HTML is generated correctly with required fixes"""

    @pytest.fixture
    def generated_html(self, tmp_path):
        """Generate HTML to a temporary file for testing"""
        output_file = tmp_path / "test_yohoo.html"

        # Generate using the actual function
        generate_html(str(output_file))

        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()

        return content

    def test_drag_drop_css_fix_present(self, generated_html):
        """Test that the CSS fix for drag-and-drop is present"""
        # Check for pointer-events: none on link children
        assert '.link-item > *' in generated_html, "Missing CSS selector for link children"
        assert 'pointer-events: none' in generated_html, "Missing pointer-events: none CSS rule"

        # Check for re-enabled pointer events on delete icon
        assert 'pointer-events: auto' in generated_html, "Missing pointer-events: auto for delete icon"

    def test_default_data_embedded(self, generated_html):
        """Test that DEFAULT_DATA constant is embedded in the HTML"""
        assert 'const DEFAULT_DATA = {' in generated_html, "DEFAULT_DATA constant not found in HTML"
        assert '"sections":' in generated_html, "DEFAULT_DATA doesn't contain sections"

        # Verify it contains expected section IDs
        assert '"norway-essentials"' in generated_html, "norway-essentials section missing from DEFAULT_DATA"
        assert '"developer-tools"' in generated_html, "developer-tools section missing from DEFAULT_DATA"

    def test_reset_function_exists(self, generated_html):
        """Test that resetToDefaults function is defined"""
        assert 'function resetToDefaults()' in generated_html, "resetToDefaults function not found"

        # Check for key reset operations
        assert 'localStorage.removeItem(STORAGE_KEY)' in generated_html, "localStorage clear missing from reset"
        assert 'DEFAULT_DATA.sections' in generated_html, "Reset doesn't use DEFAULT_DATA"
        assert 'setupDragAndDrop()' in generated_html, "Reset doesn't re-initialize drag and drop"

    def test_reset_button_calls_function(self, generated_html):
        """Test that reset button calls resetToDefaults instead of location.reload"""
        # Find reset button handler
        reset_handler_pattern = r"getElementById\('resetBtn'\)\.addEventListener\('click'.*?\{\s*(.*?)\s*\}\)"
        match = re.search(reset_handler_pattern, generated_html, re.DOTALL)

        assert match, "Reset button event listener not found"
        handler_code = match.group(1)

        assert 'resetToDefaults()' in handler_code, "Reset button doesn't call resetToDefaults()"
        assert 'location.reload()' not in handler_code, "Reset button still uses location.reload() - BUG!"

    def test_all_draggable_links_have_attributes(self, generated_html):
        """Test that all generated links have required draggable attributes"""
        # Find all link items
        link_pattern = r'<a[^>]*class="link-item"[^>]*>'
        links = re.findall(link_pattern, generated_html)

        assert len(links) > 0, "No link items found in HTML"

        for link in links:
            assert 'draggable="true"' in link, f"Link missing draggable attribute: {link}"
            assert 'data-url=' in link, f"Link missing data-url attribute: {link}"
            assert 'data-title=' in link, f"Link missing data-title attribute: {link}"

    def test_drag_handlers_exist(self, generated_html):
        """Test that all drag and drop handlers are defined"""
        required_handlers = [
            'handleLinkDragStart',
            'handleLinkDragEnd',
            'handleLinkDragOver',
            'handleLinkDragLeave',
            'handleLinkDrop',
            'handleSectionDragStart',
            'handleSectionDragEnd',
            'handleSectionDragOver',
            'handleSectionDragLeave',
            'handleSectionDrop',
        ]

        for handler in required_handlers:
            assert f'function {handler}' in generated_html, f"Handler {handler} not found in HTML"

    def test_default_data_completeness(self, generated_html):
        """Test that embedded DEFAULT_DATA matches source default_links.json"""
        # Extract DEFAULT_DATA from HTML
        data_pattern = r'const DEFAULT_DATA = (\{[\s\S]*?\});'
        match = re.search(data_pattern, generated_html)

        assert match, "Could not extract DEFAULT_DATA from HTML"

        embedded_data_str = match.group(1)
        embedded_data = json.loads(embedded_data_str)

        # Load original default links
        original_data = load_default_links(DEFAULT_LINKS_FILE)

        # Compare sections
        assert len(embedded_data['sections']) == len(original_data['sections']), \
            "Embedded data has different number of sections than original"

        # Check first and last section IDs match
        assert embedded_data['sections'][0]['id'] == original_data['sections'][0]['id'], \
            "First section ID doesn't match"
        assert embedded_data['sections'][-1]['id'] == original_data['sections'][-1]['id'], \
            "Last section ID doesn't match"

    def test_reset_rebuilds_all_sections(self, generated_html):
        """Test that reset function rebuilds all sections from DEFAULT_DATA"""
        # Find resetToDefaults function
        reset_func_pattern = r'function resetToDefaults\(\) \{([\s\S]*?)\n\s{8}\}'
        match = re.search(reset_func_pattern, generated_html)

        assert match, "Could not find resetToDefaults function body"
        reset_code = match.group(1)

        # Check it iterates over DEFAULT_DATA sections
        assert 'DEFAULT_DATA.sections' in reset_code, "Reset doesn't iterate over DEFAULT_DATA.sections"
        assert 'DEFAULT_DATA.userSections' in reset_code, "Reset doesn't handle userSections"

        # Check it creates section elements
        assert 'document.createElement' in reset_code, "Reset doesn't create new elements"
        assert 'container.appendChild' in reset_code, "Reset doesn't append sections to container"

    def test_delete_icon_has_onclick_handler(self, generated_html):
        """Test that delete icons have proper onclick handlers"""
        delete_icon_pattern = r'<span class="delete-icon"[^>]*>'
        delete_icons = re.findall(delete_icon_pattern, generated_html)

        assert len(delete_icons) > 0, "No delete icons found"

        for icon in delete_icons:
            assert 'onclick=' in icon, f"Delete icon missing onclick handler: {icon}"
            assert 'deleteLink' in icon, f"Delete icon doesn't call deleteLink: {icon}"


class TestDefaultLinksData:
    """Test the default_links.json data structure"""

    @pytest.fixture
    def default_data(self):
        """Load default links data"""
        return load_default_links(DEFAULT_LINKS_FILE)

    def test_default_data_has_sections(self, default_data):
        """Test that default data contains sections"""
        assert 'sections' in default_data, "default_links.json missing 'sections' key"
        assert len(default_data['sections']) > 0, "No sections defined in default_links.json"

    def test_all_sections_have_required_fields(self, default_data):
        """Test that all sections have required fields"""
        required_fields = ['id', 'name', 'emoji', 'links']

        for section in default_data['sections']:
            for field in required_fields:
                assert field in section, f"Section {section.get('id', 'unknown')} missing {field}"

    def test_all_links_have_required_fields(self, default_data):
        """Test that all links have required fields"""
        required_fields = ['title', 'url', 'domain']

        for section in default_data['sections']:
            for link in section.get('links', []):
                for field in required_fields:
                    assert field in link, \
                        f"Link in section {section['id']} missing {field}: {link}"

    def test_user_sections_exist(self, default_data):
        """Test that user sections are defined"""
        assert 'userSections' in default_data, "default_links.json missing 'userSections' key"
        assert len(default_data['userSections']) > 0, "No user sections defined"

    def test_user_sections_have_placeholders(self, default_data):
        """Test that user sections have placeholder text"""
        for section in default_data.get('userSections', []):
            assert 'placeholder' in section, f"User section {section.get('id')} missing placeholder"
            assert len(section.get('links', [])) == 0, \
                f"User section {section.get('id')} should start with empty links"


class TestRegressionPrevention:
    """Regression tests to prevent the specific bugs from returning"""

    def test_no_location_reload_in_reset(self):
        """REGRESSION TEST: Ensure reset doesn't use location.reload()"""
        # Generate fresh HTML
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            temp_path = f.name

        try:
            generate_html(temp_path)

            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Find reset button handler
            reset_pattern = r"getElementById\('resetBtn'\)\.addEventListener.*?\{([\s\S]*?)\}\);"
            match = re.search(reset_pattern, content)

            assert match, "Reset button handler not found"
            handler = match.group(1)

            # BUG: If this fails, the old broken behavior has returned
            assert 'location.reload()' not in handler, \
                "REGRESSION: Reset button uses location.reload() again! This is the bug we fixed."

            assert 'resetToDefaults()' in handler, \
                "REGRESSION: Reset button doesn't call resetToDefaults()"

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_link_children_have_pointer_events_none(self):
        """REGRESSION TEST: Ensure drag-and-drop CSS fix is present"""
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            temp_path = f.name

        try:
            generate_html(temp_path)

            with open(temp_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # BUG: If this fails, the drag-and-drop fix has been removed
            assert '.link-item > *' in content, \
                "REGRESSION: CSS selector for link children is missing"

            # Find the CSS rule for .link-item > *
            css_rule_pattern = r'\.link-item > \* \{([^}]*)\}'
            match = re.search(css_rule_pattern, content)

            assert match, "REGRESSION: .link-item > * CSS rule not found"
            rule_content = match.group(1)

            assert 'pointer-events: none' in rule_content, \
                "REGRESSION: pointer-events: none is missing from .link-item > * - drag and drop will break on Chrome/Windows!"

        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
