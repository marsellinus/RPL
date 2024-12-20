"""empty message

Revision ID: 36b4d6f04aa8
Revises: c74eae0348aa
Create Date: 2024-11-09 11:38:47.648639

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '36b4d6f04aa8'
down_revision = 'c74eae0348aa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('nisn', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('nama', sa.String(length=100), nullable=False))
        batch_op.add_column(sa.Column('classes_id', sa.Integer(), nullable=True))
        
        # Tambahkan nama constraint dengan eksplisit
        batch_op.create_unique_constraint(
            constraint_name='uq_user_nisn', 
            columns=['nisn']
        )
        batch_op.create_foreign_key(
            constraint_name='fk_user_classes', 
            referent_table='classes', 
            local_cols=['classes_id'], 
            remote_cols=['id']
        )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_constraint('fk_user_classes', type_='foreignkey')
        batch_op.drop_constraint('uq_user_nisn', type_='unique')
        batch_op.drop_column('classes_id')
        batch_op.drop_column('nama')
        batch_op.drop_column('nisn')

    # ### end Alembic commands ###