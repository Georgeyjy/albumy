import uuid

import PIL
import os
from urllib.parse import urlparse, urljoin

from PIL import Image
from flask import request, redirect, current_app, flash
from itsdangerous import JSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature

from albumy.models import User
from albumy.extensions import db
from albumy.settings import Operation


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and test_url.netloc == ref_url.netloc


def redirect_back(default='main.index', **kwargs):
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(default, **kwargs)


def generate_token(user, operation, expire_in=None, **kwargs):
    s = Serializer(current_app.config['SECRET_KEY'], expire_in)

    data = {'id': user.id, 'operation': operation}
    data.update(**kwargs)
    return s.dumps(data)


def validate_token(user, token, operation, new_password=None):
    s = Serializer(current_app.config['SECRET_KEY'])

    try:
        data = s.loads(token)
    except (SignatureExpired, BadSignature):
        return False

    if operation != data.get('operation') or user.id != data.get('id'):
        return False

    if operation == Operation.CONFIRM:
        user.confirmed = True
    elif operation == Operation.CHANGE_EMAIL:
        new_email = data.get('new_email')
        if User.query.filter_by(email=new_email).first():
            return False
        if new_email is None:
            return False
        user.email = new_email
    elif operation == Operation.RESET_PASSWORD:
        user.password_hash = user.set_password(new_password)
    else:
        return False

    db.session.commit()
    return True


def resize_image(image, filename, width):
    filename, ext = os.path.splitext(filename)
    img = Image.open(image)
    if img.size[0] < width:
        return filename + ext
    resize_percentage = (width / float(img.size[0]))
    resized_hight = int(float(img.size[1]) * float(resize_percentage))
    img = img.resize((width, resized_hight), PIL.Image.ANTIALIAS)

    filename += current_app.config['ALBUMY_PHOTO_SUFFIX'][width] + ext
    img.save(os.path.join(current_app.config['ALBUMY_UPLOAD_PATH'], filename), optimize=True, quality=85)
    return filename


def rename_image(old_filename):
    ext = os.path.splitext(old_filename)[1]
    new_filename = uuid.uuid4().hex + ext
    return new_filename


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ))
