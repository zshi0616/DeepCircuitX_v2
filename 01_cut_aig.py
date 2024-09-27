import os 
import numpy as np 
import random
import glob 
import utils.aiger_utils as aiger_utils
import utils.circuit_utils as circuit_utils
from utils.utils import hash_arr, run_command

gate_to_index = {'PI': 0, 'AND': 1, 'NOT': 2}
save_bench_path = './data/sub_bench'
save_aig_path = './data/sub_aig'

################################ Subcircuit Extraction ################################
size_range = [1000, 3000, 15000]        # min_size in range [a, b], max_size < c
level_range = [5, 20]                   # min_level, max_level 
no_circuits = 100                       # number of subcircuits to extract

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
    
def dfs_fanin_region(po_idx, stop_level, region, x_data, fanin_list):
    dfs_stack = [po_idx]
    tmp_region = []
    is_indp = True
    while len(dfs_stack) > 0:
        idx = dfs_stack.pop()
        for fanin_idx in fanin_list[idx]:
            if fanin_idx in region or len(region) == 0:
                is_indp = False
            if not fanin_idx in region and not fanin_idx in tmp_region \
                and x_data[idx][2] >= stop_level:
                tmp_region.append(fanin_idx)
                dfs_stack.append(fanin_idx)
    if not is_indp:
        region += tmp_region
    
if __name__ == '__main__':
    if not os.path.exists(save_bench_path):
        os.mkdir(save_bench_path)
        
    for aig_path in glob.glob('./data/raw_aig/*.aig'):
        aig_name = aig_path.split('/')[-1].split('.')[0]
        x_data, edge_index = aiger_utils.aig_to_xdata(aig_path)
        fanin_list, fanout_list = circuit_utils.get_fanin_fanout(x_data, edge_index)
        x_data, level_list = circuit_utils.feature_gen_level(x_data, fanin_list, fanout_list)
        
        # No need to extract subcircuits for the first 10 levels
        if len(level_list) <= 5:
            output_path = os.path.join(save_bench_path, '{}.bench').format(aig_name + '_0')
            region = list(range(len(x_data)))
            save_masked_circuit(region, output_path, x_data, fanin_list, fanout_list)
            continue
        
        # Random extract 
        min_size_a, min_size_b, max_size = size_range
        min_level, max_level = level_range
        subcircuit_exist = {}
        circuit_idx = 0
        for try_times in range(0, no_circuits):
            output_path = os.path.join(save_bench_path, '{}.bench').format(aig_name + '_{}'.format(circuit_idx))
            po_level = random.randint(5, len(level_list) - 1)
            stop_level = max(0, po_level - random.randint(min_level, max_level))
            res_region = []
            res_PO = []
            retry_time = 1000
            min_size = random.randint(min_size_a, min_size_b)
            while len(res_region) < min_size:
                if retry_time == 0:
                    break
                rd_select_po = random.sample(level_list[po_level], 1)[0]
                # Has been selected
                if rd_select_po in res_PO:
                    retry_time -= 1
                    continue
                # Search for fanin nodes
                previous_region_size = len(res_region)
                dfs_fanin_region(rd_select_po, stop_level, res_region, x_data, fanin_list)
                res_region.append(rd_select_po)
                if len(res_region) == previous_region_size:
                    retry_time -= 1
                    continue
                # Valid
                res_PO.append(rd_select_po)
            
            # Save the circuit
            if len(res_region) >= min_size and len(res_region) <= max_size:
                subcircuit_hash = hash_arr(res_PO)
                if not subcircuit_hash in subcircuit_exist.keys():
                    subcircuit_exist[subcircuit_hash] = True
                    save_masked_circuit(res_region, output_path, x_data, fanin_list, fanout_list)
                    circuit_idx += 1
                    print('[Info] Extracted subcircuit: {}, Size: {}'.format(output_path, len(res_region)))
                else:
                    print('[Warning] Repeated subcircuit')
            else:
                print('[Warning] Failed to extract subcircuit')
    
    # Convert to AIG 
    if not os.path.exists(save_aig_path):
        os.mkdir(save_aig_path)
    for bench_path in glob.glob(os.path.join(save_bench_path, '*.bench')):
        circuit_name = bench_path.split('/')[-1].split('.')[0]
        aig_path = os.path.join(save_aig_path, '{}.aig'.format(circuit_name))
        abc_cmd = 'abc -c "read_bench {}; strash; write_aiger {}"'.format(bench_path, aig_path)
        stdout, _ = run_command(abc_cmd)
        print('[INFO] Convert bench to aig: {}'.format(aig_path))
        