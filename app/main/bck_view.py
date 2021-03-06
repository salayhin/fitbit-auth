import flask_login
import sqlalchemy
from fitbit.exceptions import BadResponse
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import logout_user, login_required, login_user
from flask import abort, make_response

from app import db
from app.fitbit_client import fitbit_client, get_permission_screen_url, do_fitbit_auth, do_subscription
from app.main.forms import RegistrationForm, LoginForm
from app.models import User, get_user_fitbit_credentials
from . import main
from pprint import pprint
import pandas as pd
import json
from pandas.io.json import json_normalize
from datetime import datetime, date, timedelta
import pdb


@main.route('/do_subscription', methods=['GET'])
def do_subscription():
    if not flask_login.current_user.is_authenticated:
        return redirect(url_for('main.login'))
    else:
        fitbit_creds = get_user_fitbit_credentials(flask_login.current_user.id)
        data = ''
        if fitbit_creds:
            with fitbit_client(fitbit_creds) as client:
                try:
                    profile_response = client.user_profile_get()
                    user_profile = "{} has been on fitbit since {}".format(
                        profile_response['user']['fullName'],
                        profile_response['user']['memberSince']
                    )


                    ls = client.subscription(str(flask_login.current_user.id), '200', collection='activities')

                except BadResponse:
                    flash("Api Call Failed")
                    
        return render_template('do_subscription.html',  data= ls)   
        

@main.route('/list_subscriptions', methods=['GET'])
def list_subscription():
    if not flask_login.current_user.is_authenticated:
        return redirect(url_for('main.login'))
    else:
        fitbit_creds = get_user_fitbit_credentials(flask_login.current_user.id)
        data = ''
        if fitbit_creds:
            with fitbit_client(fitbit_creds) as client:
                try:
                    profile_response = client.user_profile_get()
                    user_profile = "{} has been on fitbit since {}".format(
                        profile_response['user']['fullName'],
                        profile_response['user']['memberSince']
                    )


                    ls = client.list_subscriptions()

                except BadResponse:
                    flash("Api Call Failed")
                    
        return render_template('list-subscriptions.html',  data= ls)          


@main.route('/', methods=['GET', 'POST'])
def index():
    if not flask_login.current_user.is_authenticated:
        return redirect(url_for('main.login'))
    else:
        user_profile = "Could not access fitbit profile"
        ls = 'Subscription List is Empty!'
        data = ''
        fitbit_creds = get_user_fitbit_credentials(flask_login.current_user.id)
        if fitbit_creds:
            with fitbit_client(fitbit_creds) as client:
                try:
                    
                    profile_response = client.user_profile_get()
                    user_profile = "{} has been on fitbit since {}".format(
                        profile_response['user']['fullName'],
                        profile_response['user']['memberSince']
                    )

                    #client.subscription(flask_login.current_user.id, '100')
                    #ls  = client.time_series('activities/calories', period='1y')
                    #ls = client.activity_stats()
                    #ls = client.list_subscriptions()
                    #pprint(ls)
                    #data = ls['activities-calories']
                    
                except BadResponse:
                    
                    flash("Api Call Failed")
        return render_template('index.html', user_profile=user_profile, permission_url=get_permission_screen_url())


@main.route('/oauth-redirect', methods=['GET'])
@login_required
def handle_redirect():
    code = request.args.get('code')
    do_fitbit_auth(code, flask_login.current_user)
    return redirect(url_for('main.index'))


@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    status = 200
    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.validate(form.password.data):
            login_user(user)
            flash('Logged in successfully.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid Credentials')
            status = 401
    return render_template('login.html', form=form), status


@main.route("/logout")
@login_required
def logout():
    logout_user()
    flash('Logged Out')
    return redirect(url_for('main.login'))


@main.route('/register', methods=['GET', 'POST'])
def register():
    
    form = RegistrationForm(request.form)
    status = 200
    if request.method == 'POST' and form.validate():
        user = User(
            form.username.data,
            form.password.data
        )
        
        try:
            print(db.session.add(user))
            db.session.add(user)
            db.session.commit()
            
            flash('Thanks for registering')
            return redirect(url_for('main.login'))
        except sqlalchemy.exc.IntegrityError:
            pdb.set_trace()
            db.session.rollback()
            flash('Username {} already taken'.format(form.username.data))
            status = 400

    return render_template('register.html', form=form), status


@main.route('/refresh_token')
def refresh_token():
    if not flask_login.current_user.is_authenticated:
        return redirect(url_for('main.login'))
    else:
        user_profile = "Could not access fitbit profile"
        ls = 'Subscription List is Empty!'
        data = ''
        fitbit_creds = get_user_fitbit_credentials(flask_login.current_user.id)
        if fitbit_creds:
            with fitbit_client(fitbit_creds) as client:
                try:
                    
                    profile_response = client.user_profile_get()
                    user_profile = "{} has been on fitbit since {}".format(
                        profile_response['user']['fullName'],
                        profile_response['user']['memberSince']
                    )
                    
                except BadResponse:
                    
                    flash("Api Call Failed")
        return render_template('index.html', user_profile=user_profile, permission_url=get_permission_screen_url())
    

@main.route('/api_subscriptions')
def api_subscription():
    return redirect(url_for('main.login'))
