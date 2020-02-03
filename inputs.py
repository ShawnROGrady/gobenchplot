X_NAME = 'x'
Y_NAME = 'y'
GROUP_BY_NAME = 'group-by'
FILTER_BY_NAME = 'filter-by'
SUBS_NAME = 'subs'


class InvalidInputError(Exception):
    def __init__(self, reason: str, input_names, input_val=None):
        self.reason = reason
        self.input_names = input_names
        self.input_val = input_val

    def __str__(self):
        msg = ""
        if self.input_val is None:
            msg = "invalid {}: {}".format(self.input_names, self.reason)
        else:
            msg = "invalid {} - '{}': {}".format(self.input_names,
                                                 self.input_val, self.reason)
        return "InvalidInputError: %s" % (msg)
