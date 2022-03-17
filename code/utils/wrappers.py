from copy import deepcopy

class Dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
    def __init__(self, dct):
        for key, value in dct.items():
            if hasattr(value, 'keys'):
                value = Dotdict(value)
            self[key] = value
    def __deepcopy__(self, memo=None):
        return Dotdict(deepcopy(dict(self), memo=memo))

class Monad():
    def __init__(self, value, fail=False):
        self.value = value
        self.fail = fail
    def bind(self, value):
        if self.fail:
            return self
        else:
            try:
                return Monad(value)
            except:
                return Monad(None, True)
        return Monad()
    def __or__(self, next):
        return self.bind(next(self.value))
