"""Telegram bot plugin."""
import logging
import os
import json
from typing import Dict, Any, Optional, Callable, List
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from dotenv import load_dotenv, set_key
from pathlib import Path

from common.config import get_env_var
from plugins import Plugin, Event, EventType
from database.models import PlatformProfile
from database.operations.messages import update_message_status
from .settings import TelegramSettings, MessageMode
from .message_handler import MessageFormatter

logger = logging.getLogger(__name__)

class TelegramPlugin(Plugin):
    """Telegram plugin using Telethon client."""
    
    def __init__(self):
        """Initialize the Telegram plugin."""
        self.settings = TelegramSettings.from_env()
        self.formatter = MessageFormatter()
        self.ignored_bots: Dict[str, Dict[str, str]] = {}
        
        # Initialize client
        self.client = TelegramClient(
            StringSession(self.settings.session_string),
            self.settings.api_id,
            self.settings.api_hash
        )
        
        # Event handlers
        self._event_handlers: Dict[EventType, set[Callable[[Event], None]]] = {
            event_type: set() for event_type in EventType
        }
    
    def _get_ignore_list_path(self) -> Path:
        """Get the path to the ignore list file."""
        return Path(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "telegram_ignore_list.json"))
    
    def _load_ignore_list(self) -> None:
        """Load the ignore list from file."""
        path = self._get_ignore_list_path()
        if not path.exists():
            logger.info("No ignore list file found")
            return
            
        try:
            with open(path, 'r') as f:
                self.ignored_bots = json.load(f)
            logger.info(f"Loaded {len(self.ignored_bots)} ignored bots: {self.ignored_bots}")
        except json.JSONDecodeError:
            logger.error("Failed to parse ignore list file")
            self.ignored_bots = {}
    
    def reload_ignore_list(self) -> None:
        """Reload the ignore list from file."""
        logger.debug("Reloading ignore list...")
        self._load_ignore_list()
    
    def is_bot_ignored(self, bot_id: str, username: Optional[str] = None) -> bool:
        """Check if a bot is in the ignore list.
        
        Args:
            bot_id: The bot ID to check
            username: Optional bot username to check
            
        Returns:
            bool: True if the bot is ignored, False otherwise
        """
        # Reload the ignore list to get any changes
        self.reload_ignore_list()
        
        # Check by ID
        if str(bot_id) in self.ignored_bots:
            logger.info(f"Bot {bot_id} (@{username}) is ignored by ID")
            return True
            
        # Check by username
        if username:
            # Remove @ if present and convert to lowercase
            username = username[1:] if username.startswith('@') else username
            username = username.lower()
            
            for data in self.ignored_bots.values():
                if data.get("username", "").lower() == username:
                    logger.info(f"Bot {bot_id} (@{username}) is ignored by username")
                    return True
        
        logger.debug(f"Bot {bot_id} (@{username}) is not ignored")
        return False
    
    def get_name(self) -> str:
        """Get the plugin's name."""
        return "telegram"
    
    def get_platform(self) -> str:
        """Get the platform name this plugin handles."""
        return "telegram"
    
    def get_message_handler(self) -> Callable:
        """Get the message handler for this platform."""
        return self._handle_response
    
    async def _handle_response(self, response: str, profile: PlatformProfile, message_id: int) -> None:
        """Handle sending a response to a Telegram user.
        
        Args:
            response: The response message to send
            profile: The platform profile of the recipient
            message_id: The ID of the message being responded to
        """
        try:
            # Format response for Telegram
            formatted = self.formatter.format_response(response)
            
            # Convert platform_user_id to integer for Telegram
            try:
                telegram_user_id = int(profile.platform_user_id)
            except ValueError:
                logger.error(f"Invalid Telegram user ID format: {profile.platform_user_id}")
                await update_message_status(
                    message_id=message_id,
                    status="failed",
                    response=f"Invalid Telegram user ID format: {profile.platform_user_id}"
                )
                return
            
            # Send message with typing indicator
            async with self.client.action(telegram_user_id, 'typing'):
                await self.client.send_message(
                    telegram_user_id,
                    formatted
                )
                logger.info(f"Response sent to user {profile.username} ({telegram_user_id})")
                
                # Update message status to success
                await update_message_status(
                    message_id=message_id,
                    status="success",
                    response=formatted
                )
                
        except Exception as e:
            error_msg = f"Failed to send response to {profile.platform_user_id}: {str(e)}"
            logger.error(error_msg)
            # Update message status to failed
            await update_message_status(
                message_id=message_id,
                status="failed",
                response=error_msg
            )
    
    def get_settings(self) -> Optional[Dict[str, Any]]:
        """Get the plugin's settings."""
        return self.settings.to_dict()
    
    def validate_settings(self, settings: Dict[str, Any]) -> bool:
        """Validate plugin settings."""
        try:
            TelegramSettings.from_dict(settings)
            return True
        except (KeyError, ValueError):
            return False
    
    def register_event_handler(self, event_type: EventType, handler: Callable[[Event], None]) -> None:
        """Register an event handler."""
        self._event_handlers[event_type].add(handler)
    
    def emit_event(self, event: Event) -> None:
        """Emit an event to registered handlers."""
        handlers = self._event_handlers[event.type]
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Error in event handler for {event.type}: {e}")
    
    async def start(self) -> None:
        """Start the Telegram client."""
        if not self.client:
            logger.error("❌ Telegram client not initialized")
            return
        
        try:
            logger.info("🔄 Starting Telegram client...")
            await self.client.start()
            
            if not await self.client.is_user_authorized():
                logger.error("❌ Telegram client not authorized")
                return
            
            # Load ignore list
            self._load_ignore_list()
            
            # Save the session string if it's different from what we have
            if self.settings.auto_save_session:
                new_session_string = self.client.session.save()
                if new_session_string != self.settings.session_string:
                    logger.info("💾 Saving new Telegram session string...")
                    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
                    set_key(env_path, "TELEGRAM_SESSION_STRING", new_session_string)
                    self.settings.session_string = new_session_string
            
            logger.info("✅ Telegram client started successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to start Telegram client: {str(e)}")
            raise
    
    async def stop(self) -> None:
        """Stop the Telegram client."""
        if self.client:
            await self.client.disconnect()
    
    def add_message_handler(self, callback: Callable, event: events.NewMessage) -> None:
        """Add a message handler to the client.
        
        Args:
            callback: The callback function to handle the message
            event: The event to handle
        """
        if self.client:
            self.client.add_event_handler(callback, event)
    
    def set_message_mode(self, mode: MessageMode) -> None:
        """Set the message handling mode.
        
        Args:
            mode: The message mode
        """
        self.settings.message_mode = mode
        logger.info(f"🔵 Message processing mode changed to: {mode.name}") 