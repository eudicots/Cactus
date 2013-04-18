#coding:utf-8


def parse_site_variable(var):
    """
    Basic parsing of site variables. If the variables contains an "=" use a
    key=value format. Otherwise, use as a flag and set the value to True

    Returns (key, value)
    """
    try:
        k, v = var.split('=', 1)
    except ValueError:
        return var, True
    else:
        return k, v