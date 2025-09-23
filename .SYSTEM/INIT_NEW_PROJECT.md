# INIT_NEW_PROJECT.md

Welcome! This document will guide you (and the LLM) through initializing a new MCP project. Please follow each step, confirm with the user, and use the example prompts provided.

---

## 1. Project Purpose & Overview

- **LLM: Ask the user for the project name and a 1-2 sentence description of its purpose and main goals.**
- **Example Prompt:**
  > "What is the name of your project, and what are its main goals or purpose? Please provide a brief description."

---

## 2. Scan and Summarize the Codebase

- **If this is a new codebase:**
  - Scan the project directory for existing code, modules, and files.
  - Summarize the main components, structure, and any detected dependencies.
- **If starting from scratch:**
  - Propose a minimal scaffold (folders, README, etc.) and confirm with the user.
- **Example Prompt:**
  > "I will now scan the codebase and provide a summary of the main modules, files, and dependencies."

---

## 3. Build the Knowledge Graph

- Identify main modules, concepts, and dependencies from the summary.
- Create the initial knowledge graph and store it in `.PROJECT-SPECIFIC/knowledge-graph/`.
- **Example Prompt:**
  > "Based on the project summary, I will create an initial knowledge graph of the main entities, modules, and their relationships."

---

## 4. Set Up Project Memory

- Create a summary file in `.PROJECT-SPECIFIC/PROJECT_MEMORY.md` with:
  - Project goals
  - Architecture overview
  - Key decisions
- **Example Prompt:**
  > "I will now create a project memory file summarizing the project’s goals, architecture, and any important decisions."

---

## 5. Human Review & Iteration

- **User: Please review and edit the generated knowledge graph and project memory for accuracy and completeness.**
- **LLM: Ask the user for feedback and offer to make adjustments.**
- **Example Prompt:**
  > "Please review the generated knowledge graph and project memory. Let me know if anything needs to be added or changed."

---

## 6. Automation/Script Option (if available)

- If you prefer automation, you may use a setup script (e.g., `.SYSTEM/system-setup/init_knowledge_graph.py`) to initialize the knowledge graph and project memory. Otherwise, continue collaborating with the LLM.

---

## 7. Reference Guides

- For detailed steps, see:
  - `.SYSTEM/USER_GUIDE_KNOWLEDGE_GRAPH.md`
  - `.SYSTEM/USER_GUIDE_MCP_TOOLS.md`
  - `.SYSTEM/USER_GUIDE_SETUP.md`
  - `.SYSTEM/USER_GUIDE_TESTING.md`

---

## 8. Next Steps

- Update the knowledge graph and project memory as you build.
- Use the LLM for code generation, refactoring, and documentation.
- Keep all project-specific notes in `.PROJECT-SPECIFIC/`.

---

**LLM: Please confirm each step with the user before proceeding. Use the example prompts to guide the conversation.** 