#!/usr/bin/python3
import random
import string

ERR_MSG_OAUTH = "error_description"
ERR_MSG = "error_message"
ERR_GENERIC = "error"
ERR_CODE = "error_code"
ERR_INVALID_CREDENTIALS = "Invalid credentials"
CLIENT_ATTR = "controlledClient"

def create_auth_header(token):
    return {"Authorization": "Bearer "+token}

def randomString(stringLength=30):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

def get_posible_errors(data):
    """ Gets errors (err_msg, err_code) from the data passed, or returns an empty string"""
    err_msg = ""
    err_code = ""

    if isinstance(data, list):
        for d in data:
            if ERR_MSG in d:
                err_msg = d[ERR_MSG]
                err_code = d.get(ERR_CODE,"")
                break
            if ERR_GENERIC in d:
                err_msg = d[ERR_GENERIC]
                err_code = ""
                break
    elif ERR_MSG in data:
        err_msg = data[ERR_MSG]
        err_code = data.get(ERR_CODE,"")
    elif ERR_GENERIC in data:
        err_msg = data[ERR_GENERIC]
        err_code = ""

    return err_msg, err_code