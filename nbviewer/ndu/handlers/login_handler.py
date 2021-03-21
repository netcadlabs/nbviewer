import json

import jwt
import requests

from nbviewer.ndu.handlers.ndu_base_handler import NDUBaseHandler


class LoginHandler(NDUBaseHandler):
    def get_pattern(self):
        return r"/login/?(.*)"

    def render_login_template(self, **other):
        return self.render_template(
            "login.html",
            title=self.frontpage_setup.get("title", None),
            subtitle=self.frontpage_setup.get("subtitle", None),
            text=self.frontpage_setup.get("text", None),
            show_input=self.frontpage_setup.get("show_input", True),
            **other
        )

    def get(self, *path_args, **path_kwargs):
        query_token = self.get_argument('token', None)
        if query_token:
            try:
                result = jwt.decode(query_token, options={"verify_signature": False})
                if 'TENANT_ADMIN' in result['scopes']:
                    self.set_secure_cookie(self.token_cookie_name, query_token)
                    self.redirect("/notebooks/")
            except Exception as err:
                print(err)
        else:
            current_user = self.check_token(redirect_login=False)
            if current_user:
                self.redirect("/notebooks")
                return None

        result = self.render_login_template()

        self.finish(result)

    def post(self, *path_args, **path_kwargs):
        email = self.get_argument('email', default=None)
        password = self.get_argument('password', default=None)

        try:
            token_data = self.ndu_login(email, password)
            self.set_secure_cookie(self.token_cookie_name, token_data['token'])
            self.redirect("/notebooks/")
        except ValueError as err:
            print(err)
            result = self.render_login_template()
            self.finish(result)

    def ndu_login(self, email, password):
        url = self.ndu_base_url + '/api/auth/login'
        body = {
            'username': email,
            'password': password
        }

        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.post(url, data=json.dumps(body), headers=headers)

        if response.status_code == 200:
            return json.loads(response.text)
        else:
            raise ValueError('login failed')
