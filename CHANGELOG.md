## Unreleased

## v0.2.0-alpha

This update introduces a major refactor of Mycel's database structure, identifiers, security, testing, and more. It is quite substantial as it addresses former architectural issues.
To see more details, check the commit history.

### Added

- Re-enabled minimum cloze field validation on spore save. Invalid spore states are now rejected and the last valid state is preserved. (see Mycel v0.0.5)
- Split node endpoint: decompose a node into fragments by heading level. The operation may be rejected if the selected level does not produce enough fragments to justify splitting. The due date of created fragments is set to the next day.
- Add a base class for AuthService with behavior driven by deployment_mode set in the config. AuthService can be passed when starting Mycel to allow an external concrete implementation.
- Add optional idempotency protection on all REST endpoints
- Integration tests for all REST endpoints and all repositories
- Standardize API responses, always wrapping data in a data field
- Scope all actions by user ID
- Add Scalar API reference (mycel_address/scalar)
- Add foundations for a templating system
- Abstract node model from spore/fragment to allow multiple spores to be based on the same node (preparing ground for multi-question nodes), introducing the new LearningUnit table. This comes with changes to NodeView DTOs
- Invert prioritization logic (100% is now the highest priority)
- Add max page protection and protect against SSRF
- Normalize error responses

### Refactor

- Use MycelConfig model rather than a raw dict
- Start refactoring and cleaning the REST API
- Use SQLAlchemy instead of raw SQLite to support PostgreSQL
- Replace most former dataclass models with Pydantic ones
- Use UUIDs for all identifiers instead of integers
- Store pending reviews in the database rather than in runtime cache

## v0.1.1
### Added
- Remove markdown links formatting from selection
- Spores scheduled for today but not yet due (e.g. due at 11am but reviewed at 9am) are deprioritized, surfacing only when no ready nodes remain. (togglable in config)
- Rescheduling a node that is in pending_review_cache now automatically clears its review state.
- Added /outline endpoint to extract heading structure from a node's content (also handle headings when they are in blockquote)

### Fixed
- Node query is no longer stuck to 100 nodes 
- Use float priority instead of int (which caused duplicate values)

## v0.1.0
### Added
- Depth-based fragment scheduling algorithm: deeper fragments grow toward longer intervals faster, while shallow fragments follow a near-linear review pace. (applied both at creation and review)

### Fixed
- Fragment review now takes timezone into account when computing the next due date.

## v0.0.5
### Fix 
- Removed the minimum cloze field check during spore validation as it conflicted with the autosave logic. Temporary fix until a more appropriate spore editing system is implemented.

## v0.0.4
### Added
- Start implementing calendar logic by counting due fragments/spores for each day.
- Gather days in calendar/reviews using local timezone (given by frontend)
- Can now reschedule a node to a specific day using local timezone
- Send updated node data after review (notably for new due date)
- When creating an extract (both fragments and spores atm) or importing ressource, set the first review for the next day (timezone aware).

## v0.0.3
### Added
- Automatically hard-delete soft-deleted nodes after `delete_max_age` is reached. By default, deletion runs every hour and at startup.

### Fixed
- Cloze regex was working in Mycel but was too Python-specific to be usable in the frontend. Changed that.
- Fixed unit for undo review max age: it was saved in minutes but used as seconds
- When undoing a review from a deleted node, apply undo but raise a warning
- Clarified how NodeUpdate behaves: only explicitly provided fields are updated, and even None values will overwrite existing data. (may impact existing update logic relying on None being ignored)

## v0.0.2
### Added 
- Add user config param: "add extract to nav"

### Fixed
- Correct cloze regex to allow ":" inside it

## v0.0.1
- Initial release
