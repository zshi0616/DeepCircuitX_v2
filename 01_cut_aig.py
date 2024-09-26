import numpy as np 
import glob 
import utils.aiger_utils as aiger_utils
import utils.circuit_utils as circuit_utils

def save_masked_circuit(region, bench_path, x_data, fanin_list, fanout_list):
    new_x_data = []
    new_PI = []
    new_PO = []
    # PI 
    for idx in region:
        is_PI = True
        for fanin in fanin_list[idx]:
            if fanin in region:
                is_PI = False
                break
            

if __name__ == '__main__':
    for aig_path in glob.glob('raw_aig/*.aig'):
        x_data, edge_index = aiger_utils.aig_to_xdata(aig_path)
        fanin_list, fanout_list = circuit_utils.get_fanin_fanout(x_data, edge_index)
        level_list = circuit_utils.get_level(x_data, fanin_list, fanout_list)
        
        # No need to extract subcircuits for the first 10 levels
        if len(level_list) < 10: