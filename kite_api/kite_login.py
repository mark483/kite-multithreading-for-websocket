import json

import requests
from kiteconnect import KiteConnect

KITE_LOGIN = 'https://kite.zerodha.com/api/login'
KITE_CONNECT = 'https://kite.trade/connect/login'
KITE_TWOFA = 'https://kite.zerodha.com/api/twofa'


class KiteLogin:
    def __init__(self, user_id, password,
                 api_key, kite_pin,
                 api_secret):
        self.api_secret = api_secret
        self.kite_pin = kite_pin
        self.api_key = api_key
        self.password = password
        self.user_id = user_id
        self.access_token = ''
        self.last_update = ''

        self._kite = KiteConnect(api_key)
        self._kite.set_session_expiry_hook(self.update_access_token)

    def get_client(self):
        return self._kite

    def init_session(self):
        self.get_request_token()

    def get_access_token(self):
        if not self.access_token:
            return self.update_access_token()

        return self.access_token

    def update_access_token(self):
        request_token = self._get_request_token()
        data = self._kite.generate_session(request_token, self.api_secret)
        self.access_token = data["access_token"]
        self._kite.set_access_token(self.access_token)
        return self.access_token
        # Try invalidate token

    def _get_request_token(self):
        with requests.Session() as s:
            r = s.post(KITE_LOGIN, data={'user_id': self.user_id, 'password': self.password})

            if not r.status_code == 200:
                raise Exception(r.text)
            # check if success
            request_id = json.loads(r.text)['data']['request_id']

            # Finish login process to do 2FA.
            _ = s.get(KITE_CONNECT, params={'api_key': self.api_key, 'skip_session': True})

            _ = s.post(KITE_TWOFA,
                       data={'user_id': self.user_id,
                             'request_id': request_id,
                             'twofa_value': self.kite_pin},
                       )

            resp = s.get(KITE_CONNECT, params={'api_key': self.api_key})
            return json.loads(resp.text)['token']

