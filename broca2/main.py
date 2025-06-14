"""Main application entry point."""
import asyncio
import sys
import logging
import os
import time
import json
from typing import Optional
from telethon import events
from dotenv import load_dotenv
from pathlib import Path

from runtime.core.agent import AgentClient
from runtime.core.queue import QueueProcessor
from runtime.core.plugin import PluginManager
from plugins.telegram.telegram_plugin import TelegramPlugin
from plugins.telegram.handlers import MessageHandler
from database.operations.shared import initialize_database, check_and_migrate_db
from common.config import get_env_var, get_settings, validate_settings
from common.logging import setup_logging

# Load environment variables
load_dotenv()

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

def create_default_settings() -> None:
    """Create default settings file if it doesn't exist."""
    settings_path = Path("settings.json")
    if not settings_path.exists():
        default_settings = {
            "debug_mode": False,
            "queue_refresh": 5,
            "max_retries": 3,
            "message_mode": "echo"
        }
        with open(settings_path, 'w') as f:
            json.dump(default_settings, f, indent=4)
        logger.info("Created default settings.json file")

class Application:
    """Main application class that coordinates all components."""
    
    def __init__(self):
        """Initialize the application components."""
        # Initialize plugin manager first
        self.plugin_manager = PluginManager()
        
        # Initialize other components
        self.agent = AgentClient()
        self.telegram = TelegramPlugin()  # Changed from TelegramBot to TelegramPlugin
        self.message_handler = MessageHandler(telegram_plugin=self.telegram)
        
        # Initialize queue processor with plugin manager
        self.queue_processor = QueueProcessor(
            message_processor=self._process_message,
            plugin_manager=self.plugin_manager
        )
        
        # Load the telegram plugin
        self.plugin_manager._plugins[self.telegram.get_name()] = self.telegram
        platform = self.telegram.get_platform()
        if platform:
            handler = self.telegram.get_message_handler()
            if handler:
                self.plugin_manager._platform_handlers[platform] = handler
                logger.info(f"Registered message handler for platform: {platform}")
        
        self._settings_file = "settings.json"
        self._settings_mtime = 0
        
        # Create default settings if needed
        create_default_settings()
        
        # Save PID to file
        with open("broca2.pid", "w") as f:
            f.write(str(os.getpid()))
    
    async def _check_settings(self):
        """Check if settings file has been modified."""
        try:
            current_mtime = os.path.getmtime(self._settings_file)
            if current_mtime > self._settings_mtime:
                logger.info("Settings file modified, reloading...")
                settings = get_settings()
                validate_settings(settings)
                
                # Update message mode in all components
                if 'message_mode' in settings:
                    new_mode = settings['message_mode']
                    logger.info(f"Updating message mode to: {new_mode}")
                    
                    # Update message handler
                    self.message_handler.set_message_mode(new_mode)
                    logger.info(f"Message handler mode set to: {new_mode}")
                    
                    # Update queue processor if it exists
                    if self.queue_processor:
                        self.queue_processor.set_message_mode(new_mode)
                        logger.info(f"🔵 Message processing mode changed to: {new_mode.upper()}")
                    
                    # Force immediate mode change
                    if self.queue_processor:
                        self.queue_processor.message_mode = new_mode
                        logger.info(f"🔵 Forced immediate mode change to: {new_mode.upper()}")
                
                # Update debug mode
                if 'debug_mode' in settings:
                    self.agent.debug_mode = settings['debug_mode']
                    logger.info(f"Debug mode {'enabled' if settings['debug_mode'] else 'disabled'}")
                
                # Update queue refresh interval
                if 'queue_refresh' in settings and self.queue_processor:
                    self.queue_processor.refresh_interval = settings['queue_refresh']
                    logger.info(f"Queue refresh interval set to {settings['queue_refresh']} seconds")
                
                # Update max retries
                if 'max_retries' in settings and self.queue_processor:
                    self.queue_processor.max_retries = settings['max_retries']
                    logger.info(f"Max retries set to {settings['max_retries']}")
                
                self._settings_mtime = current_mtime
                logger.info("Settings reloaded successfully")
        except Exception as e:
            logger.error(f"Failed to reload settings: {str(e)}")
    
    async def _handle_message(self, event: events.NewMessage.Event) -> None:
        """Handle incoming Telegram messages.
        
        Args:
            event: The Telegram message event
        """
        await self.message_handler.handle_private_message(event)
    
    async def _process_message(self, message: str) -> Optional[str]:
        """Process a message through the agent.
        
        Args:
            message: The message to process
            
        Returns:
            The agent's response or None if processing failed
        """
        return await self.agent.process_message(message)
    
    async def _on_message_processed(self, user_id: int, response: str) -> None:
        """Handle processed messages.
        
        Args:
            user_id: The Telegram user ID
            response: The processed response message
        """
        if self.telegram.client:
            await self.telegram.client.send_message(user_id, response)
    
    async def start(self) -> None:
        """Start all application components."""
        try:
            # Initialize and migrate the database safely
            await initialize_database()
            await check_and_migrate_db()
            
            # Initialize the agent
            logger.info("🔄 Initializing agent API connection...")
            if not await self.agent.initialize():
                logger.error("❌ Failed to initialize agent. Exiting...")
                return
            
            # Start plugin manager first
            logger.info("🔄 Starting plugin manager...")
            await self.plugin_manager.start()
            
            # Start Telegram client
            logger.info("🤖 Starting Telegram client...")
            await self.telegram.start()
            
            # Initialize queue processor
            logger.info("📋 Initializing message queue processor...")
            self.queue_processor = QueueProcessor(
                message_processor=self._process_message,
                plugin_manager=self.plugin_manager
            )
            
            # Set initial message mode
            self.message_handler.set_message_mode('echo')
            self.queue_processor.set_message_mode('echo')
            
            # Start queue processor
            queue_task = asyncio.create_task(self.queue_processor.start())
            
            # Set up Telegram handlers
            logger.info("📱 Setting up Telegram handlers...")
            self.telegram.add_message_handler(
                self._handle_message,
                events.NewMessage(incoming=True)
            )
            
            logger.info("✅ Application started successfully!")
            
            # Start settings monitor task
            settings_task = asyncio.create_task(self._monitor_settings())
            
            # Wait for the Telegram client to disconnect
            await self.telegram.client.run_until_disconnected()
            
        except KeyboardInterrupt:
            logger.warning("⚠️ Shutdown requested by user")
            # Cancel the queue processor task
            if self.queue_processor:
                queue_task.cancel()
                try:
                    await queue_task
                except asyncio.CancelledError:
                    pass
            # Clean up agent
            await self.agent.cleanup()
            # Disconnect Telegram client
            await self.telegram.client.disconnect()
            raise
        except Exception as e:
            logger.error(f"❌ Error: {str(e)}")
            # Clean up agent
            await self.agent.cleanup()
            # Disconnect Telegram client
            await self.telegram.client.disconnect()
            raise
    
    async def _monitor_settings(self):
        """Monitor settings file for changes."""
        while True:
            await self._check_settings()
            await asyncio.sleep(1)  # Check every second
    
    async def stop(self) -> None:
        """Stop all application components."""
        try:
            # Stop components in reverse order
            if self.queue_processor:
                logger.info("🛑 Stopping queue processor...")
                await self.queue_processor.stop()
            
            if self.telegram:
                logger.info("🛑 Stopping Telegram client...")
                await self.telegram.stop()
            
            # Clean up agent
            logger.info("🛑 Cleaning up agent...")
            await self.agent.cleanup()
            
            # Stop plugin manager last
            logger.info("🛑 Stopping plugin manager...")
            await self.plugin_manager.stop()
            
            # Remove PID file
            try:
                os.remove("broca2.pid")
            except:
                pass
                
            logger.info("✅ Application stopped successfully")
            
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {str(e)}")
            raise

    def update_settings(self, settings: dict) -> None:
        """Update application settings.
        
        Args:
            settings: Dictionary containing the new settings
        """
        if 'message_mode' in settings:
            new_mode = settings['message_mode']
            logger.info(f"Updating message mode to: {new_mode}")
            self.message_handler.set_message_mode(new_mode)
            if self.queue_processor:
                self.queue_processor.set_message_mode(new_mode)
        if 'debug_mode' in settings:
            self.agent.debug_mode = settings['debug_mode']

def main() -> None:
    """Application entry point."""
    try:
        logger.info("🚀 Starting application...")
        app = Application()
        asyncio.run(app.start())
    except KeyboardInterrupt:
        logger.warning("⚠️ Shutdown requested by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 