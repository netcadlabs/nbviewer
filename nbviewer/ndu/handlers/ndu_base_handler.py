import uuid
from abc import abstractmethod

import jwt

from nbviewer.providers.base import BaseHandler


class NDUBaseHandler(BaseHandler):
    @property
    def token_cookie_name(self):
        return 'token'

    def is_authenticated(self):
        return self.check_token(False) is not None

    def check_token(self, redirect_login: bool = True) -> any:
        token = self.get_secure_cookie(self.token_cookie_name)

        if not token:
            if redirect_login:
                self.redirect("/login")
            return None

        # jwt.decode(token, "secret", algorithms=["HS256"])
        result = jwt.decode(token, options={"verify_signature": False})
        if not 'TENANT_ADMIN' in result['scopes']:
            return None

        return {
            'tenantId': result['tenantId'],
            'firstName': result['firstName'],
            'userId': result['userId'],
        }

    # def get_tenant_id(self):
    #     return 'test-tenant-id'

    def is_valid_uuid(self, val):
        try:
            uuid.UUID(str(val))
            return True
        except ValueError:
            return False

    @abstractmethod
    def get_pattern(self):
        pass
