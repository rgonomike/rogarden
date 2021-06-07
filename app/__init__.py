from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_admin import Admin
from flask_bootstrap import Bootstrap
import RPi.GPIO as GPIO


app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
admin = Admin(app, name='Rogarden', template_mode='bootstrap3')


from app import routes, models, errors

from app.models import Relay

# Force relay to stop in case of reboot
all_relays = Relay.query.all()
for relay in all_relays:
    # Checking pin state
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(relay.pin,GPIO.OUT)
    GPIO.output(relay.pin,1)
