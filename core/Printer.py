import imsciutils as iu


def get_printer(name, log_level='info'):
    """
    creates or retrieves a printer object
    """
    if name in Printer.ACTIVE_PRINTERS:
        return Printer.ACTIVE_PRINTERS[name]
    else:
        return Printer(name, log_level)


def whitelist_printer(name):
    """
    whitelisted the given printer

    only whitelisted printers will print to the terminal
    """
    # remove from blacklist if it's currently on it
    if name in Printer.BLACKLIST:
        Printer.BLACKLIST.remove(name)

    # append to Whitelist if it's not already on there
    if name not in Printer.WHITELIST:
        if Printer.WHITELIST == 'all':
            Printer.WHITELIST = []
        Printer.WHITELIST.append(name)


def blacklist_printer(name):
    """
    Blacklists the given printer

    When a printer is blacklisted, it will not print out to the terminal
    """
    # remove from whitelist if it currently exists
    if name in Printer.WHITELIST:
        Printer.WHITELIST.remove(name)

    # add to blacklist if it's not already in there
    if name not in Printer.BLACKLIST:
        Printer.BLACKLIST.append(name)


def disable_printout_colors():
    """disables colored printouts for imsciutils printout messages"""
    Printer.ENABLE_COLOR = False


def enable_printout_colors():
    """enables colored printouts for imsciutils printout messages"""
    Printer.ENABLE_COLOR = True


def get_active_printers():
    """gets a list of the names of currently active printers"""
    return sorted(list(Printer.ACTIVE_PRINTERS.keys()))

def set_global_printout_level(log_level):
    """
    sets the global log level
    input:
        log_level (int,str):
            the log level to set the global log level

    return:
        None
    """
    if log_level in Printer.LOG_LEVELS:
        log_level = Printer.LOG_LEVELS[log_level]

    if not isinstance(log_level,(int,float)):
        iu.error("unable to set log_level to {}, must be an integer".format(log_level))
        return

    Printer.GLOBAL_LOG_LEVEL = log_level


class Printer(object):
    """
    Object used to print out messages to the terminal for a given
    process or object. This is meant to increase traceability particularly
    for people who are developing imsciutils

    Each message printed out using this object is automatically colorized,
    filtered for the current log level, and prefixed

    """
    ACTIVE_PRINTERS = {}
    LOG_LEVELS = {
        'debug': 10,
        'info': 20,
        'warning': 30,
        'error': 40,
        'critical': 50,
        'comment': 60,
    }
    GLOBAL_LOG_LEVEL = 0
    WHITELIST = 'all'
    BLACKLIST = []
    ENABLE_COLOR = True
    MAX_NAME_SIZE = 32

    def __init__(self, name, log_level='info'):
        if log_level in self.LOG_LEVELS:
            log_level = self.LOG_LEVELS[log_level]

        self.__error_check(name, log_level)

        self.name = name
        self.log_level = log_level

        buf = ' ' * ((MAX_NAME_SIZE - len(self.name)) // 2)
        self.level_text = {
            'debug':   '({1}{0}{1})[    DEBUG   ]'.format(self.name, buf),
            'info':    '({1}{0}{1})[    INFO    ]'.format(self.name, buf),
            'warning': '({1}{0}{1})[   WARNING  ]'.format(self.name, buf),
            'error':   '({1}{0}{1})[    ERROR   ]'.format(self.name, buf),
            'critical':'({1}{0}{1})[  CRITICAL  ]'.format(self.name, buf),
            'comment': '({1}{0}{1})[  COMMENT  ]'.format(self.name, buf),
        }

        self.ACTIVE_PRINTERS[self.name] = self

    def __error_check(self, name, log_level):
        """
        Error checks the Printer Instantiation Args
        """
        if not isinstance(log_level, (int, float)):
            raise TypeError(
                "'log_level' must be an integer or float, currently {}".format(type(log_level)))

        if not isinstance(name, str):
            raise TypeError("'name' of Printer must be a string")

    def debug(self, *messages):
        """
        prints out objects at debug level for this printer
        input:
            *messages (unpacked args):
                objects or messages to print out at debug level
        return:
            None
        """
        if not should_print('debug', *messages):
            return

        prefix = self.level_text['debug']
        if ENABLE_COLOR:
            prefix = iu.util.blue(prefix)
            messages = [iu.util.blue(str(msg)) for msg in messages]

        print(prefix, *messages)

    def info(self, *messages):
        """
        prints out objects at info level for this printer
        input:
            *messages (unpacked args):
                objects or messages to print out at info level
        return:
            None
        """
        if not should_print('info', *messages):
            return

        prefix = self.level_text['info']
        if ENABLE_COLOR:
            prefix = iu.util.blue(prefix)
            messages = [iu.util.blue(str(msg)) for msg in messages]

        print(prefix, *messages)

    def warning(self, *messages):
        """
        prints out objects at warning level for this printer
        input:
            *messages (unpacked args):
                objects or messages to print out at warning level
        return:
            None
        """
        if not should_print('warning', *messages):
            return

        prefix = self.level_text['warning']
        if ENABLE_COLOR:
            prefix = iu.util.yellow(prefix)
            messages = [iu.util.yellow(str(msg)) for msg in messages]

        print(prefix, *messages)

    def error(self, *messages):
        """
        prints out objects at error level for this printer
        input:
            *messages (unpacked args):
                objects or messages to print out at error level
        return:
            None
        """
        if not should_print('error', *messages):
            return

        prefix = self.level_text['error']
        if ENABLE_COLOR:
            prefix = iu.util.red(prefix)
            messages = [iu.util.red(str(msg)) for msg in messages]

        print(prefix, *messages)

    def critical(self, *messages):
        """
        prints out objects at critical level for this printer
        input:
            *messages (unpacked args):
                objects or messages to print out at critical level
        return:
            None
        """
        if not should_print('critical', *messages):
            return

        prefix = self.level_text['critical']
        if ENABLE_COLOR:
            prefix = iu.util.red(prefix, bold=True)
            messages = [iu.util.red(str(msg), bold=True) for msg in messages]

        print(prefix, *messages)

    def comment(self, *messages):
        """
        prints out objects at comment level for this printer
        input:
            *messages (unpacked args):
                objects or messages to print out at comment level
        return:
            None
        """
        if not should_print('comment', *messages):
            return

        prefix = self.level_text['comment']
        if ENABLE_COLOR:
            prefix = iu.util.green(prefix, bold=True)
            messages = [iu.util.green(str(msg), bold=True) for msg in messages]

        print(prefix, *messages)

    def should_print(self, message_level, *messages):
        """
        Determines whether or not the given message level should print
        to the terminal
        """
        if message_level in LOG_LEVELS:
            message_level = LOG_LEVELS[message_level]

        # if message level is less than the global or local log_level
        if message_level < max(self.log_level, self.GLOBAL_LOG_LEVEL):
            return False

        # if printer is in the whitelist
        if self.WHITELIST != 'all':
            if self.name in self.WHITELIST:
                return True
            else:
                return False

        # if printer is in blacklist
        if self.BLACKLIST != []:
            if self.name not in self.BLACKLIST:
                return True
            else:
                return False

        return True

    def __del__(self):
        if self.name in self.ACTIVE_PRINTERS:
            del ACTIVE_PRINTERS[self.name]
