from .constants import *

class Bidding(list):

    def __init__(self, *args, dlr='N'):
        '''Rebuilds the list manually to check for validity'''
        self.dlr = Player(dlr)
        self.lc = Call.PASS
        self.by = None
        self.dbl = ''

        ls = super().__init__()
        for a in args:
            self._append_args(a)

    def append(self, val):
        call = Call(val)
        if not self._is_legal(call):
            raise ValueError('Illegal Call: ' + call)

        if call == Call.X:
            self.dbl = 'x'
        elif call == Call.XX:
            self.dbl = 'xx'
        elif call != Call.PASS:
            self.lc = call; self.dbl = ''
            self.by = self._c_pl()

        return super().append(call)

    def _append_args(self, arg):
        '''Flattens in case args containts iterables'''
        try: 
            Call(arg)
        except:
            for val in arg: self.append(val)
        else:
            self.append(arg)

    def _is_legal(self, call):
        if call == Call.X:
            if self.dbl != '' or (self._c_pl() - self.by) % 2 == 0:
                return False
        elif call == Call.XX:
            if self.dbl != 'x' or (self._c_pl() - self.by) % 2 == 1:
                return False
        elif call != Call.PASS:
            if call <= self.lc:
                return False
        return True

    def _c_pl(self):
        return Player((len(self) + self.dlr.value) % 4)

    def _check_end(self):
        '''Returns True if the auction is over, else False'''
        if len(self) <= 3: return False
        return self[-1] == self[-2] == self[-3] == Call.PASS

    def _current_contract(self):
        '''Returns a Contract, Player pair'''
        return Contract(self.lc.name + self.dbl), self.by

    def __add__(self, other):
        self._append_args(other)
        return self

    def __iadd__(self, other):
        self._append_args(other)
        
    def __repr__(self):
        return f'Bidding({super().__repr__()})'

    def __str__(self):
        strs = ['|  N  |  E  |  S  |  W  |\n' + '-' * 25 + '\n|' + '     |' * self.dlr.value]
        for i, b in enumerate(self):
            strs.append('{:^5}'.format(b.name) + '|')
            if (i + self.dlr.value) % 4 == 3:
                strs.append('\n|')
        return ''.join(strs)

# --- Strategy class

class Strategy():

    def __init__(self, fn):
        '''Initialized by speficying a function (Hand, Bidding) -> Call'''
        self.fn = fn

    def __call__(self, hd, bd):
        return self.fn(hd, bd)

# --- Sample Strategies

class ConstantStrategy(Strategy):

    def __init__(self, bid):
        '''If the constant bid is legal, make it'''
        call = Call(bid)
        def const_fn(hd, bd):
            if bd._is_legal(call):
                return call
            return Call.PASS

        super().__init__(const_fn)

class PassStrategy(ConstantStrategy):
    def __init__(self):
        super().__init__('PASS')
