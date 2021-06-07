from flask import render_template, redirect, url_for, current_app
from itsdangerous import BadSignature

from app import app, db


@app.errorhandler(401)
def unauthorized(error):
    from flask import session
    try:
        current_app.sm.invalidate_session()
        session.clear()
    except:
        pass
    return redirect(url_for('login'))


@app.errorhandler(BadSignature)
def bad_signature(error):
    from flask import session
    current_app.sm.invalidate_session()
    session.clear()
    return redirect(url_for('login'))


@app.errorhandler(404)
def not_found_error(error):
    try:
        return render_template('404.html'), 404
    except:
        pass
    return redirect(url_for('login'))


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
