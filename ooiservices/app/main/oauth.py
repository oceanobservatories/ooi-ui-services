from rauth import OAuth1Service, OAuth2Service
from flask import current_app, url_for, request, redirect, session
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
        return url_for('.oauth_callback', provider=self.provider_name,
                       _external=True)

    @classmethod
    def get_provider(self, provider_name):
        if self.providers is None:
            self.providers = {}
            for provider_class in self.__subclasses__():
                provider = provider_class()
                self.providers[provider.provider_name] = provider
        return self.providers[provider_name]


class FacebookSignIn(OAuthSignIn):
    def __init__(self):
        super(FacebookSignIn, self).__init__('facebook')
        self.service = OAuth2Service(
            name='facebook',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url='https://graph.facebook.com/oauth/authorize',
            access_token_url='https://graph.facebook.com/oauth/access_token',
            base_url='https://graph.facebook.com/'
        )

    def authorize(self):
        return redirect(self.service.get_authorize_url(
            scope='email',
            response_type='code',
            redirect_uri=self.get_callback_url())
        )

    def callback(self):
        if 'code' not in request.args:
            return None, None, None
        oauth_session = self.service.get_auth_session(
            data={'code': request.args['code'],
                  'grant_type': 'authorization_code',
                  'redirect_uri': self.get_callback_url()}
        )
        me = oauth_session.get('me?fields=id,email').json()
        return (
            'facebook$' + me['id'],
            me.get('email').split('@')[0],  # Facebook does not provide
                                            # username, so the email's user
                                            # is used instead
            me.get('email')
        )


class TwitterSignIn(OAuthSignIn):
    def __init__(self):
        super(TwitterSignIn, self).__init__('twitter')
        self.service = OAuth1Service(
            name='twitter',
            consumer_key=self.consumer_id,
            consumer_secret=self.consumer_secret,
            request_token_url='https://api.twitter.com/oauth/request_token',
            authorize_url='https://api.twitter.com/oauth/authorize',
            access_token_url='https://api.twitter.com/oauth/access_token',
            base_url='https://api.twitter.com/1.1/'
        )

    def authorize(self):
        request_token = self.service.get_request_token(
            params={'oauth_callback': self.get_callback_url()}
        )
        session['request_token'] = request_token
        return redirect(self.service.get_authorize_url(request_token[0]))

    def callback(self):
        request_token = session.pop('request_token')
        if 'oauth_verifier' not in request.args:
            return None, None, None
        oauth_session = self.service.get_auth_session(
            request_token[0],
            request_token[1],
            data={'oauth_verifier': request.args['oauth_verifier']}
        )
        me = oauth_session.get('account/verify_credentials.json').json()
        social_id = 'twitter$' + str(me.get('id'))
        username = me.get('screen_name')
        return social_id, username, None   # Twitter does not provide email


class CILogonSignIn(OAuthSignIn):
    def __init__(self):
        super(CILogonSignIn, self).__init__('cilogon')
        self.service = OAuth2Service(
            name='cilogon',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url='https://test.cilogon.org/authorize',
            access_token_url='https://test.cilogon.org/oauth2/token',
            base_url='https://test.cilogon.org/'
        )

    def authorize(self):
        print 'Inside authorize'
        print self.get_callback_url()
        print 'Outside authorize'
        return redirect(self.service.get_authorize_url(
            scope='openid profile email',
            response_type='code',
            redirect_uri=self.get_callback_url())
        )

    def custom_decoder(self, x):
        print 'Inside custom_decoder'
        print x
        print 'Outside custom_decoder'
        return json.loads(str(x))

    def callback(self):
        print 'Begin callback'
        print self.get_callback_url()
        print request.args
        if 'code' not in request.args:
            return None, None, None
        print request.args['code'].rsplit('authzGrant', 1)[-1]
        print 'code: ' + str(request.args['code'])
        data = {'code': str(request.args['code']),
                'grant_type': 'authorization_code',
                'redirect_uri': self.get_callback_url()}
        print data

        oauth_session = self.service.get_auth_session(
            data=data
            ,
            decoder=self.custom_decoder
        )

        # return oauth_session.client_id
        me = oauth_session.client_id
        print 'me: ' + me
        print oauth_session.__attrs__

        me_profile = oauth_session.get('https://test.cilogon.org/oauth2/userinfo', params={'format': 'json'}).json()
        print me_profile
        print me_profile['email']

        print 'End callback'

        return me_profile['email'], me_profile['given_name'], me_profile['family_name']
        # me = oauth_session.get('me?fields=id,email').json()
        # return (
        #     'facebook$' + me['id'],
        #     me.get('email').split('@')[0],  # Facebook does not provide
        #                                     # username, so the email's user
        #                                     # is used instead
        #     me.get('email')
        # )
