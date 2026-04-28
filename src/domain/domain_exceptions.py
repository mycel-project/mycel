from typing import Any, Optional

class DomainException(Exception):
    """Base class for all domain errors."""
    pass

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
            f"Invalid update for node {node_id} "
            f"(type={node_type}, content_preview={content_preview})"
        )

        if reason:
            message += f" | reason: {reason}"

        super().__init__(message)

        self.node_id = node_id
        self.node_type = node_type
        self.node_content = node_content
        self.reason = reason
        
class ClozeValidationError(DomainException):
    pass

class ReviewLockedError(DomainException):
    pass

class NoNodeFound(DomainException):
    def __init__(self, node_id: int):
        super().__init__(f"No node found for id {node_id}")
        self.node_id = node_id

class NotAFragment(DomainException):
    def __init__(self, node_id: int):
        super().__init__(f"Node with id {node_id} is not a fragment")
        self.node_id = node_id

class NotASpore(DomainException):
    def __init__(self, node_id: int):
        super().__init__(f"Node with id {node_id} is not a spore")
        self.node_id = node_id

class NotAKnownType(DomainException):
    def __init__(self, node_id: int, type_value: int):
        super().__init__(f"Node with id {node_id} has an unknown type key: {type_value}")
        self.node_id = node_id
        self.type_value = type_value
