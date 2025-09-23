# Knowledge Graph: Forge-API-Tool

## Main Entities
- Forge-API-Tool (project root)
- web_dashboard (frontend)
- core (backend logic)
- configs/config (configuration)
- wildcards (prompt/wildcard management)
- scripts (utilities)
- tests (test suite)
- .SYSTEM (system docs/onboarding)
- .cursor (MCP config)

## Relationships
- web_dashboard uses core for backend API calls
- core uses configs for API preferences
- wildcards used by both core and web_dashboard
- scripts support wildcards and encoding fixes
- tests cover all major modules
- .SYSTEM and .cursor support onboarding and LLM integration 