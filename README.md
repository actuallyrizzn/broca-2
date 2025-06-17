# Sanctum: Broca 2 (v0.9.0)

A CLI-first, plugin-based message processing system for agent communication.

## 🚀 Overview

Sanctum: Broca 2 is a refactored version of Broca, focusing on:
- CLI-first architecture for better control and automation
- Plugin-based system for extensible message handling
- Clean separation between core and platform-specific code
- Improved maintainability and testing capabilities

## Broca: The Middleware Bridge

Sanctum: Broca 2 serves as middleware designed to bridge the Letta Agentic Framework with various communication endpoints. Just as Broca's area in the human brain is responsible for language production and speech, Sanctum: Broca 2 acts as the "speech center" for AI systems—translating agent intentions into actionable messages across different platforms.

In the AI brain, Sanctum: Broca 2 plays a crucial role by:
- **Translating Agent Intentions:** Converting high-level agent decisions into platform-specific messages.
- **Unifying Communication:** Providing a standardized interface for different endpoints (Telegram, CLI, APIs, etc.).
- **Enabling Extensibility:** Allowing new endpoints to be integrated seamlessly through the plugin system.

This middleware approach ensures that the Letta Agentic Framework can focus on decision-making and intelligence, while Sanctum: Broca 2 handles the complexities of communication and integration.

## 🏗️ Architecture

```
broca2/
├── main.py              # Core runtime entry point
├── runtime/             # Core system components
│   ├── core/           # Core functionality
│   │   ├── agent.py    # Agent API interaction
│   │   ├── queue.py    # Message queue processing
│   │   ├── plugin.py   # Plugin management
│   │   └── message.py  # Message handling
├── cli/                 # CLI tools
│   ├── queue.py        # Queue management
│   ├── users.py        # User management
│   ├── conversations.py # Conversation tools
│   └── settings.py     # Settings management
├── plugins/            # Platform plugins
│   ├── telegram/      # Telegram plugin
│   └── cli/           # CLI plugin
└── common/            # Shared utilities
    ├── config.py      # Configuration
    └── logging.py     # Logging setup
```

## 🔧 Core Components

### Runtime
- **Application**: Main coordinator
- **QueueProcessor**: Message queue handling
- **AgentClient**: Agent API interaction
- **PluginManager**: Plugin lifecycle management

### CLI Tools
- **Queue Management**: List, flush, delete messages
- **User Management**: List and manage users
- **Conversation Tools**: View and manage conversations
- **Settings**: Configure system behavior

### Plugins
- **Telegram Plugin**: Telegram message handling
- **CLI Plugin**: Diagnostic/testing interface

## 🎯 Features

### Message Processing
- Multiple processing modes:
  - Echo: Direct message return
  - Listen: Store without processing
  - Live: Process through agent
- Core block management
- Error handling and recovery

### Plugin System
- Standardized plugin interface
- Platform-specific message handling
- Event routing
- Settings management per plugin

### CLI Interface
- Comprehensive admin tools
- Diagnostic capabilities
- Settings management
- Queue operations

## 🛠️ Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/broca-2.git
   cd broca-2
   ```

2. Install dependencies:
   ```bash
   pip install -e .
   ```

3. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

## 🚦 Usage

### Running the Server
```bash
python -m broca2.main
```

### CLI Tools
```bash
# Queue management
broca-admin queue list
broca-admin queue flush

# User management
broca-admin users list

# Settings
broca-admin settings set message_mode live
```

### Plugins
- Telegram plugin runs as part of the server
- CLI plugin is a standalone diagnostic tool

## 📝 Configuration

### Settings
- Message processing mode
- Queue refresh interval
- Debug mode
- Plugin-specific settings

### Environment Variables
- Agent API credentials
- Database configuration
- Plugin-specific settings

## 🔌 Plugin Development

### Plugin Structure
```python
from plugins import Plugin

class MyPlugin(Plugin):
    def get_name(self) -> str:
        return "my_plugin"
    
    def get_platform(self) -> str:
        return "my_platform"
    
    def get_message_handler(self) -> Callable:
        return self._handle_message
    
    async def start(self) -> None:
        # Initialize plugin
        
    async def stop(self) -> None:
        # Cleanup plugin
```

### Required Methods
- `get_name()`: Plugin identifier
- `get_platform()`: Platform name
- `get_message_handler()`: Message handler
- `start()`: Plugin initialization
- `stop()`: Plugin cleanup

## 🧪 Testing

### Core Functionality
- Message processing modes
- Queue operations
- Core block management
- Error handling

### Plugin Integration
- Plugin lifecycle
- Message routing
- Event handling
- Settings propagation

## 📚 Documentation

- [Plugin Development Guide](broca2/docs/plugin_development.md)
- [CLI Tools Reference](broca2/docs/cli_reference.md)
- [Configuration Guide](broca2/docs/configuration.md)
- [Telegram Plugin](broca2/docs/telegram-plugin-spec.md)
- [Telegram Bot Plugin](broca2/docs/telegram-bot-plugin.md)
- [CLI-Test Plugin](broca2/docs/cli-test-plugin.md)

## 🤖 Agent/MCP-Ready Design

Sanctum: Broca 2 is built so that all CLI tools and plugin interfaces are **MCP'able** (machine-controllable by agents):
- Every CLI and admin tool is scriptable and can be operated by other AI agents or automation systems.
- All commands support machine-friendly output (e.g., JSON) and error handling.
- This enables Sanctum: Broca 2 to be embedded in agent networks, automated test harnesses, or orchestration systems.
- When extending Sanctum: Broca 2, always consider both human and agent/automation use cases.

## 🔮 Planned Updates

### Multi-Agent Architecture
Sanctum: Broca 2 will support multiple Letta agents through a simple, efficient architecture:
- Each agent will run in its own Broca instance
- Instances will share a common virtual environment to minimize resource usage
- Simple git-based update system that preserves agent-specific configurations
- Clear 1:1 mapping between Broca instances and Letta agents

### Broca MCP Server
A new Management Control Panel server will be added to manage multiple Broca instances:
- Instance Management: Deploy, monitor, and update Broca instances
- Agent Configuration: Manage Letta agent credentials and settings
- Monitoring & Logging: Centralized logging and performance metrics
- Resource Management: Monitor shared resources and system health
- Security: Centralized credential management and access control

## 🤖 Acknowledgments

- Original Broca project (It was me).
- Contributors and maintainers (Also me).
- Community support  (the AI agents I made to help me).