## Unreleased

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
