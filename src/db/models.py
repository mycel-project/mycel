from sqlalchemy import BigInteger, String, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column
from src.db.schema import Base

# server_default instead of default: the DB handles the default value at the DDL level.
# This ensures raw SQL inserts (e.g. in tests) also benefit from the default, bypassing SQLAlchemy.

class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[int] = mapped_column(BigInteger, nullable=False)
    conf: Mapped[str] = mapped_column(String, nullable=False, server_default="{}")
    templates: Mapped[str] = mapped_column(String, nullable=False, server_default="{}")
    pending_node_id: Mapped[str | None] = mapped_column(String(36), nullable=True)


class CollectionORM(Base):
    __tablename__ = "collections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[int] = mapped_column(BigInteger, nullable=False)
    updated_at: Mapped[int] = mapped_column(BigInteger, nullable=False)
    conf: Mapped[str] = mapped_column(String, nullable=False, server_default="{}")
    algoconf: Mapped[str] = mapped_column(String, nullable=False, server_default="{}")


class NodeORM(Base):
    __tablename__ = "nodes"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    collection_id: Mapped[str] = mapped_column(String(36), ForeignKey("collections.id", ondelete="CASCADE"), nullable=False)
    template_id: Mapped[str] = mapped_column(String(36), nullable=False)
    parent_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    base_for: Mapped[str] = mapped_column(String(20), nullable=False)
    fields: Mapped[str] = mapped_column(String, nullable=False, server_default="{}")
    data: Mapped[str] = mapped_column(String, nullable=False, server_default="{}")
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="Active")
    created_at: Mapped[int] = mapped_column(BigInteger, nullable=False)
    updated_at: Mapped[int] = mapped_column(BigInteger, nullable=False)
    deleted_at: Mapped[int | None] = mapped_column(BigInteger, nullable=True)

    
class LearningUnitORM(Base):
    __tablename__ = "learning_units"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    node_id: Mapped[str] = mapped_column(String(36), ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False)
    unit_type: Mapped[str] = mapped_column(String(20), nullable=False)
    position: Mapped[int] = mapped_column(BigInteger, nullable=False, server_default="0")
    due: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    last_review: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    unit_data: Mapped[str] = mapped_column(String, nullable=False, server_default="{}")


class ReviewORM(Base):
    __tablename__ = "reviews"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    node_id: Mapped[str] = mapped_column(String(36), ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[int] = mapped_column(BigInteger, nullable=False)
    time: Mapped[int] = mapped_column(BigInteger, nullable=False)
    duration: Mapped[int] = mapped_column(BigInteger, nullable=False)
    type_review_data: Mapped[str] = mapped_column(String, nullable=False, server_default="{}")
    node_state_before: Mapped[str | None] = mapped_column(String, nullable=True)

    __table_args__ = (
        Index("idx_reviews_node", "node_id"),
    )

    
class IdempotencyKeyORM(Base):
    __tablename__ = "idempotency_keys"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    response_body: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[int] = mapped_column(BigInteger, nullable=False)
