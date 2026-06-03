from sqlalchemy import Integer, String, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column
from src.db.schema import Base

# server_default instead of default: the DB handles the default value at the DDL level.
# This ensures raw SQL inserts (e.g. in tests) also benefit from the default, bypassing SQLAlchemy.

class UserORM(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[int] = mapped_column(Integer, nullable=False)
    conf: Mapped[str] = mapped_column(String, default="{}")


class CollectionORM(Base):
    __tablename__ = "collections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[int] = mapped_column(Integer, nullable=False)
    updated_at: Mapped[int] = mapped_column(Integer, nullable=False)
    conf: Mapped[str] = mapped_column(String, nullable=False, server_default="{}")
    fsrsconf: Mapped[str] = mapped_column(String, nullable=False, server_default="{}")


class NodeORM(Base):
    __tablename__ = "nodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    collection_id: Mapped[int] = mapped_column(Integer, ForeignKey("collections.id", ondelete="CASCADE"), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    type: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False, server_default="{}")
    created_at: Mapped[int] = mapped_column(Integer, nullable=False)
    updated_at: Mapped[int] = mapped_column(Integer, nullable=False)
    deleted_at: Mapped[int | None] = mapped_column(Integer, nullable=True)
    data: Mapped[str] = mapped_column(String, nullable=False, server_default="{}")
    type_data: Mapped[str] = mapped_column(String, nullable=False, server_default="{}")
    due: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_review: Mapped[int | None] = mapped_column(Integer, nullable=True)
    position: Mapped[str | None] = mapped_column(String, nullable=True)

    __table_args__ = (
        Index("idx_nodes_due", "due"),
        Index("idx_nodes_collection", "collection_id"),
    )


class ReviewORM(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    node_id: Mapped[int] = mapped_column(Integer, ForeignKey("nodes.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[int] = mapped_column(Integer, nullable=False)
    time: Mapped[int] = mapped_column(Integer, nullable=False)
    duration: Mapped[int] = mapped_column(Integer, nullable=False)
    type_review_data: Mapped[str] = mapped_column(String, nullable=False, server_default="{}")
    node_state_before: Mapped[str | None] = mapped_column(String, nullable=True)

    __table_args__ = (
        Index("idx_reviews_node", "node_id"),
    )
