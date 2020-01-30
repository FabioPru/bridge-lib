from .constants import *
from .base import Deal
from .bidding import Bidding, Strategy

from requests import get

ADDR = 'https://gibrest.bridgebase.com/u_bm/robot.php'

def find_bid(dl: Deal, bd=None):
    '''Returns the bid GIB would make for the given sequence and deal'''
    if bd is None:
        bd = Bidding(dlr=dl.dlr)

    dlr = bd.dlr.name
    pl = Player((len(bd) + bd.dlr.value) % 4).name
    vul = ''.join([side for bit, side in zip(dl.vul, ['NS', 'EW']) if bit])
    if vul == '': vul = '-'
    n = dl.N.pbn.lower()
    s = dl.S.pbn.lower()
    e = dl.E.pbn.lower()
    w = dl.W.pbn.lower()

    b_str = '-'.join([bid.name.replace('PASS', 'P').lower() for bid in bd])

    url = ADDR + f'?sc=tp&pov={pl}&d={dlr}&v={vul}&n={n}&s={s}&w={w}&e={e}&h={b_str}'

    out = get(url).text
    front_str = out[out.index('bid="')+5:]
    bid_str = front_str[:front_str.index('"')]
    if bid_str == 'P': bid_str = 'PASS'
    try:
        return Call(bid_str)
    except AttributeError:
        return Call(bid_str.lower())

class GIBStrategy(Strategy):

    def __init__(self):

        def gib_fn(hd, bd):
            c_pl = bd._c_pl().value
            dl = Deal([hd]).permute_players(sh=-c_pl) # Rotate counterclockwise
            return find_bid(dl, bd)

        super().__init__(gib_fn)

# Other available APIs to my knowledge:
# Prints all explanations of continuations of a sequence:
#   http://gibrest.bridgebase.com/u_bm/u_bm.php?t=g&s=P-P-P-1s-2n-*
# Card play: 
#   see https://github.com/Quantum64/GIBAccess/blob/master/js/bidding.js