from langchain_core.tools import tool
from browser.manager import BrowserManager

# Global browser instance (simplification for prototype)
# In a real app, this would be passed via context or dependency injection
browser = BrowserManager(headless=False)

@tool
def navigate(url: str):
    """Navigates the browser to the specified URL."""
    if not browser.browser:
        browser.start()
    browser.navigate(url)
    return f"Navigated to {url}"

@tool
def click_element(element_id: int):
    """Clicks on the element with the given numeric ID."""
    try:
        browser.interact("click", element_id)
        return f"Clicked element #{element_id}"
    except Exception as e:
        return f"Error clicking element #{element_id}: {str(e)}"

@tool
def type_text(element_id: int, text: str):
    """Types text into the element with the given numeric ID."""
    try:
        browser.interact("type", element_id, value=text)
        return f"Typed '{text}' into element #{element_id}"
    except Exception as e:
        return f"Error typing into element #{element_id}: {str(e)}"

@tool
def scroll():
    """Scrolls the page down."""
    try:
        browser.interact("scroll", 0) # ID 0 is ignored for scroll
        return "Scrolled down"
    except Exception as e:
        return f"Error scrolling: {str(e)}"

@tool
def done(result: str):
    """Call this when the goal is achieved."""
    return result

def get_tools():
    return [navigate, click_element, type_text, scroll, done]

def get_browser():
    return browser
