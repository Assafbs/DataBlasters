
def get_value_from_cookie(request, cookie_name):
    if cookie_name in request.cookies:
        value = request.cookies.get(cookie_name)
        if value != '':
            return value
        else:
            return None

