import requests

ENDPOINT = "https://api.monobank.ua"
UAGENT = "python-monobank_handler"


def api_request(method, path, **kwargs):
    "Handles all HTTP requests for monobank_handler endponts"
    headers = kwargs.pop("headers")
    headers["User-Agent"] = UAGENT
    url = ENDPOINT + path
    # print(method, url, headers)
    response = requests.request(method, url, headers=headers, **kwargs)
    if response.status_code == 200:
        if not response.content:  # can be just empty an response, but it's fine
            return None
        return response.json()

    if response.status_code == 429:
        raise monobank_handler.TooManyRequests("Too many requests", response)

    data = response.json()
    message = data.get("errorDescription", str(data))
    raise monobank_handler.Error(message, response)
