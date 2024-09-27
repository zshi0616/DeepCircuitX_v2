import os 
import numpy as np 
import glob 
import utils.aiger_utils as aiger_utils
import utils.circuit_utils as circuit_utils

gate_to_index = {'PI': 0, 'AND': 1, 'NOT': 2}
save_path = './data/sub_bench'

def save_masked_circuit(region, bench_path, x_data, fanin_list, fanout_list):
    new_PI = []
    new_PO = []
    f = open(bench_path, 'w')
    # PI 
    for idx in region:
        is_PI = True
        for fanin in fanin_list[idx]:
            if fanin in region:
                is_PI = False
                break
        if is_PI:
            new_PI.append(idx)
    for idx in region:
        if not idx in new_PI:
            for fanin in fanin_list[idx]: 
                if not fanin in region:
                    new_PI.append(fanin)
    new_PI = list(set(new_PI))
    for idx in new_PI:
        f.write('INPUT({})\n'.format(idx))
    f.write('\n')
        
    # PO
    for idx in region:
        is_PO = True
        for fanout in fanout_list[idx]:
            if fanout in region:
                is_PO = False
                break
        if is_PO:
            new_PO.append(idx)
    for idx in new_PO:
        f.write('OUTPUT({})\n'.format(idx))
    f.write('\n')
    
    # Gates 
    for idx in region: 
        if idx not in new_PI:
            gate_name = x_data[idx][0]
            if x_data[idx][1] == gate_to_index['AND']:
                gate_type = 'AND'
            elif x_data[idx][1] == gate_to_index['NOT']:
                gate_type = 'NOT'
            new_line = '{} = {}('.format(gate_name, gate_type)
            for k, fanin in enumerate(fanin_list[idx]):
                if k == len(fanin_list[idx]) - 1:
                    new_line += '{})\n'.format(fanin)
                else:
                    new_line += '{}, '.format(fanin)
            f.write(new_line)
    f.close()
                
if __name__ == '__main__':
    if not os.path.exists(save_path):
        os.mkdir(save_path)
        
    for aig_path in glob.glob('./data/raw_aig/*.aig'):
        aig_name = aig_path.split('/')[-1].split('.')[0]
        x_data, edge_index = aiger_utils.aig_to_xdata(aig_path)
        fanin_list, fanout_list = circuit_utils.get_fanin_fanout(x_data, edge_index)
        level_list = circuit_utils.get_level(x_data, fanin_list, fanout_list)
        
        # No need to extract subcircuits for the first 10 levels
        if len(level_list) <= 5:
            output_path = os.path.join(save_path, '{}.bench').format(aig_name + '_0')
            region = list(range(len(x_data)))
            save_masked_circuit(region, output_path, x_data, fanin_list, fanout_list)
            
        