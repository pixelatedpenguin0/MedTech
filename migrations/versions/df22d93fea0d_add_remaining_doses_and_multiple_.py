"""Add remaining doses and multiple reminders

Revision ID: df22d93fea0d
Revises: b152899a8682
Create Date: 2025-04-26 15:50:57.258051

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'df22d93fea0d'
down_revision = 'b152899a8682'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('medication', schema=None) as batch_op:
        batch_op.add_column(sa.Column('remaining_doses', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('medication', schema=None) as batch_op:
        batch_op.drop_column('remaining_doses')

    # ### end Alembic commands ###
