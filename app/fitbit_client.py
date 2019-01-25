import base64
from contextlib import contextmanager

import fitbit
import requests
import pdb
from app.models import save_fitbit_token
from config import get_current_config

# These grant permissions for your app to access user data.
# Ask for as little as possible
# Details https://dev.fitbit.com/docs/oauth2/
SCOPES = [
    'profile',
   'activity',
   'heartrate',
   'location',
   'nutrition',
   'settings',
   'sleep',
   'social',
   'weight'
]


"""
Helper method to get fitbit client ID and client secret
"""
@contextmanager
def fitbit_client(fitbit_credentials):
    config = get_current_config()
    client = fitbit.Fitbit(
        config.FITBIT_CLIENT_ID,
        config.FITBIT_CLIENT_SECRET,
        access_token=fitbit_credentials.access_token,
        refresh_token=fitbit_credentials.refresh_token
    )
    yield client
    # Save in case we did some refreshes
    
    save_fitbit_token(
        fitbit_credentials.user_id,
        client.client.token['access_token'],
        client.client.token['refresh_token']
    )

"""
Generate permission screen link for fitbit
"""

def get_permission_screen_url():
    return ('https://fitbit.com/oauth2/authorize'
            '?response_type=code&client_id={client_id}&scope={scope}').format(
        client_id=get_current_config().FITBIT_CLIENT_ID,
        scope='%20'.join(SCOPES)
    )


"""
Helper method to get fitbit tokens
"""
def get_token():
    config = get_current_config()
    return base64.b64encode(
        "{}:{}".format(
            config.FITBIT_CLIENT_ID,
            config.FITBIT_CLIENT_SECRET
        ).encode('utf-8')
    ).decode('utf-8')


"""
Generate authorization screen link for fitbit
"""
def get_auth_url(code):
    return 'https://api.fitbit.com/oauth2/token?code={code}&client_id={client_id}&grant_type=authorization_code&expires_in=31536000'.format(
        code=code,
        client_id=get_current_config().FITBIT_CLIENT_ID
    )

"""
Helper method to handle fitbit authorization 
"""
def do_fitbit_auth(code, user):
    r = requests.post(
        get_auth_url(code),
        headers={
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Basic {}'.format(get_token()),
        }
    )
    
    r.raise_for_status()
    response = r.json()
    
    return save_fitbit_token(
        user.id,
        response['access_token'],
        response['refresh_token']
    )

"""
Helper method for subscription
"""
def do_subscription(subscription_id, subscriber_id):
    fitbit.Fitbit.subscription(subscription_id, subscriber_id)
