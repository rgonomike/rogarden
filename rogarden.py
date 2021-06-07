from app import app, db
from app.models import User, Area, Relay, Sensor, Appconfig, Schedule

@app.shell_context_processor
def make_shell_context():
    return {'db': db,
    'User': User,
    'Area': Area, 
    'Relay': Relay,
    'Sensor': Sensor,
    'Schedule': Schedule,
    'Settings': Appconfig
    
    }