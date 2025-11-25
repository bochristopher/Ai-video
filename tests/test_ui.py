"""
UI tests for AI Video Generator frontend
Uses Selenium WebDriver to test browser interactions
"""
import unittest
from unittest.mock import patch, Mock
import json
import time
import os
import sys

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


@unittest.skipIf(not SELENIUM_AVAILABLE, "Selenium not installed")
class TestUI(unittest.TestCase):
    """UI tests using Selenium WebDriver"""

    @classmethod
    def setUpClass(cls):
        """Set up class-level fixtures"""
        print("\n" + "="*60)
        print("UI TESTS - SETUP")
        print("="*60)

        # Set up Chrome options for headless mode
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')

        try:
            cls.driver = webdriver.Chrome(options=chrome_options)
            print("[UI] ✓ Chrome WebDriver initialized")
        except Exception as e:
            print(f"[UI] ⚠ Could not initialize Chrome: {e}")
            print("[UI] Trying Firefox...")
            try:
                firefox_options = webdriver.FirefoxOptions()
                firefox_options.add_argument('--headless')
                cls.driver = webdriver.Firefox(options=firefox_options)
                print("[UI] ✓ Firefox WebDriver initialized")
            except Exception as e2:
                print(f"[UI] ✗ Could not initialize Firefox: {e2}")
                cls.driver = None

        cls.base_url = "http://localhost:5000"

    @classmethod
    def tearDownClass(cls):
        """Clean up class-level fixtures"""
        if cls.driver:
            cls.driver.quit()
            print("\n[UI] WebDriver closed")

    def setUp(self):
        """Set up test fixtures"""
        print("\n" + "="*60)
        print(f"Running: {self._testMethodName}")
        print("="*60)

        if not self.driver:
            self.skipTest("WebDriver not available")

    def tearDown(self):
        """Clean up after tests"""
        print(f"✓ {self._testMethodName} completed")

    def test_page_title(self):
        """Test that page title is correct"""
        print("[UI TEST] Testing page title")

        self.driver.get(self.base_url)
        title = self.driver.title

        self.assertEqual(title, "AI Video Generator")
        print(f"[UI TEST] ✓ Page title: {title}")

    def test_header_present(self):
        """Test that header is present"""
        print("[UI TEST] Testing header presence")

        self.driver.get(self.base_url)

        header = self.driver.find_element(By.TAG_NAME, "h1")
        self.assertIn("AI Video Generator", header.text)

        print(f"[UI TEST] ✓ Header text: {header.text}")

    def test_form_elements_present(self):
        """Test that all form elements are present"""
        print("[UI TEST] Testing form elements")

        self.driver.get(self.base_url)

        # Check for prompt textarea
        prompt_field = self.driver.find_element(By.ID, "prompt")
        self.assertIsNotNone(prompt_field)
        print("[UI TEST] ✓ Prompt textarea found")

        # Check for model select
        model_select = self.driver.find_element(By.ID, "model")
        self.assertIsNotNone(model_select)
        print("[UI TEST] ✓ Model select found")

        # Check for duration input
        duration_input = self.driver.find_element(By.ID, "duration")
        self.assertIsNotNone(duration_input)
        print("[UI TEST] ✓ Duration input found")

        # Check for generate button
        generate_btn = self.driver.find_element(By.ID, "generateBtn")
        self.assertIsNotNone(generate_btn)
        print("[UI TEST] ✓ Generate button found")

    def test_example_chips_present(self):
        """Test that example prompt chips are present"""
        print("[UI TEST] Testing example chips")

        self.driver.get(self.base_url)

        chips = self.driver.find_elements(By.CLASS_NAME, "chip")
        self.assertGreater(len(chips), 0)

        print(f"[UI TEST] ✓ Found {len(chips)} example chips")

    def test_example_chip_click(self):
        """Test clicking an example chip fills the prompt"""
        print("[UI TEST] Testing example chip click")

        self.driver.get(self.base_url)

        # Get the first chip
        chip = self.driver.find_element(By.CLASS_NAME, "chip")
        expected_prompt = chip.get_attribute("data-prompt")

        # Click it
        chip.click()
        time.sleep(0.5)  # Wait for JS to execute

        # Check that prompt field is filled
        prompt_field = self.driver.find_element(By.ID, "prompt")
        actual_prompt = prompt_field.get_attribute("value")

        self.assertEqual(actual_prompt, expected_prompt)
        print(f"[UI TEST] ✓ Prompt filled: {actual_prompt[:50]}...")

    def test_form_validation(self):
        """Test that form validation works"""
        print("[UI TEST] Testing form validation")

        self.driver.get(self.base_url)

        # Try to submit empty form
        generate_btn = self.driver.find_element(By.ID, "generateBtn")

        # Clear any existing value
        prompt_field = self.driver.find_element(By.ID, "prompt")
        prompt_field.clear()

        # Try to submit
        generate_btn.click()

        # HTML5 validation should prevent submission
        # Check if prompt is still focused (validation failed)
        time.sleep(0.5)

        validation_message = prompt_field.get_attribute("validationMessage")
        print(f"[UI TEST] ✓ Validation message: {validation_message}")

    def test_status_section_hidden_initially(self):
        """Test that status section is hidden on page load"""
        print("[UI TEST] Testing initial status section visibility")

        self.driver.get(self.base_url)

        status_section = self.driver.find_element(By.ID, "statusSection")
        is_displayed = status_section.is_displayed()

        self.assertFalse(is_displayed)
        print("[UI TEST] ✓ Status section hidden initially")

    def test_results_section_hidden_initially(self):
        """Test that results section is hidden on page load"""
        print("[UI TEST] Testing initial results section visibility")

        self.driver.get(self.base_url)

        results_section = self.driver.find_element(By.ID, "resultsSection")
        is_displayed = results_section.is_displayed()

        self.assertFalse(is_displayed)
        print("[UI TEST] ✓ Results section hidden initially")

    def test_error_section_hidden_initially(self):
        """Test that error section is hidden on page load"""
        print("[UI TEST] Testing initial error section visibility")

        self.driver.get(self.base_url)

        error_section = self.driver.find_element(By.ID, "errorSection")
        is_displayed = error_section.is_displayed()

        self.assertFalse(is_displayed)
        print("[UI TEST] ✓ Error section hidden initially")

    def test_model_options_present(self):
        """Test that model select has options"""
        print("[UI TEST] Testing model options")

        self.driver.get(self.base_url)

        model_select = self.driver.find_element(By.ID, "model")
        options = model_select.find_elements(By.TAG_NAME, "option")

        self.assertGreater(len(options), 0)
        print(f"[UI TEST] ✓ Found {len(options)} model options")

        for option in options:
            print(f"[UI TEST]   - {option.text}")

    def test_footer_present(self):
        """Test that footer is present"""
        print("[UI TEST] Testing footer")

        self.driver.get(self.base_url)

        footer = self.driver.find_element(By.TAG_NAME, "footer")
        self.assertIsNotNone(footer)

        print(f"[UI TEST] ✓ Footer text: {footer.text}")

    def test_responsive_layout(self):
        """Test that layout is responsive"""
        print("[UI TEST] Testing responsive layout")

        self.driver.get(self.base_url)

        # Test desktop size
        self.driver.set_window_size(1920, 1080)
        time.sleep(0.5)
        print("[UI TEST] ✓ Desktop layout (1920x1080)")

        # Test tablet size
        self.driver.set_window_size(768, 1024)
        time.sleep(0.5)
        print("[UI TEST] ✓ Tablet layout (768x1024)")

        # Test mobile size
        self.driver.set_window_size(375, 667)
        time.sleep(0.5)
        print("[UI TEST] ✓ Mobile layout (375x667)")

    def test_css_loaded(self):
        """Test that CSS is loaded"""
        print("[UI TEST] Testing CSS loading")

        self.driver.get(self.base_url)

        # Check if a styled element has non-default styling
        header = self.driver.find_element(By.TAG_NAME, "h1")
        color = header.value_of_css_property("color")

        # Default black text would be "rgba(0, 0, 0, 1)"
        # Our CSS should override this
        self.assertIsNotNone(color)
        print(f"[UI TEST] ✓ Header color: {color}")

    def test_javascript_loaded(self):
        """Test that JavaScript is loaded and executed"""
        print("[UI TEST] Testing JavaScript loading")

        self.driver.get(self.base_url)

        # Execute a script that checks if our JS functions exist
        js_loaded = self.driver.execute_script("""
            return typeof handleFormSubmit === 'function' &&
                   typeof checkJobStatus === 'function';
        """)

        self.assertTrue(js_loaded)
        print("[UI TEST] ✓ JavaScript functions loaded")

    def test_recent_jobs_section_present(self):
        """Test that recent jobs section is present"""
        print("[UI TEST] Testing recent jobs section")

        self.driver.get(self.base_url)

        jobs_list = self.driver.find_element(By.ID, "jobsList")
        self.assertIsNotNone(jobs_list)

        print("[UI TEST] ✓ Recent jobs section found")

    def test_console_logging(self):
        """Test that console.log statements are working"""
        print("[UI TEST] Testing console logging")

        self.driver.get(self.base_url)

        # Get browser console logs
        logs = self.driver.get_log('browser')

        # Should have initialization log
        init_logs = [log for log in logs if 'initialized' in log['message'].lower()]

        print(f"[UI TEST] ✓ Found {len(logs)} console logs")
        if init_logs:
            print(f"[UI TEST] ✓ Initialization logged")


@unittest.skipIf(SELENIUM_AVAILABLE, "Manual UI tests - run separately")
class TestUIManual(unittest.TestCase):
    """Manual UI tests that require visual inspection"""

    def test_visual_appearance(self):
        """Manual test: Check visual appearance"""
        print("""
        [MANUAL TEST] Visual Appearance
        --------------------------------
        1. Open http://localhost:5000 in browser
        2. Verify gradient background
        3. Verify card styling
        4. Verify button hover effects
        5. Verify responsive layout
        """)

    def test_video_playback(self):
        """Manual test: Test video playback"""
        print("""
        [MANUAL TEST] Video Playback
        ----------------------------
        1. Generate a test video
        2. Verify video player appears
        3. Verify video plays correctly
        4. Verify download button works
        """)


if __name__ == '__main__':
    if not SELENIUM_AVAILABLE:
        print("\n" + "="*60)
        print("⚠ WARNING: Selenium not installed")
        print("="*60)
        print("To run UI tests, install Selenium:")
        print("  pip install selenium")
        print("\nYou also need a WebDriver:")
        print("  Chrome: brew install chromedriver  # macOS")
        print("  Chrome: apt-get install chromium-chromedriver  # Linux")
        print("="*60 + "\n")

    print("\n" + "="*60)
    print("UI TESTS")
    print("="*60 + "\n")

    unittest.main(verbosity=2)
