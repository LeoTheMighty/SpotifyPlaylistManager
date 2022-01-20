DEBUG_PREFIX = '[DEBUG] '

class Log:
    def __init__(self, if_debug):
        self.if_debug = if_debug

    def debug(s):
        if self.if_debug:
            print(DEBUG_PREFIX + s)




