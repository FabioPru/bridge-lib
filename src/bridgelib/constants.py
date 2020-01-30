suits = 'cdhs'
card_vals = 'AKQJT98765432'

strains = ['NT', 's', 'h', 'd', 'c']
levels = '01234567'

players = ['N', 'E', 'S', 'W'] # Must be in clockwise order

## --- Card class --- 

from enum import IntEnum, unique
from itertools import count

@unique
class MyEnum(IntEnum):
    '''Card(1), Card('sA'), Card.sA all are the same thing'''

    @classmethod
    def _missing_(cls, value):
        return cls.__getattr__(value)

Card = MyEnum('Card', zip([s+v for s in suits[::-1] for v in card_vals],
                        count()), module=__name__)
deck = [t for t in Card]

## --- Strains and Players helpers for indexing

Strain = MyEnum('Strain', zip(strains, count()), module=__name__)
Player = MyEnum('Player', zip(players, count()), module=__name__)

## --- Contract and Call classes

@unique
class ContractEnum(MyEnum):

    def strain(self):
        if self.name == 'PASS': return None
        return self.name.split('x')[0][1:]

    def level(self):
        if self.name == 'PASS': return None
        return int(self.name[0])

    def dbl(self):
        return self.name.count('x')

Contract = ContractEnum('Contract', zip(['PASS'] + [l + s + d for l in levels[1:] for s in strains[::-1] for d in ['', 'x', 'xx']], 
                                        count()), module=__name__)
contracts = [t for t in Contract]

Call = MyEnum('Call', zip(['PASS'] + [l + s for l in levels[1:] for s in strains[::-1]] + ['X', 'XX'], 
                            count()), module=__name__)
calls = [t for t in Call]
