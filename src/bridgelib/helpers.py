from .constants import *

from functools import lru_cache
import numpy as np

@lru_cache(maxsize=8192)
def decode_hex(x):
    if x == 'A':
        return 10
    if x == 'B':
        return 11
    if x == 'C':
        return 12
    if x == 'D':
        return 13
    return int(x)

dds_players = ['S', 'E', 'N', 'W']
def decode_winners(sol):
    wnrs = [{} for _ in range(0, len(strains))]
    for s_idx in range(len(strains)):
        wnrs[s_idx] = {dds_players[pl]: 13 - decode_hex(sol[4*s_idx + pl]) \
                        for pl in range(len(dds_players))}
    return wnrs

def array_from_solver_out(out_fragment):
    dds_out = decode_winners(out_fragment)

    array = np.zeros((4, 5, 14))
    for st_id in range(len(strains)):
        for pl_idx, pl_by in enumerate(players):
            wnrs = dds_out[st_id][pl_by]
            array[pl_idx][st_id][wnrs] = 1 

    return array


def hand_to_pbn(d):
    out = []
    for pl in 'NESW':
        for st in reversed(suits):
            out += d[pl][st]
            if st != 'c': out.append('.')
        if pl != 'W': out.append(' ')
    return ''.join(out)