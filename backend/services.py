import time
import logging
from typing import Tuple, Dict, Any, Optional
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import DemoSession, CommandLog

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
    def _handle_dummy_command(command: str) -> Tuple[str, bool]:
        """Handle dummy commands for testing"""
        command_lower = command.lower()
        
        if "hello" in command_lower:
            return "Hello! How can I assist you today?", False
        elif "time" in command_lower:
            current_time = timezone.now().strftime('%H:%M:%S')
            return f"The current time is {current_time}", False
        elif "help" in command_lower:
            return "I can help you with basic commands. Try saying 'hello', 'time', or prefix with 'ai:' for AI responses.", False
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