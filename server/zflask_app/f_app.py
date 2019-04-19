from flask import Flask, render_template_string, redirect
from flask_security import Security, current_user, login_required, \
     SQLAlchemySessionUserDatastore, login_user, logout_user
from f_database import db_session, init_db
from f_models import User, Role

# Create app
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'super-secret'
# Bcrypt is set as default SECURITY_PASSWORD_HASH, which requires a salt
app.config['SECURITY_PASSWORD_SALT'] = 'super-secret-random-salt'

# Setup Flask-Security
user_datastore = SQLAlchemySessionUserDatastore(db_session,
                                                User, Role)
security = Security(app, user_datastore)

# Create a user to test with
@app.before_first_request
def create_user():
    init_db()
    user_datastore.create_user(email='matt2@nob.net', password='password')
    db_session.commit()

@app.route("/logout")
@login_required
def logout():
    # logout_user()
    return redirect("../index.html")

# Views
@app.route('/')
@login_required
def home():
    return render_template_string('Hello {{email}} !', email=current_user.email)

if __name__ == '__main__':
    app.run(port=5110)