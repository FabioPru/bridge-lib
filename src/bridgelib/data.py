from .play import DDSResult, LiveResult
import pickle

def dds_resulter(l):
    if not l.startswith('N:'):
        return DDSResult.fromline('N:' + l)
    else:
        return DDSResult.fromline(l)

def gen_dds(max_no=None):
    with open(__file__[:-7] + '../../data/dds_deals.txt') as fp:
        i = 0
        while True:
            try:
                yield dds_resulter(fp.readline())
            except:
                break
            if max_no:
                i += 1
                if i >= max_no:
                    break

def read_dds(max_no=None):
    with open(__file__[:-7] + '../../data/dds_deals.txt') as fp:
        if max_no is not None:
            lines = fp.readlines(max_no * 89)
        else:
            lines = fp.readlines()
    return [dds_resulter(ln) for ln in lines]

def read_results_file(file_path):
    '''sample: tournaments/test.pkl'''

    with open(__file__[:-7] + '../../data/' + file_path, 'rb') as pickle_in:
        unpickled_list = pickle.load(pickle_in)
    return [LiveResult.from_file(*tf) for tf in unpickled_list]
