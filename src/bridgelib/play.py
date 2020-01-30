import os
import numpy as np
from functools import lru_cache

from .constants import *
from .helpers import array_from_solver_out
from .score import score_contract, reverse_score
from .base import Deal

DDS_SOLVER_DIR = __file__[:-22] + '/dds-master/examples/'

class PlayResult():
    '''Holds a Deal and a (4, 5, 14)-shape np.array with probabilities of tricks taken in each suit by each decl'''

    def __init__(self, deal, array):
        self.deal = deal
        if array.shape != (4, 5, 14): raise ValueError("Wrong shape supplied")
        self.a = array

    def __getitem__(self, key):
        # Takes a pair (strain, list of players). (strain, None) or (strain,) returns avg
        if not isinstance(key, tuple):
            key = (key, 'NSEW')
        try: 
            iter(key[1])
            pl_lst = key[1]
        except:
            pl_lst = [key[1]]

        st = Strain(key[0]).value
        pls = [Player(pl).value for pl in pl_lst]
        return self.a[pls, st].mean(axis=0)

    def _tricks(self, strain, pl_by=None):
        return self[strain, pl_by].idxmax()

# --- Double-Dummy solver
@lru_cache(maxsize=8192)
def dds_solver(pbn):
    """Takes a pbn of the form 'AKJ852.AKT3..KT9 T3.Q62.5.AQJ8763 Q764.98754.J872. 9.J.AKQT9643.542' """
    os.system('echo \"1\n' + pbn + '\n\" > ' + DDS_SOLVER_DIR + 'myd.txt')
    out = os.popen('cd ' + DDS_SOLVER_DIR + '; ./CalcAllTablesPBN < myd.txt').read()
    if not out:
        print("""Instructions to get DDS to work:
            (You might have to install Boost C+ if not already present)
            First, move to the dds-master/src dir
            copy and rename the appropriate makefile from the Makefile directory
            run make, then run make install
            Then, move to the dds-master/examples directory
            copy the appropriate makefile, then make""")
        raise ValueError("DDS not working: check if it exists at address\n" + DDS_SOLVER_DIR)
    return out

class DDSResult(PlayResult):

    def __init__(self, deal):
        
        solver_out = dds_solver(deal.pbn)
        array = array_from_solver_out(solver_out[70:90])
        return super().__init__(deal, array)

    @classmethod
    def fromline(cls, line):
        return PlayResult(Deal(line[2:69]), array_from_solver_out(line[70:90]))

# --- From scraped ACBL pages

def proba_from_reslist(lst, vul):
    taken = []
    for t in lst:
        try:
            if t[2] in 'NS': taken.append(6 + reverse_score(t[1], t[0], vul[0]))
            else: taken.append(7 - reverse_score(t[1], -t[0], vul[1]))
        except:
            pass

    array = np.zeros(14)
    for tricks in taken:
        array[tricks] += 1
    if len(taken) > 0:
        return array / len(taken)
    return None

class LiveResult(PlayResult):
    '''On top of the double dummy, replaces tricks taken by what
        happened during play. Also, matchpoints scoring'''

    def __init__(self, deal, res_list):
        # Compute array from result list
        self.res_list = sorted(res_list)
        solver_out = dds_solver(deal.pbn)
        self.dds_array = array_from_solver_out(solver_out[70:90])

        array = self.dds_array.copy()
        for s_idx, s in enumerate(strains):
            s_list = [t for t in self.res_list if s in t[1]]
            avg_array = proba_from_reslist(s_list, deal.vul)
            if avg_array is not None:
                for p_idx, pl in enumerate(players):
                    pl_array = proba_from_reslist([t for t in s_list if pl in t[2]], deal.vul)

                    if pl_array is not None: array[p_idx][s_idx] = pl_array
                    else: array[p_idx][s_idx] = avg_array

        return super().__init__(deal, array)

    def _mp(self, points):
        '''Return the matchpoint score (between 0 and 1) for the NS side'''
        return (len([t for t in self.res_list if t[0] < points]) + 
          0.5 * len([t for t in self.res_list if t[0] == points])) / len(self.res_list)

    @lru_cache(maxsize=8192) 
    def mp_contract(self, contract, vul=0, pl_by='NS'):
        '''Returns the matchpoints for the NS side if final contract is contract played by'''
        contr = Contract(contract)
        if contr == Contract.PASS: return self._mp(0)
        proba = self[contr.strain(), pl_by]

        mp_mean = 0
        for i, p in enumerate(proba):
            if pl_by in 'EW':
                print(-score_contract(contr, 7 - i, vul))
                mp_mean += p * self._mp(-score_contract(contr, 7 - i, vul))
            else:
                mp_mean += p * self._mp(score_contract(contr, i - 6, vul))
        return mp_mean

    def to_file(self):
        return self.deal.pbn, self.deal.dlr, self.deal.vul, self.dds_array, self.a, self.res_list

    @classmethod
    def from_file(cls, pbn, dlr, vul, dds_a, a, res_list):
        self = cls.__new__(cls)
        self.deal = Deal(pbn, dealer=dlr, vul=vul)
        self.a = a
        self.res_list = res_list
        self.dds_array = dds_a
        return self
