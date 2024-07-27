from requests import get, head


def safe_get(url: str):
    response = None
    try:
        response = get(url)
    except:
        pass
    return response


def check_wifi():
    try:
        head("https://example.com").raise_for_status()
    except:
        return False

    return True
