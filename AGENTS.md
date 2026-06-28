# Project Overview
Mycel is a long-term learning backend written in Python, exposing a REST API to which
different clients connect to add content, review, and learn. Mycel is and must stay
agnostic. It is designed to be self-hostable or run on a centralized server, but infrastructure
beyond the core backend (e.g. cloud hosting, authentication services) is out of scope
for this project.

# Architecture
Layers are kept strictly separated.

Main directories:
- core/ — app-level utilities and configuration
- domain/ — business logic and use cases
- models/ — data models
- schemas/ — API schemas (input/output)
- repositories/ — data access layer
- services/ — orchestration between domain and repositories
- interfaces/ — API layer (FastAPI)
- db/ — database setup and migrations

The flow is: API request → (orchestrators → use cases →) services → repositories, and back up.

# Key Concepts
- Spore: atomic unit of knowledge to memorize (like a flashcard)
  (equivalent to an Item in SuperMemo)
- Fragment: equivalent to a Topic in SuperMemo
- Node: model stored in the database, holding data associated to a spore or fragment
- Learning unit: attached to a node, but multiple can be attached to the same node.
  Holds type-specific data that would otherwise be duplicated, for example, allowing
  multiple spores to be created from the same node and thus the same content.
- Slot: index identifying a specific learning unit within a node. Also corresponds to the index used in render_config when specified in a template (see template.py). Starts at 1.

# Stack
- Python with SQLAlchemy for database abstraction
- FastAPI for the API layer
- Alembic for database migrations, ensuring compatibility across versions. Any breaking change — even minor ones, especially around endpoints or business logic — must be discussed before implementation to find the best migration path.

# Conventions
- Follow existing code conventions — when in doubt, look at what's already there
- Everything written into files (code, comments, ...) must be written in English.
- Keep comments minimal — only add them when the code is not self-explanatory or when explicitly asked.
- When adding a new field to the configuration, document it in the changelog in bold.

# Testing
- All tests are in tests/, mirroring the source structure with unit and integration subdirectories

# Workflow
- When adding a feature, always discuss the testing approach together before implementing it.

# What NOT to do
- Don't break the layer architecture
- Never commit unless explicitly told to

# Commits
- Follow Conventional Commits: feat/fix/refactor/chore: short description (English).
- Add a body when the commit message alone is not self-explanatory, or for releases. Skip it for trivial changes.
- Add Co-authored-by: <model-name> only when the agent wrote or significantly modified the code, not for simple instructions applied as-is.
- Always write in English in commit messages, even if we are talking in another language.
- After each meaningful commit, add an entry to CHANGELOG.md under the Unreleased section, in the appropriate category (Added, Fixed, or Refactored), in English. Skip trivial or chore commits.
