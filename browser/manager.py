import base64
from playwright.sync_api import sync_playwright
import os

class BrowserManager:
    def __init__(self, headless=False):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.page = None
        
        # Load grounding script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(current_dir, 'grounding.js'), 'r') as f:
            self.grounding_script = f.read()

    def start(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.page = self.browser.new_page()
        # Set a reasonable viewport
        self.page.set_viewport_size({"width": 1280, "height": 720})

    def stop(self):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def navigate(self, url):
        self.page.goto(url)
        self.page.wait_for_load_state('networkidle')

    def interact(self, action_type, element_id, value=None):
        """
        Executes an action on an element by its ID.
        Uses the cached items to find the selector and tag type.
        """
        # 1. Find the element in the current state
        # We need to re-evaluate the map or store it. 
        # For simplicity, we'll assume the agent passes the ID and we look it up 
        # from the LAST captured state. 
        # NOTE: In a real app, we might want to re-verify the element exists.
        
        # We need to store the last items to look up the ID
        if not hasattr(self, 'last_items'):
            raise ValueError("No items found. Capture state first.")
            
        target = next((item for item in self.last_items if item['id'] == element_id), None)
        if not target:
            raise ValueError(f"Element with ID {element_id} not found.")
            
        selector = target['selector']
        tag = target['tag']
        
        print(f"Interacting with ID {element_id} ({tag}): {action_type}")

        # 2. Smart Logic based on Tag/Type
        if action_type == "click":
            self.page.click(selector)
        
        elif action_type == "type":
            self.page.fill(selector, value)
            
        elif action_type == "submit":
            self.page.press(selector, "Enter")
            
        self.page.wait_for_load_state('networkidle')

    def capture_state(self):
        """
        Injects marks, takes a screenshot, and returns the state.
        """
        # 1. Inject Grounding Script
        items = self.page.evaluate(self.grounding_script)
        self.last_items = items # Cache for interaction lookup
        
        # 2. Take Screenshot
        screenshot_bytes = self.page.screenshot(full_page=False)
        screenshot_b64 = base64.b64encode(screenshot_bytes).decode('utf-8')

        return {
            "screenshot": screenshot_b64,
            "items": items
        }
