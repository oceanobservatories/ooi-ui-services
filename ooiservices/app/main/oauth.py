from rauth import OAuth2Service
from flask import current_app, request, redirect
import json


class OAuthSignIn(object):
    providers = None

    def __init__(self, provider_name):
        self.provider_name = provider_name
        self.consumer_id = current_app.config['CILOGON_ID']
        self.consumer_secret = current_app.config['CILOGON_SECRECT']

    def authorize(self):
        pass

    def callback(self):
        pass

    def get_callback_url(self):
        return current_app.config['UI_URL'] + '/callback/cilogon'

    @classmethod
    def get_provider(self, provider_name):
        if self.providers is None:
            self.providers = {}
            for provider_class in self.__subclasses__():
                provider = provider_class()
                self.providers[provider.provider_name] = provider
        return self.providers[provider_name]


class CILogonSignIn(OAuthSignIn):
    def __init__(self):
        super(CILogonSignIn, self).__init__('cilogon')
        self.service = OAuth2Service(
            name='cilogon',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url = current_app.config['CILOGON_BASE_URL'] + '/authorize',
            access_token_url = current_app.config['CILOGON_BASE_URL'] + '/oauth2/token',
            base_url = current_app.config['CILOGON_BASE_URL']
        )

    def authorize(self):
        # print 'Inside authorize'
        # print self.get_callback_url()
        # print 'Outside authorize'
        return redirect(self.service.get_authorize_url(
            scope='openid profile email',
            response_type='code',
            redirect_uri=self.get_callback_url())+'&vo=ooi'
        )

    def custom_decoder(self, x):
        # print 'Inside custom_decoder'
        # print x
        # print 'Outside custom_decoder'
        return json.loads(str(x))

    def callback(self):
        debug = False
        if debug:
            print 'Begin callback'
            print(request.args)
        if 'code' not in request.args:
            return None, None, None
        if debug:
            print request.args['code'].rsplit('authzGrant', 1)[-1]
            print 'code: ' + str(request.args['code'])
        data = {'code': str(request.args['code']),
                'grant_type': 'authorization_code',
                'redirect_uri': self.get_callback_url()}
        if debug:
            print data

        oauth_session = self.service.get_auth_session(
            data=data,
            decoder=self.custom_decoder
        )

        # return oauth_session.client_id
        ci_logon_url = current_app.config['CILOGON_BASE_URL'] + '/oauth2/userinfo'
        me_profile = oauth_session.get(ci_logon_url,
                                       params={'format': 'json'}).json()
        if debug:
            print(me_profile)

        # Use the CILogon 'sub' returned as the unique user_id
        user_id = me_profile['sub']

        if debug:
            print(user_id)
            print 'End callback'

        return me_profile['email'], \
            me_profile['given_name'], \
            me_profile['family_name'], \
            user_id, \
            oauth_session.access_token

