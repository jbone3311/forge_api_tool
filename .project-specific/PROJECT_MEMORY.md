# PROJECT_MEMORY.md

## Project Name
Forge-API-Tool

## Project Purpose
A modern web-based client application for managing and automating image generation using external AI image generation APIs (Automatic1111, ComfyUI, etc.). Features a beautiful Bootstrap 5 dashboard, template management, and comprehensive settings. Features advanced wildcard management with encoding fix utilities.

## Architecture Overview
- **Frontend:** web_dashboard (Bootstrap 5, modular JS, HTML templates)
- **Backend:** core (API config, batch runner, image analysis, etc.)
- **Configuration:** configs/ and config/ (JSON files for API preferences, templates, etc.)
- **Wildcard Management:** wildcards/ (prompt sets, encoding utilities)
- **Utilities:** scripts/ (debug, encoding fixes)
- **Testing:** tests/ (unit, functional, property, security, performance, stress)
- **System Docs:** .SYSTEM/ (onboarding, setup, guides)
- **MCP Config:** .cursor/ (MCP/LLM server configuration)

## Key Decisions
- Use of Bootstrap 5 for a modern, responsive dashboard UI
- Modular test suite for comprehensive coverage
- Advanced wildcard management with encoding fix utilities
- LLM-first onboarding and project memory approach
- All project-specific notes and memory stored in .PROJECT-SPECIFIC/ 