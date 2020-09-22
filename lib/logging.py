from colorama import Fore, Back, Style
from enum import IntEnum

class LogLevel(IntEnum):
    FATAL = 0
    ERROR = 1
    WARNING = 2
    INFO = 3
    DEBUG = 4
    TRACE = 5

loglevel = LogLevel.TRACE

def log_console(level, source, message):

    # Level
    lvstr = "UNK"

    if level == LogLevel.FATAL:
        lvstr = Fore.RED + Style.BRIGHT + "FTL" + Style.RESET_ALL + Fore.RESET
    elif level == LogLevel.ERROR:
        lvstr = Fore.RED + "ERR" + Fore.RESET
    elif level == LogLevel.WARNING:
        lvstr = Fore.YELLOW + "WRN" + Fore.RESET
    elif level == LogLevel.INFO:
        lvstr = "INF"
    elif level == LogLevel.DEBUG:
        lvstr = Fore.BLUE + "DBG" + Fore.RESET
    elif level == LogLevel.TRACE:
        lvstr = Fore.GREEN + "TRC" + Fore.RESET

    # Source
    if type(source) is str:
        pass
    else:
        source = type(source).__name__

    # Print
    print("[%s] %s: %s" % (lvstr, source, message))

def get_log_level():
    return loglevel

def set_log_level(level):
    log(LogLevel.INFO, "Logging", "Log level set to %s." % level)
    loglevel = level

def log(level, source, message):
    if int(level) > int(loglevel):
        return

    log_console(level, source, message)

def trace(source, message):
    log(LogLevel.TRACE, source, message)

def debug(source, message):
    log(LogLevel.DEBUG, source, message)

def info(source, message):
    log(LogLevel.INFO, source, message)

def warn(source, message):
    log(LogLevel.WARNING, source, message)

def error(source, message):
    log(LogLevel.ERROR, source, message)

def fatal(source, message):
    log(LogLevel.FATAL, source, message)

class Logger:
    def __init__(self, component):
        self.component = component

    def trace(self, message):
        trace(self.component, message)

    def debug(self, message):
        debug(self.component, message)

    def info(self, message):
        info(self.component, message)

    def warn(self, message):
        warn(self.component, message)

    def error(self, message):
        error(self.component, message)

    def fatal(self, message):
        fatal(self.component, message)
