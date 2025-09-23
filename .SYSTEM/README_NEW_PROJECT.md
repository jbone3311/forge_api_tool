# New Project Setup

## Quick Start

1. **Copy the following directories into your new project root:**
   - `.SYSTEM` (system-level docs, templates, and setup scripts)
   - `.cursor` (MCP server configuration and system settings)

2. **First Run:**
   - On first run, the system will automatically create the `.PROJECT-SPECIFIC` directory structure for project memory and project-specific docs.

3. **System Setup Scripts:**
   - All system setup scripts are now located in the `system-setup/` directory inside `.SYSTEM`.
   - Use these scripts to verify MCP server installation, environment setup, and system checks.

4. **Environment Variables:**
   - Ensure you have a `.env` file (see `.SYSTEM/env-sample.txt`) with all required secrets and connection strings.

5. **User Documentation:**
   - See `USER_DOCS_INDEX.md` for a full index of user-facing documentation.

---

## Notes
- Do **not** copy `.PROJECT-SPECIFIC` from another project; it will be created fresh for each new project.
- All onboarding, test, and setup scripts reference `.SYSTEM` and `.PROJECT-SPECIFIC` (not `.universal` or `.project-specific`).
- Old setup scripts and directories have been removed or consolidated into `system-setup/`. 