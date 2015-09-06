#coding:utf-8
from __future__ import print_function
from six.moves import urllib
from six.moves import input


class InvalidInput(Exception):
    """
    Raised when an input is invalid.
    You should use this in your `coerce_fn` passed to `prompt`, to indicate that the
    input you received was no valid.
    """
    def __init__(self, reason=""):
        self.reason = reason


def prompt(q, coerce_fn=None, error_msg="Invalid input, please try again", prompt_fn=input):
    """
    :param q: The prompt to display to the user
    :param coerce_fn: A function to coerce, and validate, the user input.
        You may raise InvalidInput in it, to indicate that the input was not valid.
    :param error_msg: An error message to display if the input is incorrect
    :return: The user's input
    :rtype: str
    """
    if coerce_fn is None:
        coerce_fn = lambda x:x

    while 1:
        r = prompt_fn(q + " > ")
        try:
            return coerce_fn(r)
        except InvalidInput as e:
            print(e.reason or error_msg)


_yes_no_mapping = {"y":True, "n":False}
def _yes_no_coerce_fn(r):
    """
    :rtype: bool
    """
    try:
        return _yes_no_mapping[r.lower()]
    except KeyError:
        raise InvalidInput("Please enter `y` or `n`")

def prompt_yes_no(q):
    """
    :param q: The prompt to display to the user
    :return: True of False
    :rtype : bool
    """
    return prompt(q + " [y/n]", _yes_no_coerce_fn)


def _normalized_coerce_fn(r):
    """
    :rtype: str
    """
    return r.lower().strip()

def prompt_normalized(q):
    """
    :param q: The prompt to display to the user
    :returns: The user's normalized input
    :rtype: str
    """
    return prompt(q, _normalized_coerce_fn)


def _url_coerce_fn(r):
    """
    :rtype: str
    """
    p = urllib.parse.urlparse(r)
    if not p.scheme:
        raise InvalidInput("Specify an URL scheme (e.g. http://)")
    if not p.netloc:
        raise InvalidInput("Specify a domain (e.g. example.com)")
    if p.path and p.path != "/":
        raise InvalidInput("Do not specify a path")
    if p.params or p.query or p.fragment:
        raise InvalidInput("Do not leave trailing elements")

    if not p.path:
        r += "/"  #TODO: Fixme once the sitemap is fixed!
    r = r.lower()

    return r


def prompt_url(q):
    """
    :param q: The prompt to display to the user
    :return: The user's normalized input. We ensure there is an URL scheme, a domain, a "/" path,
        and no trailing elements.
    :rtype: str
    """
    return prompt(q, _url_coerce_fn)
