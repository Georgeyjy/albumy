from sqlite3 import IntegrityError
from faker import Faker

from albumy import User
from albumy.extensions import db


def fake_admin():
    fake = Faker()
    admin = User(
        name='Yang',
        username='yangjianyu',
        email='george_yjy@163.com',
        bio=fake.sentence(),
        website='http://123.com',
        confirmed=True
    )
    admin.set_password('123456')
    db.session.add(admin)
    db.session.commit()


def fake_users(count=10):
    fake = Faker()
    for _ in range(count):
        user = User(
            name=fake.name(),
            confirmed=True,
            username=fake.user_name(),
            bio=fake.sentence(),
            location=fake.city(),
            website=fake.url(),
            member_since=fake.date_this_decade(),
            email=fake.email()
        )
        user.set_password('123456')
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

