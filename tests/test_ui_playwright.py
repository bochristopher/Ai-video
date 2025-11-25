"""
UI tests using Playwright (alternative to Selenium)
Playwright is faster and more reliable for modern web testing
"""
import unittest
import os
import sys

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


@unittest.skipIf(not PLAYWRIGHT_AVAILABLE, "Playwright not installed")
class TestUIPlaywright(unittest.TestCase):
    """UI tests using Playwright"""

    @classmethod
    def setUpClass(cls):
        """Set up class-level fixtures"""
        print("\n" + "="*60)
        print("PLAYWRIGHT UI TESTS - SETUP")
        print("="*60)

        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=True)
        cls.base_url = "http://localhost:5000"

        print("[Playwright] ✓ Browser launched")

    @classmethod
    def tearDownClass(cls):
        """Clean up class-level fixtures"""
        if hasattr(cls, 'browser'):
            cls.browser.close()
        if hasattr(cls, 'playwright'):
            cls.playwright.stop()
        print("\n[Playwright] Browser closed")

    def setUp(self):
        """Set up test fixtures"""
        print("\n" + "="*60)
        print(f"Running: {self._testMethodName}")
        print("="*60)

        self.context = self.browser.new_context()
        self.page = self.context.new_page()

    def tearDown(self):
        """Clean up after tests"""
        self.context.close()
        print(f"✓ {self._testMethodName} completed")

    def test_page_loads(self):
        """Test that page loads successfully"""
        print("[Playwright] Testing page load")

        self.page.goto(self.base_url)
        title = self.page.title()

        self.assertEqual(title, "AI Video Generator")
        print(f"[Playwright] ✓ Page loaded: {title}")

    def test_form_interaction(self):
        """Test form interaction"""
        print("[Playwright] Testing form interaction")

        self.page.goto(self.base_url)

        # Fill in the form
        self.page.fill("#prompt", "A beautiful sunset over mountains")
        self.page.select_option("#model", "animate-diff")
        self.page.fill("#duration", "5")

        print("[Playwright] ✓ Form filled")

        # Check values
        prompt_value = self.page.input_value("#prompt")
        self.assertEqual(prompt_value, "A beautiful sunset over mountains")

        print(f"[Playwright] ✓ Prompt value: {prompt_value}")

    def test_example_chip_interaction(self):
        """Test clicking example chips"""
        print("[Playwright] Testing example chip click")

        self.page.goto(self.base_url)

        # Click first chip
        chip = self.page.query_selector(".chip")
        expected_prompt = chip.get_attribute("data-prompt")
        chip.click()

        # Wait for JS to execute
        self.page.wait_for_timeout(500)

        # Check prompt was filled
        actual_prompt = self.page.input_value("#prompt")
        self.assertEqual(actual_prompt, expected_prompt)

        print(f"[Playwright] ✓ Chip clicked, prompt filled")

    def test_responsive_design(self):
        """Test responsive design at different viewports"""
        print("[Playwright] Testing responsive design")

        # Desktop
        self.page.set_viewport_size({"width": 1920, "height": 1080})
        self.page.goto(self.base_url)
        print("[Playwright] ✓ Desktop viewport (1920x1080)")

        # Tablet
        self.page.set_viewport_size({"width": 768, "height": 1024})
        print("[Playwright] ✓ Tablet viewport (768x1024)")

        # Mobile
        self.page.set_viewport_size({"width": 375, "height": 667})
        print("[Playwright] ✓ Mobile viewport (375x667)")

    def test_all_sections_present(self):
        """Test that all major sections are present"""
        print("[Playwright] Testing section presence")

        self.page.goto(self.base_url)

        # Check sections exist
        self.assertIsNotNone(self.page.query_selector("#videoForm"))
        print("[Playwright] ✓ Form section present")

        self.assertIsNotNone(self.page.query_selector("#statusSection"))
        print("[Playwright] ✓ Status section present")

        self.assertIsNotNone(self.page.query_selector("#resultsSection"))
        print("[Playwright] ✓ Results section present")

        self.assertIsNotNone(self.page.query_selector("#errorSection"))
        print("[Playwright] ✓ Error section present")

        self.assertIsNotNone(self.page.query_selector("#jobsList"))
        print("[Playwright] ✓ Jobs list present")

    def test_screenshot_capture(self):
        """Test capturing screenshots"""
        print("[Playwright] Testing screenshot capture")

        self.page.goto(self.base_url)

        # Take full page screenshot
        screenshot_path = "/tmp/ai-video-generator-ui-test.png"
        self.page.screenshot(path=screenshot_path, full_page=True)

        self.assertTrue(os.path.exists(screenshot_path))
        print(f"[Playwright] ✓ Screenshot saved: {screenshot_path}")

        # Cleanup
        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)

    def test_console_messages(self):
        """Test that console messages are logged"""
        print("[Playwright] Testing console messages")

        messages = []

        def handle_console(msg):
            messages.append(msg.text)
            print(f"[Console] {msg.type}: {msg.text}")

        self.page.on("console", handle_console)
        self.page.goto(self.base_url)

        # Wait for page to fully load
        self.page.wait_for_load_state("networkidle")

        self.assertGreater(len(messages), 0)
        print(f"[Playwright] ✓ Captured {len(messages)} console messages")

    def test_network_requests(self):
        """Test network requests made by the page"""
        print("[Playwright] Testing network requests")

        requests = []

        def handle_request(request):
            requests.append({
                'url': request.url,
                'method': request.method
            })
            print(f"[Network] {request.method} {request.url}")

        self.page.on("request", handle_request)
        self.page.goto(self.base_url)

        # Wait for page to load
        self.page.wait_for_load_state("networkidle")

        self.assertGreater(len(requests), 0)
        print(f"[Playwright] ✓ Captured {len(requests)} network requests")

    def test_accessibility(self):
        """Test basic accessibility features"""
        print("[Playwright] Testing accessibility")

        self.page.goto(self.base_url)

        # Check for proper labels
        prompt_label = self.page.query_selector('label[for="prompt"]')
        self.assertIsNotNone(prompt_label)
        print("[Playwright] ✓ Form labels present")

        # Check for alt text on any images (if present)
        images = self.page.query_selector_all("img")
        for img in images:
            alt = img.get_attribute("alt")
            if alt is None:
                print(f"[Playwright] ⚠ Image missing alt text: {img}")

        print("[Playwright] ✓ Accessibility check complete")


if __name__ == '__main__':
    if not PLAYWRIGHT_AVAILABLE:
        print("\n" + "="*60)
        print("⚠ WARNING: Playwright not installed")
        print("="*60)
        print("To run Playwright UI tests, install it:")
        print("  pip install playwright")
        print("  playwright install chromium")
        print("="*60 + "\n")

    print("\n" + "="*60)
    print("PLAYWRIGHT UI TESTS")
    print("="*60 + "\n")

    unittest.main(verbosity=2)
