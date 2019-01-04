from flask import Blueprint, render_template

from albumy.utils import redirect_back

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('auth/register.html')


@auth_bp.route('/logout')
def logout():
    return redirect_back()
