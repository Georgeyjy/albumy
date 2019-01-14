import os

import click
from flask import Flask, render_template

from albumy.blueprints.ajax import ajax_bp
from albumy.blueprints.auth import auth_bp
from albumy.blueprints.main import main_bp
from albumy.blueprints.user import user_bp
from albumy.fakes import fake_comment, fake_collect, fake_photo, fake_tag, fake_follow
from albumy.models import User, Role
from albumy.settings import config
from albumy.extensions import db, bootstrap, login_manager, mail, moment, csrf, dropzone, avatars


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask('albumy')
    app.config.from_object(config[config_name])

    register_extensions(app)
    register_blueprints(app)
    register_shell_context(app)
    register_errorhandlers(app)
    register_commands(app)

    return app


def register_extensions(app):
    db.init_app(app)
    bootstrap.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    csrf.init_app(app)
    dropzone.init_app(app)
    avatars.init_app(app)


def register_blueprints(app):
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(ajax_bp, url_prefix='/ajax')


def register_shell_context(app):
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db, User=User)


def register_template_context(app):
    pass


def register_errorhandlers(app):
    @app.errorhandler(400)
    def bad_reuqest(e):
        return render_template('errors/400.html'), 400

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(413)
    def request_entity_too_large(e):
        return render_template('errors/413.html'), 413

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500


def register_commands(app):
    @app.cli.command()
    @click.option('--drop', is_flag=True)
    def initdb(drop):
        if drop:
            click.confirm('Confirm to delete database')
            db.drop_all()
            click.echo('Database deleted')
        db.create_all()
        click.echo('Initialized database')

    @app.cli.command()
    @click.option('--user', default=10)
    def forge(user):

        from albumy.fakes import fake_admin, fake_users

        db.drop_all()
        db.create_all()

        Role.init_role()
        fake_admin()
        fake_users(user)
        fake_tag()
        fake_photo()
        fake_comment()
        fake_collect()
        fake_follow()

        click.echo('Done')
