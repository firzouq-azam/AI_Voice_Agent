import time
import logging
from typing import Tuple, Dict, Any, Optional
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import DemoSession, CommandLog
from .browser_automation import browser_service

logger = logging.getLogger(__name__)

class SessionService:
    """Service for managing demo sessions"""
    
    @staticmethod
    def create_session() -> DemoSession:
        """Create a new demo session"""
        try:
            session = DemoSession.objects.create()
            logger.info(f"Created new session: {session.session_id}")
            return session
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise
    
    @staticmethod
    def get_session(session_id: str) -> Optional[DemoSession]:
        """Get a session by ID"""
        try:
            return DemoSession.objects.get(session_id=session_id)
        except DemoSession.DoesNotExist:
            logger.warning(f"Session not found: {session_id}")
            return None
    
    @staticmethod
    def end_session(session_id: str) -> bool:
        """End a session"""
        session = SessionService.get_session(session_id)
        if session and session.is_active:
            session.end_session()
            logger.info(f"Ended session: {session_id}")
            return True
        return False

class CommandService:
    """Service for handling voice commands"""
    
    @staticmethod
    def process_command(session_id: str, command: str) -> Tuple[Dict[str, Any], int]:
        """Process a voice command and return response"""
        start_time = time.time()
        
        try:
            # Validate session
            session = SessionService.get_session(session_id)
            if not session:
                return {"error": "Session not found"}, 404
            
            if not session.is_active:
                return {"error": "Session has ended"}, 400
            
            # Validate command
            if not command or not command.strip():
                return {"error": "Command cannot be empty"}, 400
            
            # Process command based on type
            if command.lower().startswith("ai:"):
                response, is_ai = CommandService._handle_ai_command(command)
            elif command.lower().startswith("browser:"):
                response, is_ai = CommandService._handle_browser_command(command)
            else:
                response, is_ai = CommandService._handle_dummy_command(command)
            
            # Calculate processing time
            processing_time = int((time.time() - start_time) * 1000)
            
            # Log the command
            CommandLog.objects.create(
                session=session,
                command_text=command.strip(),
                response=response,
                is_ai_response=is_ai,
                processing_time_ms=processing_time
            )
            
            logger.info(f"Processed command for session {session_id}: {command[:50]}...")
            return {"response": response}, 200
            
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            return {"error": "Internal server error"}, 500
    
    @staticmethod
    def _handle_ai_command(command: str) -> Tuple[str, bool]:
        """Handle AI-powered commands"""
        try:
            import openai
            
            # Get API key from settings
            api_key = getattr(settings, 'OPENAI_API_KEY', None)
            if not api_key:
                return "AI service not configured", False
            
            openai.api_key = api_key
            prompt = command[3:].strip()  # Remove 'ai:' prefix
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip(), True
            
        except Exception as e:
            logger.error(f"AI command processing error: {e}")
            return f"AI service error: {str(e)}", False
    
    @staticmethod
    def _handle_browser_command(command: str) -> Tuple[str, bool]:
        """Handle browser automation commands"""
        try:
            # Remove 'browser:' prefix
            browser_cmd = command[8:].strip().lower()
            
            # Parse browser commands
            if "join meeting" in browser_cmd or "join call" in browser_cmd:
                return CommandService._handle_meeting_join(browser_cmd)
            elif "click" in browser_cmd:
                return CommandService._handle_click_command(browser_cmd)
            elif "scroll" in browser_cmd:
                return CommandService._handle_scroll_command(browser_cmd)
            elif "type" in browser_cmd or "write" in browser_cmd:
                return CommandService._handle_type_command(browser_cmd)
            elif "screenshot" in browser_cmd or "capture" in browser_cmd:
                return CommandService._handle_screenshot_command(browser_cmd)
            elif "navigate" in browser_cmd or "go to" in browser_cmd:
                return CommandService._handle_navigate_command(browser_cmd)
            elif "start browser" in browser_cmd:
                return CommandService._handle_start_browser(browser_cmd)
            elif "close browser" in browser_cmd:
                return CommandService._handle_close_browser(browser_cmd)
            else:
                return "I don't understand that browser command. Try: join meeting, click, scroll, type, screenshot, navigate", False
                
        except Exception as e:
            logger.error(f"Browser command processing error: {e}")
            return f"Browser automation error: {str(e)}", False
    
    @staticmethod
    def _handle_meeting_join(command: str) -> Tuple[str, bool]:
        """Handle meeting join commands"""
        try:
            # Extract meeting URL from command
            # Example: "browser: join meeting https://zoom.us/j/123456789"
            import re
            url_match = re.search(r'https?://[^\s]+', command)
            if not url_match:
                return "Please provide a meeting URL. Example: browser: join meeting https://zoom.us/j/123456789", False
            
            meeting_url = url_match.group()
            
            # Start browser if not already started
            if not browser_service.driver:
                if not browser_service.start_browser():
                    return "Failed to start browser", False
            
            # Join the meeting
            result = browser_service.join_meeting(meeting_url)
            
            if result["success"]:
                return f"Successfully joined meeting at {meeting_url}", False
            else:
                return f"Failed to join meeting: {result.get('error', 'Unknown error')}", False
                
        except Exception as e:
            return f"Meeting join error: {str(e)}", False
    
    @staticmethod
    def _handle_click_command(command: str) -> Tuple[str, bool]:
        """Handle click commands"""
        try:
            # Extract selector from command
            # Example: "browser: click button.login-btn"
            import re
            selector_match = re.search(r'click\s+([^\s]+)', command)
            if not selector_match:
                return "Please specify what to click. Example: browser: click button.login-btn", False
            
            selector = selector_match.group(1)
            
            if not browser_service.driver:
                return "Browser not started. Use 'browser: start browser' first", False
            
            result = browser_service.click_element(selector)
            
            if result["success"]:
                return f"Clicked {selector}", False
            else:
                return f"Failed to click: {result.get('error', 'Unknown error')}", False
                
        except Exception as e:
            return f"Click error: {str(e)}", False
    
    @staticmethod
    def _handle_scroll_command(command: str) -> Tuple[str, bool]:
        """Handle scroll commands"""
        try:
            # Parse scroll direction and amount
            direction = "down"
            amount = 500
            
            if "up" in command:
                direction = "up"
            elif "left" in command:
                direction = "left"
            elif "right" in command:
                direction = "right"
            elif "top" in command:
                direction = "top"
            elif "bottom" in command:
                direction = "bottom"
            
            # Extract amount if specified
            import re
            amount_match = re.search(r'(\d+)\s*pixels?', command)
            if amount_match:
                amount = int(amount_match.group(1))
            
            if not browser_service.driver:
                return "Browser not started. Use 'browser: start browser' first", False
            
            result = browser_service.scroll_page(direction, amount)
            
            if result["success"]:
                return f"Scrolled {direction} by {amount} pixels", False
            else:
                return f"Failed to scroll: {result.get('error', 'Unknown error')}", False
                
        except Exception as e:
            return f"Scroll error: {str(e)}", False
    
    @staticmethod
    def _handle_type_command(command: str) -> Tuple[str, bool]:
        """Handle type commands"""
        try:
            # Extract text to type
            # Example: "browser: type Hello World"
            text_start = command.find("type") + 4
            if text_start >= len(command):
                return "Please specify text to type. Example: browser: type Hello World", False
            
            text = command[text_start:].strip()
            
            if not browser_service.driver:
                return "Browser not started. Use 'browser: start browser' first", False
            
            result = browser_service.type_text(text)
            
            if result["success"]:
                return f"Typed: {text}", False
            else:
                return f"Failed to type: {result.get('error', 'Unknown error')}", False
                
        except Exception as e:
            return f"Type error: {str(e)}", False
    
    @staticmethod
    def _handle_screenshot_command(command: str) -> Tuple[str, bool]:
        """Handle screenshot commands"""
        try:
            if not browser_service.driver:
                return "Browser not started. Use 'browser: start browser' first", False
            
            result = browser_service.take_screenshot()
            
            if result["success"]:
                return f"Screenshot saved as {result.get('filename', 'screenshot.png')}", False
            else:
                return f"Failed to take screenshot: {result.get('error', 'Unknown error')}", False
                
        except Exception as e:
            return f"Screenshot error: {str(e)}", False
    
    @staticmethod
    def _handle_navigate_command(command: str) -> Tuple[str, bool]:
        """Handle navigation commands"""
        try:
            # Extract URL from command
            import re
            url_match = re.search(r'https?://[^\s]+', command)
            if not url_match:
                return "Please provide a URL. Example: browser: navigate to https://google.com", False
            
            url = url_match.group()
            
            if not browser_service.driver:
                if not browser_service.start_browser():
                    return "Failed to start browser", False
            
            result = browser_service.navigate_to(url)
            
            if result:
                return f"Navigated to {url}", False
            else:
                return f"Failed to navigate to {url}", False
                
        except Exception as e:
            return f"Navigation error: {str(e)}", False
    
    @staticmethod
    def _handle_start_browser(command: str) -> Tuple[str, bool]:
        """Handle browser start command"""
        try:
            if browser_service.driver:
                return "Browser is already running", False
            
            headless = "headless" in command
            result = browser_service.start_browser(headless)
            
            if result:
                return "Browser started successfully", False
            else:
                return "Failed to start browser", False
                
        except Exception as e:
            return f"Browser start error: {str(e)}", False
    
    @staticmethod
    def _handle_close_browser(command: str) -> Tuple[str, bool]:
        """Handle browser close command"""
        try:
            result = browser_service.close_browser()
            
            if result:
                return "Browser closed successfully", False
            else:
                return "Failed to close browser", False
                
        except Exception as e:
            return f"Browser close error: {str(e)}", False
    
    @staticmethod
    def _handle_dummy_command(command: str) -> Tuple[str, bool]:
        """Handle dummy commands for testing"""
        command_lower = command.lower()
        
        if "hello" in command_lower:
            return "Hello! How can I assist you today?", False
        elif "time" in command_lower:
            current_time = timezone.now().strftime('%H:%M:%S')
            return f"The current time is {current_time}", False
        elif "help" in command_lower:
            return "I can help you with:\n- Basic commands: hello, time, help\n- AI responses: ai: your question\n- Browser control: browser: join meeting, click, scroll, type, screenshot", False
        else:
            return "I'm not sure how to respond to that yet. Try saying 'help' for available commands.", False

class TranscriptService:
    """Service for managing session transcripts"""
    
    @staticmethod
    def get_session_transcript(session_id: str) -> Tuple[Dict[str, Any], int]:
        """Get full transcript for a session"""
        try:
            session = SessionService.get_session(session_id)
            if not session:
                return {"error": "Session not found"}, 404
            
            commands = session.commands.all()
            
            transcript_data = {
                "session_id": str(session.session_id),
                "started_at": session.started_at,
                "ended_at": session.ended_at,
                "is_active": session.is_active,
                "total_commands": commands.count(),
                "commands": []
            }
            
            for cmd in commands:
                transcript_data["commands"].append({
                    "timestamp": cmd.timestamp,
                    "command": cmd.command_text,
                    "response": cmd.response,
                    "is_ai_response": cmd.is_ai_response,
                    "processing_time_ms": cmd.processing_time_ms
                })
            
            return transcript_data, 200
            
        except Exception as e:
            logger.error(f"Error getting transcript: {e}")
            return {"error": "Internal server error"}, 500 