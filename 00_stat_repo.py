import os 
import numpy as np 
import random
import glob 
import re
import time 
import utils.aiger_utils as aiger_utils
import utils.circuit_utils as circuit_utils
from utils.utils import hash_arr, run_command

raw_dir = './data/output_riscv_diffModule2'

if __name__ == '__main__':
    f = open('repo_list.txt', 'w')
    for design_dir in glob.glob('{}/*'.format(raw_dir)):
        design_name = design_dir.split('/')[-1]
        f.write('{}\n'.format(design_name))
        print(design_name)
    f.close()