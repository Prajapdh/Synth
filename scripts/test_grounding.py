import sys
import os
import base64

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from browser.manager import BrowserManager

def test_grounding():
    print("Initializing Browser...")
    browser = BrowserManager(headless=False) # Headless=False to see it happen
    browser.start()

    try:
        print("Navigating to demo site...")
        browser.navigate("https://saucedemo.com")

        print("Injecting Set of Marks...")
        state = browser.capture_state()

        items = state['items']
        print(f"Found {len(items)} interactive elements.")
        
        # Print first 5 items to verify mapping
        for item in items[:5]:
            print(f"ID: {item['id']} | Tag: {item['tag']} | Text: {item['text']} | Selector: {item['selector']}")

        # Save screenshot to verify visual tags
        print("Saving tagged screenshot...")
        with open("tagged_screenshot.png", "wb") as f:
            f.write(base64.b64decode(state['screenshot']))
        
        print("Test Passed! Check 'tagged_screenshot.png' to see the red boxes.")

    except Exception as e:
        print(f"Test Failed: {e}")
    finally:
        # Keep open for a moment if needed, or close
        # input("Press Enter to close...")
        browser.stop()

if __name__ == "__main__":
    test_grounding()
