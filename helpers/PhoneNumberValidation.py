import re

def is_valid_mobile(string):
    mobile_regex = "^09(1[0-9]|3[1-9])-?[0-9]{3}-?[0-9]{4}$"
    if re.search(mobile_regex, string):
        return True
    return False