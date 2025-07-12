import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.core.exceptions import ValidationError
from .services import SessionService, CommandService, TranscriptService
from .serializers import (
    DemoSessionSerializer, 
    CommandRequestSerializer, 
    TranscriptSerializer
)

logger = logging.getLogger(__name__)

class StartSessionView(APIView):
    """API endpoint to start a new demo session"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Create a new demo session"""
        try:
            session = SessionService.create_session()
            serializer = DemoSessionSerializer(session)
            
            logger.info(f"Started new session: {session.session_id}")
            return Response(
                {
                    "message": "Session started successfully",
                    "data": serializer.data
                }, 
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            logger.error(f"Failed to start session: {e}")
            return Response(
                {"error": "Failed to start session"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class SendCommandView(APIView):
    """API endpoint to send voice commands"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Process a voice command"""
        try:
            # Validate request data
            serializer = CommandRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {"error": "Invalid request data", "details": serializer.errors}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            session_id = serializer.validated_data['session_id']
            command = serializer.validated_data['command']
            
            # Process command using service
            result, status_code = CommandService.process_command(str(session_id), command)
            
            return Response(result, status=status_code)
            
        except ValidationError as e:
            logger.warning(f"Validation error in command: {e}")
            return Response(
                {"error": "Invalid command format"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error in SendCommandView: {e}")
            return Response(
                {"error": "Internal server error"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class TranscriptView(APIView):
    """API endpoint to get session transcript"""
    permission_classes = [AllowAny]
    
    def get(self, request, session_id):
        """Get full transcript for a session"""
        try:
            result, status_code = TranscriptService.get_session_transcript(str(session_id))
            return Response(result, status=status_code)
            
        except Exception as e:
            logger.error(f"Error getting transcript: {e}")
            return Response(
                {"error": "Internal server error"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class EndSessionView(APIView):
    """API endpoint to end a demo session"""
    permission_classes = [AllowAny]
    
    def post(self, request, session_id):
        """End a demo session"""
        try:
            success = SessionService.end_session(str(session_id))
            
            if success:
                return Response(
                    {"message": "Session ended successfully"}, 
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"error": "Session not found or already ended"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
                
        except Exception as e:
            logger.error(f"Error ending session: {e}")
            return Response(
                {"error": "Internal server error"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
