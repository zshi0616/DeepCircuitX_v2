import os 
import numpy as np 
import random
import glob 
import re
import time 
import utils.aiger_utils as aiger_utils
import utils.circuit_utils as circuit_utils
from utils.utils import hash_arr, run_command

if __name__ == '__main__':
    f = open('stat.csv', 'w')
    f.write('Circuit,Succ,Input,Output,Lat,And,Lev\n')
    no_circuits = 0
    for aig_path in glob.glob('./data/raw_aig/*.aig'):
        aig_name = aig_path.split('/')[-1].split('.')[0]
        
        abc_cmd = 'abc -c \"read {}; print_stats;\"'.format(aig_path)
        stdout, runtime = run_command(abc_cmd)
        no_circuits += 1
        print('Circuit: {}, No. Circuits: {}'.format(aig_name, no_circuits))
        
        # Parse
        pattern = r"i/o\s*=\s*(\d+)/\s*(\d+)\s*lat\s*=\s*(\d+)\s*and\s*=\s*(\d+)\s*lev\s*=\s*(\d+)"
        matches = re.search(pattern, stdout[-2])
        if matches:
            input_var = int(matches.group(1))
            output_var = int(matches.group(2))
            lat_var = int(matches.group(3))
            and_var = int(matches.group(4))
            lev_var = int(matches.group(5))
            f.write('{},1,{},{},{},{},{}\n'.format(
                aig_name, input_var, output_var, lat_var, and_var, lev_var
            ))
        else:
            f.write('{},0,0,0,0,0,0\n'.format(aig_name))
        
    f.close()
        
        