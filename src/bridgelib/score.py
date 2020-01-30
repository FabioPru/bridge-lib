from functools import lru_cache
from .constants import *

import numpy as np

# Source for bridge scoring constants: http://www.rpbridge.net/2y66.htm

penalties = {0: [[(-50) * i for i in range(13)],
             [(-100) * i for i in range(13)]],

             1: [[-100, -300, -500] + [-800 - 300*i for i in range(10)],
             [-200] + [-500 - 300*i for i in range(12)]],

             2: [[-200, -600, -1000] + [-1600 - 600*i for i in range(10)],
             [-400] + [-1000 - 600*i for i in range(12)]]}

base_scores = {0: [[[0, 60, 60, 310, 310, 310, 810, 1310],
               [0, 50, 50, 50, 300, 300, 800, 1300],
               [0, 50, 50, 50, 50, 300, 800, 1300]],
               
               [[0, 60, 60, 510, 510, 510, 1260, 2010],
               [0, 50, 50, 50, 500, 500, 1250, 2000],
               [0, 50, 50, 50, 50, 500, 1250, 2000]]], 

               1: [[[0, 80, 290, 250, 210, 170, 630, 1090],
               [0, 60, 270, 230, 190, 150, 610, 1070],
               [0, 40, -20, 170, 110, 50, 490, 930]],
               
               [[0, -20, 290, 150, 10, -130, 480, 1090],
               [0, -40, 270, 130, -10, -150, 460, 1070],
               [0, -60, -220, 70, -90, -250, 340, 930]]],

               2: [[[0, 360, 280, 200, 120, 40, 440, 880],
               [0, 320, 240, 160, 80, 0, 420, 840],
               [0, 30, 160, 40, -80, -200, 180, 560]],
               
               [[0, 360, 80, -200, -480, -760, -290, 180],
               [0, 320, 40, -240, -520, -800, -330, 140],
               [0, -170, -40, -360, -680, -1000, -570, -140]]]}

incr = {0: [[30, 30, 20], [30, 30, 20]],
        1: [[100] * 3, [200] * 3],
        2: [[200] * 3, [400] * 3]}

@lru_cache(maxsize=8192)
def score_contract(contract, made=0, vul=0):
    contr = Contract(contract)
    if contr == Contract.PASS: return 0

    dbl = contr.dbl()
    diff = int(made) - contr.level()
    s_i = (Strain(contr.strain()).value + 1) // 2 #0: NT, 1: maj, 2: minor

    if diff < 0:
        return penalties[dbl][vul][-diff]
    else:
        return made * incr[dbl][vul][s_i] + base_scores[dbl][vul][s_i][contr.level()]

@lru_cache(maxsize=8192)
def score_array(contract, vul=0):
    return np.array([score_contract(contract, made, vul) for made in range(-6, 8)])

#score_contract('1NT', 3, 0)
#    output: 150

IMPscale = [15, 45, 85, 125, 165, 215, 265, 315, 365, \
            425, 495, 595, 745, 895, 1095, 1295, 1495, \
            1745, 1995, 2245, 2495, 2995, 3495, 3995, 99999]

@lru_cache(maxsize=8192)
def points_to_IMPs(pt_diff):
    if pt_diff < 0:
        return -points_to_IMPs(-pt_diff)
    for j in range(0, len(IMPscale)):
        if pt_diff < IMPscale[j]:
            return j

#points_to_IMPs(score_contract('3NT', 3, 0) - score_contract('1NT', 3, 0))
#    output: 6

@lru_cache(maxsize=8192)
def reverse_score(contract, points, vul):
    for made in range(-6, 8):
        if score_contract(contract, made, vul) == points:
            return made
    return None
