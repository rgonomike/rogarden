# -*- coding: utf-8 -*-
from flask import render_template, flash, redirect, url_for, jsonify
from app import app, db, admin
from app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Relay, Area, Sensor, Appconfig, Schedule
from flask import request
from werkzeug.urls import url_parse
from flask_admin.contrib.sqla import ModelView
from crontab import CronTab
import RPi.GPIO as GPIO
import time
from datetime import datetime
import Adafruit_DHT

admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Relay, db.session))
admin.add_view(ModelView(Sensor, db.session))
admin.add_view(ModelView(Area, db.session))
admin.add_view(ModelView(Schedule, db.session))
admin.add_view(ModelView(Appconfig, db.session))


app_conf_json={}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form, appconfig=app_conf_json )


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/')
@app.route('/index')
@login_required
def index():
    app_conf = Appconfig.query.all()
    for i in app_conf:
        app_conf_json[i.name]=i.value
    # crontab init
    cron = CronTab(user='pi')
    cron.remove_all()
    cron.write()
    # relays setup
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    pins_relays={}
    all_relays = Relay.query.all()
    for relay in all_relays:
        pins_relays[relay.name] = {}
        pins_relays[relay.name]['pin']=relay.pin
        # Checking pin state
        GPIO.setup(relay.pin,GPIO.OUT)
        # GPIO.output(relay.pin,1)
        pins_relays[relay.name]['state'] = GPIO.input(relay.pin)
        pins_relays[relay.name]['last_start_dt']=relay.last_start_dt.strftime("%Y/%m/%d %H:%M:%S")
        pins_relays[relay.name]['last_stop_dt']=relay.last_stop_dt.strftime("%Y/%m/%d %H:%M:%S")
        pins_relays[relay.name]['schedules'] = {}
        for schedule in relay.schedules:
            pins_relays[relay.name]['schedules'][schedule.name] = schedule.serialize()
            # Crontab logic #
            # START #
            sched_start = cron.new(command='curl localhost:5000/relay/{}'.format(relay.name), comment='{}-{}'.format(schedule.id, relay.id))
            sched_start.setall('{m} {h} * * *'.format(h=schedule.start.split('h')[0], m=schedule.start.split('h')[1]))
            # END # 
            sched_end = cron.new(command='curl localhost:5000/relay/{}'.format(relay.name), comment='{}-{}'.format(schedule.id, relay.id))
            sched_end.setall('{m} {h} * * *'.format(h=schedule.end.split('h')[0], m=schedule.end.split('h')[1]))
            sched_start.enable(schedule.active)
            sched_end.enable(schedule.active)
            cron.write()
    return render_template('index.html', title='Home', relays=pins_relays, appconfig=app_conf_json )
 

@app.route('/register', methods=['GET', 'POST'])
def register():
    
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    app_conf = Appconfig.query.all()
    for i in app_conf:
        app_conf_json[i.name]=i.value
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form, appconfig=app_conf_json )    


@app.route('/forecast', methods=['GET', 'POST'])
def forecast():
    app_conf = Appconfig.query.all()
    for i in app_conf:
        app_conf_json[i.name]=i.value
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    # example: https://openweathermap.org/city/3030387    
    return render_template('weather_forecast.html', title='Weather Forecast', appconfig=app_conf_json )     


@app.route('/relay/<name>', methods=['GET'])
def switch_relay(name):
    # RELAY TESTS
    # Set up GPIO pins
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    pins_relays={}
    all_relays = Relay.query.all()
    for relay in all_relays:
        pins_relays[relay.name]= relay.pin

    result = {}
    now = datetime.now()
    pin=pins_relays[name]
    GPIO.setup(pin,GPIO.OUT)
    state = GPIO.input(pin)
    
    if state:
        GPIO.output(pin,0)
        relay = Relay.query.filter_by(name=name).first()
        relay.last_start_dt = now
        result['last_start_dt'] = now.strftime("%Y/%m/%d %H:%M:%S")
        result['last_stop_dt']=None
        result['last_run_duration']=None
        db.session.commit()
        print("{} turned on.".format(name))
    else:
        GPIO.output(pin,1)
        relay = Relay.query.filter_by(name=name).first()
        relay.last_stop_dt = now
        last_run_duration = str(now - relay.last_start_dt)
        relay.last_run_duration = last_run_duration
        result['last_stop_dt'] = now.strftime("%Y/%m/%d %H:%M:%S")
        result['last_start_dt']=relay.last_start_dt.strftime("%Y/%m/%d %H:%M:%S")
        result['last_run_duration']= last_run_duration
        db.session.commit()
        print("{} turned off. Runtime: {}".format(name, result['last_run_duration']))
    result['state'] = state
    
    return jsonify(result)
    
@app.route('/temp_sensor/<id>', methods=['GET'])    
def temp_sensor(id):
    # Temp/Hum sensor setup
    s = Adafruit_DHT.AM2302
    p = id
    fa_code, color  = '', ''
    result = {}
    humidity, temperature = Adafruit_DHT.read_retry(s,p)
    if temperature <= 10:
        fa_code, color = 'fa-thermometer-empty', 'deepskyblue'
    elif temperature > 10 and temperature <= 14:
        fa_code, color = 'fa-thermometer-2', 'orange'
    elif temperature > 14 and temperature <= 20:
        fa_code, color = 'fa-thermometer-3', 'orange'
    elif temperature > 20 and temperature <= 26:
        fa_code, color = 'fa-thermometer-full', 'red'
    else:
        fa_code, color = 'fa-fire', 'red'
    if temperature is not None and humidity is not None:
        result['temperature'] = '{0:0.1f}°C'.format(temperature)
        result['fa'] = '<i class="fa {}" aria-hidden="true" style="color:{}"></i> '.format(fa_code, color)
        result['humidity'] = '{0:0.1f}%'.format(humidity)    
    else:
         print('Ohoh')
    return jsonify(result)

    
@app.route('/moisture_sensor/<id>', methods=['GET'])    
def moisture_sensor(id):
    # Moisture sensor setup
    pin = int(id)
    GPIO.setmode(GPIO.BCM)  
    # Setup your channel
    GPIO.setup(pin, GPIO.IN)
    # To test the value of a pin use the .input method
    state = GPIO.input(pin)  # Returns 0 if OFF or 1 if ON
    return jsonify(state)

