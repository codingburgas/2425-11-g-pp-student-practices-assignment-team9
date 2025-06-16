"""Make user_id non-nullable

Revision ID: a66a06943692
Revises: 27f77abad8e5
Create Date: 2025-06-16 22:34:19.641758

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a66a06943692'
down_revision = '27f77abad8e5'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('survey') as batch_op:
        batch_op.alter_column('user_id',
                              existing_type=sa.Integer(),
                              nullable=False)

def downgrade():
    with op.batch_alter_table('survey') as batch_op:
        batch_op.alter_column('user_id',
                              existing_type=sa.Integer(),
                              nullable=True)


