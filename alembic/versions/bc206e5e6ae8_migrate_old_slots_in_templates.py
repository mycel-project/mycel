"""migrate old slots in templates

Revision ID: bc206e5e6ae8
Revises: d1001fbf0b72
Create Date: 2026-06-28 15:24:53.602218

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bc206e5e6ae8'
down_revision: Union[str, Sequence[str], None] = 'd1001fbf0b72'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


import json

def upgrade() -> None:
    """Upgrade schema."""
    connection = op.get_bind()
    users = connection.execute(sa.text("SELECT id, templates FROM users")).fetchall()
    
    for user_id, templates_json in users:
        if not templates_json:
            continue
        try:
            templates = json.loads(templates_json)
        except json.JSONDecodeError:
            continue
            
        modified = False
        for template_id, template in templates.items():
            if template.get("kind") == "spore_standard" and "render_config" in template:
                new_render_config = {}
                for slot_str, struct in template["render_config"].items():
                    if slot_str.isdigit():
                        new_slot = int(slot_str) + 1
                        new_render_config[str(new_slot)] = struct
                        modified = True
                    else:
                        new_render_config[slot_str] = struct
                template["render_config"] = new_render_config
        
        if modified:
            new_json = json.dumps(templates)
            connection.execute(
                sa.text("UPDATE users SET templates = :new_templates WHERE id = :id"),
                {"new_templates": new_json, "id": user_id}
            )

def downgrade() -> None:
    """Downgrade schema."""
    connection = op.get_bind()
    users = connection.execute(sa.text("SELECT id, templates FROM users")).fetchall()
    
    for user_id, templates_json in users:
        if not templates_json:
            continue
        try:
            templates = json.loads(templates_json)
        except json.JSONDecodeError:
            continue
            
        modified = False
        for template_id, template in templates.items():
            if template.get("kind") == "spore_standard" and "render_config" in template:
                new_render_config = {}
                for slot_str, struct in template["render_config"].items():
                    if slot_str.isdigit():
                        new_slot = int(slot_str) - 1
                        new_render_config[str(new_slot)] = struct
                        modified = True
                    else:
                        new_render_config[slot_str] = struct
                template["render_config"] = new_render_config
        
        if modified:
            new_json = json.dumps(templates)
            connection.execute(
                sa.text("UPDATE users SET templates = :new_templates WHERE id = :id"),
                {"new_templates": new_json, "id": user_id}
            )
