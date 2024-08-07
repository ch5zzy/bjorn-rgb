from requests import get, head


def import_unicorn(sim=False):
    if sim:
        from unicorn_hat_sim import unicornhathd as unicorn
    else:
        import unicornhathd as unicorn
    return unicorn


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


def hex_to_rgb(hex: str):
    return tuple(int(hex[_ : _ + 2], 16) for _ in (0, 2, 4))
