# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.9.0] - 2024-12-28

### Added
- **CLI-first Architecture**: Complete redesign focusing on command-line interface for better control and automation
- **Plugin System**: Extensible plugin-based message handling system
  - Telegram plugin for Telegram bot integration
  - CLI plugin for diagnostic and testing capabilities
  - Standardized plugin interface with lifecycle management
- **Prismatic Telegram Bot Plugin**: New plugin implementing 1:1 owner-only messaging with aiogram integration
- **Queue Management System**: Comprehensive message queue processing with multiple modes (Echo, Listen, Live)
- **Agent API Integration**: Enhanced Letta Agentic Framework integration through `AgentClient`
- **Database Operations**: New database models and operations for users, messages, and queue management
- **CLI Tools**: Comprehensive admin tools including:
  - Queue management (`broca-admin queue`)
  - User management (`broca-admin users`)
  - Settings management (`broca-admin settings`)
  - Conversation tools for viewing and managing conversations
- **MCP-Ready Design**: All CLI tools and plugin interfaces designed for machine-controllability by agents

### Changed
- **Project Rebranding**: Renamed from "Broca 2" to "Sanctum: Broca 2" across all documentation and references
- **Architecture Restructure**: Clean separation between core and platform-specific code
- **Database Schema**: Refactored LettaUser model, removed redundant `conversation_history_limit` field
- **Documentation Updates**: 
  - Enhanced README with middleware role explanation and multi-agent architecture plans
  - Updated project analysis and documentation formatting
  - Revised project plans for Telegram bot implementation
  - Added comprehensive plugin development guide

### Fixed
- **Telegram Bot Stability**: Addressed minor bugs in Prismatic Telegram BOT plugin implementation
- **Database Migration**: Enhanced migration scripts with proper error handling and logging
- **Message Handling**: Improved Telegram message handling with bot ignore functionality
- **Documentation**: Corrected formatting in Database Layer section for improved readability

### Removed
- **Legacy Documentation**: Removed outdated `broca-2-plan.md` and `codebase-analysis.md` files as part of project restructuring
- **Database Backup**: Removed database backup from git tracking and updated `.gitignore`

### Technical Details
- **Dependencies**: Updated to include telethon, python-dotenv, sqlalchemy, aiohttp, emoji, rich, typer, and pydantic
- **Entry Points**: Added console scripts for `broca2` and `broca-admin`
- **Version**: Bumped to 0.9.0 reflecting major architectural changes

### Planned Features
- **Multi-Agent Architecture**: Support for multiple Letta agents with shared virtual environments
- **Broca MCP Server**: Management Control Panel for instance management, monitoring, and centralized configuration

---

## How to Read This Changelog

- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Vulnerability fixes

---

*For more details on any changes, please refer to the git commit history or project documentation.*