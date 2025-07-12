import time
import logging
from typing import Dict, Any, Optional, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import re

logger = logging.getLogger(__name__)

class BrowserAutomationService:
    """Service for browser automation and control"""
    
    def __init__(self):
        self.driver = None
        self.current_url = None
        
    def start_browser(self, headless: bool = False) -> bool:
        """Start a new browser session"""
        try:
            chrome_options = Options()
            if headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            # Auto-download and setup ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            logger.info("Browser started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            return False
    
    def navigate_to(self, url: str) -> bool:
        """Navigate to a specific URL"""
        try:
            if not self.driver:
                return False
                
            self.driver.get(url)
            self.current_url = url
            logger.info(f"Navigated to: {url}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {e}")
            return False
    
    def join_meeting(self, meeting_url: str, meeting_id: str = None, password: str = None) -> Dict[str, Any]:
        """Join a video meeting (supports Zoom, Google Meet, Teams)"""
        try:
            if not self.driver:
                return {"success": False, "error": "Browser not started"}
            
            # Navigate to meeting URL
            if not self.navigate_to(meeting_url):
                return {"success": False, "error": "Failed to navigate to meeting"}
            
            # Wait for page to load
            time.sleep(3)
            
            # Handle different meeting platforms
            if "zoom.us" in meeting_url:
                return self._handle_zoom_meeting(meeting_id, password)
            elif "meet.google.com" in meeting_url:
                return self._handle_google_meet(meeting_id, password)
            elif "teams.microsoft.com" in meeting_url:
                return self._handle_teams_meeting(meeting_id, password)
            else:
                return {"success": True, "message": f"Joined meeting at {meeting_url}"}
                
        except Exception as e:
            logger.error(f"Failed to join meeting: {e}")
            return {"success": False, "error": str(e)}
    
    def _handle_zoom_meeting(self, meeting_id: str, password: str) -> Dict[str, Any]:
        """Handle Zoom meeting join process"""
        try:
            # Wait for join button and click it
            join_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='join-button']"))
            )
            join_button.click()
            
            # Handle meeting ID if provided
            if meeting_id:
                id_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='Meeting ID']"))
                )
                id_input.send_keys(meeting_id)
            
            # Handle password if provided
            if password:
                password_input = self.driver.find_element(By.CSS_SELECTOR, "input[placeholder*='Password']")
                password_input.send_keys(password)
            
            # Click join
            join_btn = self.driver.find_element(By.CSS_SELECTOR, "button[data-testid='join-button']")
            join_btn.click()
            
            return {"success": True, "message": "Joined Zoom meeting successfully"}
            
        except Exception as e:
            return {"success": False, "error": f"Zoom join failed: {str(e)}"}
    
    def _handle_google_meet(self, meeting_id: str, password: str) -> Dict[str, Any]:
        """Handle Google Meet join process"""
        try:
            # Wait for join button
            join_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-mdc-dialog-action='join']"))
            )
            join_button.click()
            
            # Handle camera/mic setup
            camera_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-mdc-dialog-action='camera']"))
            )
            camera_button.click()
            
            return {"success": True, "message": "Joined Google Meet successfully"}
            
        except Exception as e:
            return {"success": False, "error": f"Google Meet join failed: {str(e)}"}
    
    def _handle_teams_meeting(self, meeting_id: str, password: str) -> Dict[str, Any]:
        """Handle Microsoft Teams join process"""
        try:
            # Wait for join button
            join_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='join-button']"))
            )
            join_button.click()
            
            return {"success": True, "message": "Joined Teams meeting successfully"}
            
        except Exception as e:
            return {"success": False, "error": f"Teams join failed: {str(e)}"}
    
    def click_element(self, selector: str, selector_type: str = "css") -> Dict[str, Any]:
        """Click on an element using various selector types"""
        try:
            if not self.driver:
                return {"success": False, "error": "Browser not started"}
            
            # Map selector types to Selenium By
            by_map = {
                "css": By.CSS_SELECTOR,
                "xpath": By.XPATH,
                "id": By.ID,
                "class": By.CLASS_NAME,
                "name": By.NAME,
                "tag": By.TAG_NAME
            }
            
            by_type = by_map.get(selector_type.lower(), By.CSS_SELECTOR)
            
            # Wait for element and click
            element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((by_type, selector))
            )
            element.click()
            
            logger.info(f"Clicked element: {selector}")
            return {"success": True, "message": f"Clicked {selector}"}
            
        except Exception as e:
            logger.error(f"Failed to click element {selector}: {e}")
            return {"success": False, "error": str(e)}
    
    def scroll_page(self, direction: str = "down", amount: int = 500) -> Dict[str, Any]:
        """Scroll the page in specified direction"""
        try:
            if not self.driver:
                return {"success": False, "error": "Browser not started"}
            
            if direction.lower() == "down":
                self.driver.execute_script(f"window.scrollBy(0, {amount});")
            elif direction.lower() == "up":
                self.driver.execute_script(f"window.scrollBy(0, -{amount});")
            elif direction.lower() == "left":
                self.driver.execute_script(f"window.scrollBy(-{amount}, 0);")
            elif direction.lower() == "right":
                self.driver.execute_script(f"window.scrollBy({amount}, 0);")
            elif direction.lower() == "top":
                self.driver.execute_script("window.scrollTo(0, 0);")
            elif direction.lower() == "bottom":
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            logger.info(f"Scrolled {direction} by {amount}px")
            return {"success": True, "message": f"Scrolled {direction}"}
            
        except Exception as e:
            logger.error(f"Failed to scroll: {e}")
            return {"success": False, "error": str(e)}
    
    def type_text(self, text: str, selector: str = None) -> Dict[str, Any]:
        """Type text into an element or active element"""
        try:
            if not self.driver:
                return {"success": False, "error": "Browser not started"}
            
            if selector:
                element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                element.clear()
                element.send_keys(text)
            else:
                # Type into active element
                actions = ActionChains(self.driver)
                actions.send_keys(text)
                actions.perform()
            
            logger.info(f"Typed text: {text[:50]}...")
            return {"success": True, "message": f"Typed text: {text[:50]}..."}
            
        except Exception as e:
            logger.error(f"Failed to type text: {e}")
            return {"success": False, "error": str(e)}
    
    def take_screenshot(self, filename: str = None) -> Dict[str, Any]:
        """Take a screenshot of the current page"""
        try:
            if not self.driver:
                return {"success": False, "error": "Browser not started"}
            
            if not filename:
                filename = f"screenshot_{int(time.time())}.png"
            
            self.driver.save_screenshot(filename)
            logger.info(f"Screenshot saved: {filename}")
            return {"success": True, "filename": filename}
            
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return {"success": False, "error": str(e)}
    
    def get_page_info(self) -> Dict[str, Any]:
        """Get current page information"""
        try:
            if not self.driver:
                return {"success": False, "error": "Browser not started"}
            
            info = {
                "url": self.driver.current_url,
                "title": self.driver.title,
                "window_size": self.driver.get_window_size(),
                "scroll_position": self.driver.execute_script("return [window.pageXOffset, window.pageYOffset];")
            }
            
            return {"success": True, "info": info}
            
        except Exception as e:
            logger.error(f"Failed to get page info: {e}")
            return {"success": False, "error": str(e)}
    
    def close_browser(self) -> bool:
        """Close the browser session"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                logger.info("Browser closed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to close browser: {e}")
            return False

# Global browser instance
browser_service = BrowserAutomationService() 