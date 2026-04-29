from typing import Any, Optional


# We include status_code here even though exception handling is not strictly tied to REST, for convenience.
class DomainException(Exception):
    def __init__(self, code: str, message: str, status_code: int):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code

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

        
# Extract errors

class ExtractMismatchError(DomainException):
    def __init__(self, rebuilt_text: str, text: str):
        message = (
            "Selection mismatch: extracted content differs from reconstructed slice. "
            f"rebuilt_text='{rebuilt_text[:100]}', text='{text[:100]}'"
        )
        super().__init__(
            code="EXTRACT_MISMATCH",
            message=message,
            status_code=400,
        )
        
class InvalidSourceNodeType(DomainException):
    def __init__(self):
        super().__init__(
            code="INVALID_SOURCE_NODE_TYPE",
            message="You can only create a new node from a fragment",
            status_code=400
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
        content_preview = str(node_content)[:100]

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


# Other 

class ClozeValidationError(DomainException):
    def __init__(self, message: str = "Cloze validation error"):
        super().__init__(
            code="CLOZE_VALIDATION_ERROR",
            message="",
            status_code=400
        )
