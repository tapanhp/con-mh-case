""" Initial rev of database -- this should always be the first alembic version

Revision ID: 0000000
Revises: None
Create Date: 2014-10-28 14:14:45.896256

"""

# revision identifiers, used by Alembic.
revision = '00000000'
down_revision = None

from alembic import op


def upgrade():
    op.execute('''INSERT INTO user
        (username, email_address, display_name, signup_date)
        VALUES
            ('tester1', 'test@test.com', 'Chuck Norris', '2016-07-04'),
            ('tester2', 'test2@test.com', 'Elvis Presley', '2016-08-06'),
            ('tester3', 'test3@test.com', 'Justin Bieber', '2016-10-11')
    ''')

    op.execute('''INSERT INTO rel_user_multi (user_id, rel_lookup, attribute)
        VALUES
            (1, 'PHONE', '+14086441234'),
            (1, 'PHONE', '+14086445678'),
            (2, 'PHONE', '+14086551234')
    ''')

    op.execute('''INSERT INTO rel_user (user_id, rel_lookup, attribute)
        VALUES
            (3, 'LOCATION', 'USA'),
            (1, 'LOCATION', 'EUROPE')
    ''')


def downgrade():
    op.execute("TRUNCATE TABLE user")
    op.execute("TRUNCATE TABLE rel_user")
    op.execute("TRUNCATE TABLE rel_user_multi")
