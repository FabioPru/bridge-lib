from requests import get
from bs4 import BeautifulSoup
import pickle

from .constants import *
from .helpers import hand_to_pbn
from .play import LiveResult
from .base import Deal, Hand

def write_one_tournament():
    with open(__file__[:-9] + '../../data/tournament_urls.txt') as f:
        lines = f.readlines()

    url = lines[0][:-1]
    print("Scraping " + url[20:])
    out = scrape_ACBL_tournament(url) # Remove trailing newline

    filename = url[url.index('event')+6:].replace('/', '_')
    if out:
        print("     Writing to file " + filename + ".pkl")
        with open(__file__[:-9] + '../../data/tournaments/' + filename + '.pkl', 'wb') as pickle_out:
            pickle.dump([lr.to_file() for lr in out], pickle_out)
    with open(__file__[:-9] + '../../data/tournament_urls.txt', "w") as f:
        for line in lines[1:]:
            f.write(line)

# For this file only, we need different constants
ACBL_pl = ['N', 'W', 'E', 'S']
ACBL_suits = ['s', 'h', 'd', 'c']
vul_map = {'Vul: None': (0, 0), 'Vul: N-S': (1, 0), 'Vul: E-W': (0, 1), 'Vul: Both': (1, 1)}

def scrape_ACBL_tournament(url: str):
    '''Sample usage: scrape_ACBL_tournament('http://live.acbl.org/event/YNABC162/YPRS/1/summary')
    Returns a list of PlayResult objects for future analysis
    '''
    out = scrape_page(url)
    out_dls = []
    for hd, rlist, vul, dlr in zip(out['hands'], out['results'], out['vul'], out['dlr']):
        new_r = []
        for r in rlist:
            try:
                spl_r = [s for s in r.strip().split(' ') if s] # remove empty space
                spl_r[3], spl_r[4] # eliminates some empty entries
                new_r.append((int(spl_r[2]), spl_r[0], spl_r[1]))
            except:
                pass
        if len(new_r) > 0:
            deal = Deal([Hand(st) for st in hand_to_pbn(hd).split(' ')], dealer=dlr, vul=vul)
            out_dls.append(LiveResult(deal, new_r))
    return out_dls

def hands_from_divlist(lst):
    spns = lst[0].find_all('span')[::2] + lst[1].find_all('span')[::2] + lst[2].find_all('span')[::2]
    if len(spns) != 16:
        raise ValueError("Invalid number of hands")
    hnd = {p: {s: [] for s in ACBL_suits} for p in ACBL_pl}
    for i, s in enumerate(spns):
        txt = s.text.replace('10', 'T').replace(' —', '') # T and void
        hnd[ACBL_pl[int(i // 4)]][ACBL_suits[int(i % 4)]] = txt.split(' ')[1:]
    return hnd

def scrape_page(url: str):

    response = get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    soups = [soup]
    try:
        section_items = soup.find('ul', class_='sections').find_all('a')[1:]
        for s in section_items:
            try:
                new_url = url + '?section=' + str(s.text)
                response = get(new_url)
                soups.append(BeautifulSoup(response.text, 'html.parser'))
            except:
                pass
    except:
        pass
    print("Scrapped a total of " + str(len(soups)) + " sections")
    
    bds = soups[0].find_all('div', class_='board-data')[::2]
    bds_info = soups[0].find_all('div', class_='board-data')[1::2]
    tbls = [s.find_all('table', class_='board-results-table')[::2] for s in soups]
    print("Analzing " + str(len(bds)) + " boards")
    hds = {'hands': [], 'dlr': [], 'vul': [],
           'results': []}
    for bd_no, (b, bi) in enumerate(zip(bds, bds_info)):
        try:
            h_hands = hands_from_divlist(b.find_all('div', class_='hand'))
            h_dlr = bi.find('span').text[-1]
            h_vul = vul_map[bi.find_all('span')[1].text]
            h_res = []
        
            for t in tbls:
                try:
                    r_lst = t[bd_no].find_all('tr')[1:]

                    for r in r_lst:
                        try:
                            txt = ' '.join([str(x) for x in r.find_all('td') if len(str(x)) < 100]).replace('<td>', '').replace('</td>', '')
                            for sn in ['spades', 'hearts', 'diams', 'clubs']:
                                txt = txt.replace('<span class="'+sn+' symbol contract"></span>', sn[0])
                            
                            h_res.append(txt)
                        except:
                            pass
                except IndexError: # board was not played in this session
                    pass

            hds['hands'].append(h_hands)
            hds['dlr'].append(h_dlr)
            hds['vul'].append(h_vul)
            hds['results'].append(h_res)
        except:
            pass #Somethign went wrong
            
    return hds

