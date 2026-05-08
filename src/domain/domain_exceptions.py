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
    def __init__(self, user_id: int):
        super().__init__(
            code="USER_NOT_FOUND",
            message=f"No user found for id {user_id}",
            status_code=404,
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
    def __init__(self, collection_id: int):
        super().__init__(
            code="COLLECTION_NOT_FOUND",
            message=f"No collection found for id {collection_id}",
            status_code=404,
        )

# Node errors

class NoNodeFound(DomainException):
    def __init__(self, node_id: int):
        super().__init__(
            code="NODE_NOT_FOUND",
            message=f"No node found for id {node_id}",
            status_code=404
        )
        

class NotAFragment(DomainException):
    def __init__(self, node_id: int):
        super().__init__(
            code="NOT_A_FRAGMENT",
            message=f"Node with id {node_id} is not a fragment",
            status_code=400
        )


class NotASpore(DomainException):
    def __init__(self, node_id: int):
        super().__init__(
            code="NOT_A_SPORE",
            message=f"Node with id {node_id} is not a spore",
            status_code=400
        )


class NotAKnownType(DomainException):
    def __init__(self, node_id: int, type_value: int):
        super().__init__(
            code="UNKNOWN_NODE_TYPE",
            message=f"Node with id {node_id} has an unknown type key: {type_value}",
            status_code=400
        )

class NodeDeleted(Exception):
    def __init__(self, node_id: int):
        super().__init__(f"Node {node_id} exists but has been deleted")

        
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
    def __init__(self, node_id: int, type: int):
        super().__init__(
            code="INVALID_SOURCE_NODE_TYPE",
            message=f"You can only create a new node from a fragment, but node with id {node_id} has a type of {type}.",
        )


# update errors

class InvalidNodeUpdate(DomainException):
    def __init__(
        self,
        node_id: int,
        node_type: int,
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

# Reviews Errors

class ReviewError(DomainException):
    def __init__(self, code: str, message: str, status_code: int):
        super().__init__(
            code=code,
            message=message,
            status_code=status_code,
        )

class PendingReviewMismatchError(ReviewError):
    def __init__(self, review_id: int, pending_id: int):
        super().__init__(
            code="PENDING_REVIEW_MISMATCH",
            message=f"Received review id ({review_id}) does not match pending id ({pending_id})",
            status_code=409,
        )

class NoPendingNodeError(ReviewError):
    def __init__(self, review_id: int):
        super().__init__(
            code="NO_PENDING_NODE",
            message=f"No pending review node (received {review_id})",
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

class ReviewUndoNodeInaccessible(ReviewUndoError):
    def __init__(self, node_id: int, review_id: int):
        super().__init__(
            code="UNDO_NODE_INACCESSIBLE",
            message=f"Review {review_id} was undone but node {node_id} is inaccessible",
        )

class ReviewUndoNotAllowedError(ReviewUndoError):
    def __init__(self, review_age_ms: int, max_age_ms: int):
        super().__init__(
            code="UNDO_REVIEW_NOT_ALLOWED",
            message = f"Undo not allowed: review is too old\n({review_age_ms}ms > {max_age_ms}ms)",
            status_code=403,
        )
        
# Other 

class ClozeValidationError(DomainException):
    def __init__(self, text: str):
        super().__init__(
            code="CLOZE_VALIDATION_ERROR",
            message=f"No cloze field found in {text[:200]}",
            status_code=400
        )
