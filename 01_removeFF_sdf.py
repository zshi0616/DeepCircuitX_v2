import os 
import glob 
from torch_geometric.data import Data, InMemoryDataset
import deepgate as dg 
import torch
import random
import time
import threading
import copy
import numpy as np 

from utils.utils import run_command, hash_arr
from parse_graph import parse_sdf
import utils.circuit_utils as circuit_utils

raw_dir = './data/raw_data'
# genlib_path = 'genlib/sky130.csv'
genlib_path = './genlib/sky130.csv'

ff_keys = ['dfrtp','dfbbp', 'dfrtn', 'dlxbp', 'dfxtp', 'dfbbn', 'dlrtp', 'einvn', 'dlxtp', 'dfsbp', 'dfstp', 'dfxbp']

if __name__ == '__main__':
    cell_dict = circuit_utils.parse_genlib(genlib_path)
    sdf_list = glob.glob(os.path.join(raw_dir, '*/*.sdf'))
    tot_time = 0
    graphs = {}
    
    for sdf_k, sdf_path in enumerate(sdf_list):
        # if 'RISC16BitProcessor' not in sdf_path:
        #     continue
        
        start_time = time.time()
        circuit_name = sdf_path.split('/')[-2]
        if not os.path.exists(sdf_path):
            print('[ERROR] File not found: {}'.format(sdf_path))
            continue
        
        # Parse SDF 
        x_data, edge_index, fanin_list, fanout_list = parse_sdf(sdf_path)
        if len(x_data) < 5 or len(edge_index) < 5:
            print('[ERROR] Empty graph: {}'.format(sdf_path))
            continue
        
        # Remove FF, convert seq to comb 
        x_data, edge_index, fanin_list, fanout_list = circuit_utils.seq_to_comb(x_data, fanin_list, ff_keys=ff_keys)
        
        # Check loop
        loop = circuit_utils.find_loop(fanout_list)
        if len(loop) > 0:
            print('Loop: ', loop)
            for idx in range(len(x_data)):
                is_comb_cell = False
                if x_data[idx][1] == 'PI':
                    continue
                for cell_name in cell_dict.keys():
                    if x_data[idx][1] == cell_name:
                        is_comb_cell = True
                        break
                if not is_comb_cell:
                    raise('FF Cell Name: {}'.format(x_data[idx][1]))
            print('[ERROR] Has loop: {}'.format(sdf_path))
            continue
        
        ###################################################
        # @ Chengyu: Output circuit graph to .v for ABC
        ###################################################
        
        
        
        # Statistics
        print('Parse: {} ({:} / {:}), Size: {:}, Time: {:.2f}s, ETA: {:.2f}s'.format(
            circuit_name, sdf_k, len(sdf_list), len(x_data), 
            tot_time, tot_time / ((sdf_k + 1) / len(sdf_list)) - tot_time
        ))
        tot_time += time.time() - start_time