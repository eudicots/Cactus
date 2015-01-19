#coding:utf-8
from django.core.management.commands.makemessages import Command as MakeMessagesCommand
from django.core.management.commands.compilemessages import Command as CompileMessagesCommand

from cactus.utils.filesystem import chdir


DEFAULT_COMMAND_KWARGS = {
    # Command Options
    "verbosity": 3,
    "settings": None,
    "pythonpath": None,
    "traceback": True,
    "all": False,
}

DEFAULT_MAKEMESSAGES_KWARGS = {
    # MakeMessages Options: Default
    "domain": "django",
    "extensions": [],
    "ignore_patterns": [],
    "symlinks": False,
    "use_default_ignore_patterns": True,
    "no_wrap": False,
    "no_location": False,
    "no_obsolete": False,
    "keep_pot": False
}

def WrappedCommandFactory(wrapped, default_kwargs=None):
    # Compose a list of kwargs for future runs
    base_kwargs = {}
    base_kwargs.update(DEFAULT_COMMAND_KWARGS)
    if default_kwargs is not None:
        base_kwargs.update(default_kwargs)

    class WrappedCommand(object):
        """
        Wraps a Django management command
        """
        def __init__(self, site):
            self.site = site

        def execute(self):
            kwargs = {"locale": self.site.locale}
            kwargs.update(base_kwargs)

            cmd = wrapped()
            with chdir(self.site.path):
                cmd.execute(**kwargs)  # May raise an exception depending on gettext install.


    return WrappedCommand


MessageMaker = WrappedCommandFactory(MakeMessagesCommand, DEFAULT_MAKEMESSAGES_KWARGS)
MessageCompiler = WrappedCommandFactory(CompileMessagesCommand)
