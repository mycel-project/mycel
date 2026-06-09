from typing import Any, Optional

# We include status_code here even though exception handling is not strictly tied to REST, for convenience.
class DomainException(Exception):
    def __init__(self, code: str, message: str, status_code: int):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code

# User errors

class UserError(DomainException):
    def __init__(self, code: str, message: str, status_code: int):
        super().__init__(
            code=code,
            message=message,
            status_code=status_code,
        )

class NoUserFound(UserError):
    def __init__(self, user_id: str):
        super().__init__(
            code="USER_NOT_FOUND",
            message=f"No user found for id {user_id}",
            status_code=404,
        )

class ForbiddenError(UserError):
    def __init__(self):
        super().__init__(
            code="FORBIDDEN",
            message="Access denied",
            status_code=403,
        )

# Collection errors

class CollectionError(DomainException):
    def __init__(self, code: str, message: str, status_code: int):
        super().__init__(
            code=code,
            message=message,
            status_code=status_code,
        )

class NoCollectionFound(CollectionError):
    def __init__(self, collection_id: str):
        super().__init__(
            code="COLLECTION_NOT_FOUND",
            message=f"No collection found for id {collection_id}",
            status_code=404,
        )

# Node errors

class NoNodeFound(DomainException):
    def __init__(self, node_id: str):
        super().__init__(
            code="NODE_NOT_FOUND",
            message=f"No node found for id {node_id}",
            status_code=404
        )

class NoLearningUnitFound(DomainException):
    def __init__(self, learning_unit_id: str):
        super().__init__(
            code="LEARNING_UNIT_NOT_FOUND",
            message=f"No learning unit for id {learning_unit_id}",
            status_code=404
        )

class NotAFragment(DomainException):
    def __init__(self, id: str):
        super().__init__(
            code="NOT_A_FRAGMENT",
            message=f"Node/Learning unit {id} is not a fragment",
            status_code=400
        )

class NotASpore(DomainException):
    def __init__(self, id: str):
        super().__init__(
            code="NOT_A_SPORE",
            message=f"Node/Learning unit {id} is not a spore",
            status_code=400
        )

class NotAKnownType(DomainException):
    def __init__(self, node_id: str, type_value: str):
        super().__init__(
            code="UNKNOWN_NODE_TYPE",
            message=f"Node with id {node_id} has an unknown type key: {type_value}",
            status_code=400
        )

class NodeDeleted(Exception):
    def __init__(self, node_id: str):
        super().__init__(f"Node {node_id} exists but has been deleted")

        
class EmptyField(DomainException):
    def __init__(self, node_id: str, field: str):
        super().__init__(
            code="EMPTY_FIELD",
            message=f"Node with id {node_id} has no content for field {field}",
            status_code=400
        )
        
# Extract errors

class ExtractError(DomainException):
    def __init__(self, code: str, message: str):
        super().__init__(
            code=code,
            message=message,
            status_code=400,
        )

class ExtractMismatchError(ExtractError):
    def __init__(self, rebuilt_text: str, text: str):
        message = (
            "Selection mismatch: extracted content differs from reconstructed slice. "
            f"rebuilt_text='{rebuilt_text[:100]}', text='{text[:100]}'"
        )
        super().__init__(
            code="EXTRACT_MISMATCH",
            message=message,
        )
        
class InvalidSourceNodeType(ExtractError):
    def __init__(self, node_id: str, type: str):
        super().__init__(
            code="INVALID_SOURCE_NODE_TYPE",
            message=f"You can only create a new node from a fragment, but node with id {node_id} has a type of {type}.",
        )


# update errors

class InvalidNodeUpdate(DomainException):
    def __init__(
        self,
        node_id: str,
        node_type: str,
        node_content: Any,
        reason: Optional[str] = None,
    ):
        content_preview = str(node_content)[:200]

        message = (
            f"Invalid update for node {node_id}"
            f"(type={node_type}, content_preview={content_preview})"
        )

        if reason:
            message += f" | reason: {reason}"

        super().__init__(
            code="INVALID_NODE_UPDATE",
            message=message,
            status_code=400
        )

# Ressource Errors

class RessourceError(DomainException):
    def __init__(self, code: str, message: str, status_code: int):
        super().__init__(
            code=code,
            message=message,
            status_code=400,
        )

class UnknownRessourceTypeError(RessourceError):
    def __init__(self, type: str):
        super().__init__(
            code="UNKNOWN_RESSOURCE_TYPE",
            message=f"Cannot create resource: unknown type '{type}'",
            status_code=400
        )

class InvalidUrl(RessourceError):
    def __init__(self, url: str):
        super().__init__(
            code="INVALID_URL",
            message=f"'{url}' is not a valid URL",
            status_code=400
        )

class UnsafeUrl(RessourceError):
    def __init__(self, url: str):
        super().__init__(
            code="UNSAFE_URL",
            message=f"'{url}' is not a safe URL to fetch",
            status_code=400
        )

class PageTooLarge(RessourceError):
    def __init__(self, url: str, max_size_bytes: int):
        super().__init__(
            code="PAGE_TOO_LARGE",
            message=f"Page at '{url}' is too large (max {max_size_bytes // (1024 * 1024)}MB)",
            status_code=400
        )


# Reviews Errors

class ReviewError(DomainException):
    def __init__(self, code: str, message: str, status_code: int):
        super().__init__(
            code=code,
            message=message,
            status_code=status_code,
        )

class PendingReviewMismatchError(ReviewError):
    def __init__(self, review_id: str, pending_id: str):
        super().__init__(
            code="PENDING_REVIEW_MISMATCH",
            message=f"Received review id ({review_id}) does not match pending id ({pending_id})",
            status_code=409,
        )

class NoPendingReviewError(ReviewError):
    def __init__(self, review_id: str):
        super().__init__(
            code="NO_PENDING_REVIEW",
            message=f"No pending review (received {review_id})",
            status_code=409,
        )

class UnknownReviewTypeError(ReviewError):
    def __init__(self, review_type: str):
        super().__init__(
            code="UNKNOWN_REVIEW_TYPE",
            message=f"Unknown review type: {review_type}",
            status_code=400,
        )

class NoReviewToUndo(ReviewError):
    def __init__(self):
        super().__init__(
            code="NO_REVIEW_TO_UNDO",
            message = f"No review available to undo",
            status_code=409,
        )

class ReviewUndoError(ReviewError):
    def __init__(self, code: str, message: str, status_code=409):
        super().__init__(code=code, message=message, status_code=status_code)

class ReviewUndoLearningUnitInaccessible(ReviewUndoError):
    def __init__(self, learning_unit_id: str, review_id: str):
        super().__init__(
            code="UNDO_LEARNING_UNIT_INACCESSIBLE",
            message=f"Review {review_id} was undone but learning unit {learning_unit_id} is inaccessible",
        )

class ReviewUndoNotAllowedError(ReviewUndoError):
    def __init__(self, review_age_s: int, max_age_s: int):
        super().__init__(
            code="UNDO_REVIEW_NOT_ALLOWED",
            message = f"Undo not allowed: review is too old\n({review_age_s}ms > {max_age_s}ms)",
            status_code=403,
        )
        
# Other 

class ClozeValidationError(DomainException):
    def __init__(self, code: str = "CLOZE_VALIDATION_ERROR", message: str = "", status_code: int = 422):
        super().__init__(
            code=code,
            message=message,
            status_code=status_code,
        )

class NoClozeFieldError(ClozeValidationError):
    def __init__(self, text: str):
        super().__init__(
            code="NO_CLOZE_FIELD_ERROR",
            message=f"No cloze field found in {text[:200]}",
            status_code=422
        )

class NoHeadingToSplit(DomainException):
    def __init__(self, node_id: str, level: int):
        super().__init__(
            code="NO_HEADING_TO_SPLIT",
            message=f"No heading of level <= {level} found in node {node_id}",
            status_code=422
        )

# Authentication

class AuthenticationError(DomainException):
    """Base authentication error"""
    def __init__(self, code: str = "AUTHENTICATION_ERROR", message: str = "", status_code: int = 422):
        super().__init__(
            code=code,
            message=message,
            status_code=status_code,
        )

class Unauthorized(AuthenticationError):
    """User is not authorized"""
    def __init__(self, code: str = "UNAUTHORIZED", message: str = "", status_code: int = 401):
        super().__init__(
            code=code,
            message=message,
            status_code=status_code,
        )

class InvalidToken(Unauthorized):
    """Provided token is invalid or expired"""
    def __init__(self, code: str = "INVALID_TOKEN", message: str = "Token is invalid or expired"):
        super().__init__(
            code=code,
            message=message,
        )

# ImportExport
class DataError(DomainException):
    def __init__(self, code: str = "DATA_ERROR", message: str = "An error occurred during import or export.", status_code: int = 400):
        super().__init__(
            code=code,
            message=message,
            status_code=status_code,
        )

class DataImportError(DataError):
    def __init__(self, code: str = "IMPORT_ERROR", message: str = "Data import failed.", status_code: int = 422):
        super().__init__(
            code=code,
            message=message,
            status_code=status_code,
        )

class DataExportError(DataError):
    def __init__(self, code: str = "EXPORT_ERROR", message: str = "Data export failed.", status_code: int = 400):
        super().__init__(
            code=code,
            message=message,
            status_code=status_code,
        )
