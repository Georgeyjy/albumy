from flask import url_for

from albumy.extensions import db
from albumy.models import Notification


def push_follow_notification(follower, receiver):
    message = 'User <a href="{}">{}</a> followed you.'.format(
        url_for('user.index', username=follower.username), follower.username)
    notification = Notification(message=message, receiver=receiver)
    db.session.add(notification)
    db.session.commit()


def push_comment_notification(photo_id, receiver, page=1):
    message = 'New comment/reply in <a href="{}#comments">This photo</a>.'.format(
        url_for('main.show_photo', photo_id=photo_id, page=page))
    notification = Notification(message=message, receiver=receiver)
    db.session.add(notification)
    db.session.commit()


def push_collect_notification(collector, photo_id, receiver):
    message = 'User <a href="{}">{}</a> collected <a href="{}">your photo</a>.'.format(
        url_for('user.index', username=collector.username),
        collector.username,
        url_for('main.show_photo', photo_id=photo_id))
    notification = Notification(message=message, receiver=receiver)
    db.session.add(notification)
    db.session.commit()
