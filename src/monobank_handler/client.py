from datetime import datetime, date, timedelta
from monobank_handler.utils import to_timestamp
from monobank_handler.signature import SignKey
from monobank_handler.transport import api_request
from monobank_handler.handler_utils import add_handler, CheckPayHandler
from monobank_handler.handler_utils import add_webhook_handler, Webhooks



class ClientBase(object):
    def _get_headers(self, url) -> dict:
        raise NotImplementedError("Please implement _get_headers")

    def make_request(self, method, path, **kwargs):
        headers = self._get_headers(path)
        return api_request(method, path, headers=headers, **kwargs)

    def pay_handler(self, amount=0, comment=None, may_be_bigger=True):
        """WORKING ONLY ONCE PER MINUTE!!\n
        ALSO WORKING IN POLL
        :return: pay_history"""
        def handler(func):
            assert amount >= 0, "amount may be bigger than 0"
            add_handler(func, amount, comment, may_be_bigger)
        return handler

    def pay_handler_webhook(self, amount=0, account=None, comment=None, may_be_bigger=True):
        """WORKING ONLY WITH SERVER!!\n
        running with await run_webhook()
        :return: pay_history"""
        def handler(func):
            assert amount >= 0, "amount may be bigger than 0"
            add_webhook_handler(func, amount, comment, may_be_bigger, account)
        return handler

    def pay_history(self, from_: str, account: str = "0", to: str = None, # path
                    time_: str = None, request_id: str = None, sign: str = None,  # header
                     ):
        ...
        if to:
            url = f"/personal/statement/{account}/{from_}/{to}"
        else:
            url = f"/personal/statement/{account}/{from_}"

        headers = self._get_headers(url)
        #   headers["X-Key-Id"] = key_id
        if time_:
            headers["X-Time"] = time_
        if request_id:
            headers["X-Request-Id"] = request_id
        if sign:
            headers["X-Sign"] = sign
        return api_request("GET", url, headers=headers)

    def get_currency(self):
        return self.make_request("GET", "/bank/currency")

    def get_client_info(self):
        return self.make_request("GET", "/personal/client-info")

    def get_statements(self, account, date_from, date_to=None):
        if date_to is None:
            date_to = date_from
        assert date_from <= date_to, "date_from must be <= date_to"
        if isinstance(date_to, date):
            # dates converted to timestamps of the same day but 00:00
            # which is not very practical
            # in that case we moving 24 hours ahead to include desired date:
            date_to += timedelta(days=1)
        t_from, t_to = to_timestamp(date_from), to_timestamp(date_to)

        url = f"/personal/statement/{account}/{t_from}/{t_to}"
        return self.make_request("GET", url)

    def create_webhook(self, url):
        return self.make_request("POST", "/personal/webhook", json={"webHookUrl": url, })


class Client(ClientBase, Webhooks, CheckPayHandler):
    """Personal API"""

    def __init__(self, token):
        self.token = token

    def _get_headers(self, url):
        return {
            "X-Token": self.token,
        }
    def run_webhook(self, url, port=3000, route="/webhook", host="0.0.0.0"):
        super(ClientBase, self).run_webhook(url, port, route, host)


class CorporateClient(ClientBase):
    """Corporate API"""

    def __init__(self, request_id, private_key):
        self.request_id = request_id
        self.key = SignKey(private_key)

    def _get_headers(self, url):
        headers = {
            "X-Key-Id": self.key.key_id(),
            "X-Time": str(to_timestamp(datetime.now())),
            "X-Request-Id": self.request_id,
        }
        data = headers["X-Time"] + headers["X-Request-Id"] + url
        headers["X-Sign"] = self.key.sign(data)
        return headers

    def check(self):
        "Checks if user approved access request"
        try:
            self.make_request("GET", "/personal/auth/request")
            return True
        except monobank_handler.Error as e:
            if e.response.status_code == 401:
                return False
            raise


def access_request(permissions, private_key, callback_url=None):
    "Creates an access request for corporate api user"
    key = SignKey(private_key)
    headers = {
        "X-Key-Id": key.key_id(),
        "X-Time": str(to_timestamp(datetime.now())),
        "X-Permissions": permissions,
    }
    if callback_url:
        headers["X-Callback"] = callback_url
    path = "/personal/auth/request"
    sign_str = headers["X-Time"] + headers["X-Permissions"] + path
    headers["X-Sign"] = key.sign(sign_str)
    return api_request("POST", path, headers=headers)
