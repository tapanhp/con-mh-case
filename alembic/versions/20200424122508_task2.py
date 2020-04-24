"""task2

Revision ID: a97b69cafde
Revises: 00000000
Create Date: 2020-04-24 12:35:08.309634

"""

# revision identifiers, used by Alembic.
revision = 'a97b69cafde'
down_revision = '00000000'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # TASK 2
    op.execute('''update user set point_balance = 5000 
        where 
        username = "tester1"
        ''')

    op.execute('''INSERT INTO rel_user (user_id, rel_lookup, attribute)
                VALUES
                    (2, 'LOCATION', 'USA')
            ''')

    op.execute('''update user set tier="Silver" 
        where username="tester3"
        ''')


def downgrade():
    pass
