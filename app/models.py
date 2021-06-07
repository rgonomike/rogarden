from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from sqlalchemy import event

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
    
schedules_relays = 'schedules_relays'
relationship_tables = {
    schedules_relays: db.Table(schedules_relays,
                          db.Column('relay_id', db.Integer(), db.ForeignKey('relay.id')),
                          db.Column('schedule_id', db.Integer(), db.ForeignKey('schedule.id'))
                          )
}


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '{}'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)	


class Area(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140))
    description = db.Column(db.String(140))
    last_watering_dt = db.Column(db.DateTime, index=True)
    relays = db.relationship('Relay', backref='area', lazy='dynamic')

    def __repr__(self):
        return '{}'.format(self.name)

	
class Relay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140))
    pin = db.Column(db.Integer)
    state = db.Column(db.Integer)
    last_start_dt= db.Column(db.DateTime, index=True)
    last_stop_dt= db.Column(db.DateTime, index=True)
    last_run_duration = db.Column(db.String(140))
    area_id = db.Column(db.Integer, db.ForeignKey('area.id'))
    schedules = db.relationship('Schedule', secondary=relationship_tables[schedules_relays],
                                backref=db.backref('relays', lazy='dynamic'),
                                order_by="Schedule.name")

    def __repr__(self):
        return '{}'.format(self.name)


class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    start = db.Column(db.String(255))
    end = db.Column(db.String(255))
    active = db.Column(db.Boolean(), default=False)

    def __repr__(self):
        return '{} ({} - {})'.format(self.name, self.start, self.end)
        
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "start": self.start,
            "end": self.end,
            "active": self.active,
        }    
        
        

class Sensor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140))
    pin = db.Column(db.Integer)
    area_id = db.Column(db.Integer, db.ForeignKey('area.id'))

    def __repr__(self):
        return '{}'.format(self.name)


class Appconfig(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255))
    description = db.Column(db.String(255))
    value = db.Column(db.String(255))

    def __repr__(self):
        return '{} '.format(self.name)
               
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "active": self.value,
        }  
