import re

def ensure_email_validation(email_address):
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    email_as_str = str(email_address)
    if re.match(regex, email_as_str) is None:
        return False
    return True

