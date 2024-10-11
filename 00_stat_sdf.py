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

ff_keys = ['dfrtp','sky130_fd_sc_hd__edfxtp_1', 'dfrtn', 'dfxtp', 'dfbbn', 'dlrtp', 'einvn', 'dlxtp', 'dfsbp', 'dfstp', 'edfxbp']

if __name__ == '__main__':
    cell_dict = circuit_utils.parse_genlib(genlib_path)
    sdf_list = glob.glob(os.path.join(raw_dir, '*/*.sdf'))
    tot_time = 0
    graphs = {}
    f = open('stat_sdf.csv', 'w')
    f.write("Circuit,Succ,Input,Output,FFs,Nds,Lev\n")
    
    for sdf_k, sdf_path in enumerate(sdf_list):
        # if 'RISC16BitProcessor' not in sdf_path:
        #     continue
        
        start_time = time.time()
        circuit_name = sdf_path.split('/')[-2]
        if not os.path.exists(sdf_path):
            f.write('{},{},{},{},{},{},{}\n'.format(
                circuit_name, 0, 0, 0, 0, 0, 0
            ))
            continue
        
        # Parse SDF 
        x_data, edge_index, fanin_list, fanout_list = parse_sdf(sdf_path)
        
        if len(x_data) == 0:
            f.write('{},{},{},{},{},{},{}\n'.format(
                circuit_name, 0, 0, 0, 0, 0, 0
            ))
            continue
            
        no_pi = 0
        no_po = 0
        no_ff = 0
        for idx in range(len(x_data)):
            if len(fanin_list[idx]) > 0 and len(fanout_list[idx]) == 0:
                no_po += 1
            if len(fanin_list[idx]) == 0 and len(fanout_list[idx]) > 0:
                no_pi += 1
            is_ff = False
            for ff_key in ff_keys:
                if ff_key in x_data[idx][1]:
                    is_ff = True
                    break
            if is_ff:
                no_ff += 1
            
        f.write('{},{},{},{},{},{},{}\n'.format(
            circuit_name, 1, no_pi, no_po, no_ff, len(x_data), 0
        ))
        
        # Statistics
        print('Parse: {} ({:} / {:}), Size: {:}, Time: {:.2f}s, ETA: {:.2f}s'.format(
            circuit_name, sdf_k, len(sdf_list), len(x_data), 
            tot_time, tot_time / ((sdf_k + 1) / len(sdf_list)) - tot_time
        ))
        tot_time += time.time() - start_time
    f.close()