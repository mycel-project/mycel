"""add content_format default to markdown for all nodes

Revision ID: cf1359ee4c55
Revises: bc206e5e6ae8
Create Date: 2026-08-20 23:52:34.771473

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cf1359ee4c55'
down_revision: Union[str, Sequence[str], None] = 'bc206e5e6ae8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


import json

def upgrade() -> None:
    """Upgrade schema."""
    connection = op.get_bind()
    nodes = connection.execute(sa.text("SELECT id, data FROM nodes")).fetchall()

    for node_id, data_json in nodes:
        if not data_json:
            continue
        try:
            data = json.loads(data_json)
        except json.JSONDecodeError:
            continue

        if "content_format" in data:
            continue
        
        data["content_format"] = "markdown"
        
        new_data = json.dumps(data)

        connection.execute(
            sa.text("UPDATE nodes SET data = :new_data WHERE id = :id"),
            {"new_data": new_data, "id": node_id}
        )

def downgrade() -> None:
    """Downgrade schema."""
    connection = op.get_bind()
    nodes = connection.execute(sa.text("SELECT id, data FROM nodes")).fetchall()
    
    for node_id, data_json in nodes:
        if not data_json:
            continue
        try:
            data = json.loads(data_json)
        except json.JSONDecodeError:
            continue
        
        if "content_format" not in data:
            continue  
        
        data.pop("content_format")
        connection.execute(
            sa.text("UPDATE nodes SET data = :new_data WHERE id = :id"),
            {"new_data": json.dumps(data), "id": node_id}
        )
