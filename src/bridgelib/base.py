import numpy as np
import random

from .constants import *

## --- Hand class ---

class Hand(tuple):
    '''Hand class. Hand() is a random hand. Cards are held sorted.'''

    def __new__(self, *args):
        if len(args) == 0:
            # Return random hand
            return Hand(random.sample(deck, len(deck) // 4))
        else:
            if isinstance(args[0], str):
                # From PBN
                new = [Card(s+c) for s, cds in zip(reversed(suits), args[0].split('.')) \
                            for c in cds]
            else:
                if len(args[0]) != len(deck) // 4: raise ValueError("Too many/few cards supplied ("+str(len(args[0]))+")")
                new = args[0]
            return super().__new__(self, sorted(new))

    def __repr__(self):
        return "Hand object with pbn: " + self.pbn

    memos = {'hcp', 'dist', 'pbn', 'mask'}
    def __getattr__(self, attr):
        if attr in Hand.memos:
            self.__setattr__(attr, self.__getattribute__('_'+attr)())
            return self.__getattribute__(attr)
        return super().__getattribute__(attr)

    def _hcp(self):
        hcp = 0
        for cd in self:
            if 0 <= int(cd) % len(card_vals) <= 3: hcp += 4 - (int(cd) % len(card_vals))
        return hcp

    def _dist(self):
        dist = [0, 0, 0, 0]
        for cd in self: dist[((cd-1) // 13)] += 1
        return tuple(dist)

    def _pbn(self):
        names = [Card(x).name for x in self]
        out_ch = []
        for su in reversed(suits):
            out_ch += [cd[1] for cd in names if cd[0] == su] + ['.']
        return ''.join(out_ch[:-1])

    def _mask(self):
        msk = np.zeros(len(deck))
        for cd in self: msk[int(cd)] = 1
        return msk

    def permute_suits(self, sh=0):
        # Permutes the suits in the order s -> h -> d -> c
        return Hand([((x - 1 + 13*sh) % len(deck)) + 1 for x in self])

    
## --- Deal class

class Deal(tuple):
    '''A deal is a tuple of four hand objects'''
    def __new__(self, *args, **kwargs):
        if len(args) == 0:
            # Return random deal
            sh_deck = deck.copy()
            random.shuffle(sh_deck)
            return Deal([Hand(sh_deck[13*t:13*(t+1)]) for t in range(4)])
        elif isinstance(args[0], str):
            return Deal([Hand(pbn) for pbn in args[0].split(' ')])
        elif len(args[0]) < 4:
            # Generate missing hands randomly
            for hd in args[0]: 
                if not isinstance(hd, Hand): raise ValueError("Arguments must be Hands")
            msk = np.ones(len(deck))
            for hd in args[0]: msk -= hd.mask
            remaining = [Card(i) for i in range(len(deck)) if msk[i] == 1]
            random.shuffle(remaining)
            if len(remaining) + 13 * len(args[0]) != 52: raise ValueError("Duplicate cards supplied")
            return Deal(args[0] + [Hand(remaining[13*t:13*(t+1)]) for t in range(4 - len(args[0]))])
        else:
            return super().__new__(self, args[0], **kwargs)

    def __init__(self, *args, dealer=None, vul=None):

        if dealer: self.dlr = dealer
        else: self.dlr = random.choice(players)

        if vul: self.vul = vul
        else: self.vul = (random.choice([0, 1]), random.choice([0, 1]))

    def __repr__(self):
        return "Deal object with pbn: " + self.pbn

    memos = {'pbn', 'mask', 'N', 'E', 'S', 'W'}
    def __getattr__(self, attr):
        if attr in Deal.memos:
            self.__setattr__(attr, self.__getattribute__('_'+attr)())
            return self.__getattribute__(attr)
        return super().__getattribute__(attr)

    def _pbn(self):
        return ' '.join([hd.pbn for hd in self])

    def _N(self): return self[0]
    def _E(self): return self[1]
    def _S(self): return self[2]
    def _W(self): return self[3]

    def _mask(self):
        return np.stack([hd.mask for hd in self])

    def from_NS(self, handN, handS):
        newd = Deal([handN, handS])
        return Deal([newd[0], newd[2], newd[1], newd[3]])

    def permute_suits(self, sh=0):
        # Permutes the suits in the order s -> h -> d -> c
        return Deal([hd.permute_suits(sh) for hd in self])

    def permute_players(self, sh=0):
        return Deal(self[(sh % 4):] + self[:(sh % 4)])

