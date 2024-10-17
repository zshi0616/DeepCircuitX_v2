import os 

exclude = [
    'risc', 'rv', 'counter', 'decoder', 'encoder', 'dma', 'ALU', 'processor', 
    'arbiter', 'pci', 'multi', 'FPU', 'chisel', 'fpga', 'AHB', 'spi'
]

if __name__ == '__main__':
    csv_path = './categories.csv'
    f = open(csv_path, 'r')
    lines = f.readlines()
    f.close()
    
    # Get all 
    cat = {}
    for line_id, line in enumerate(lines):
        if line_id == 0:
            continue
        arr = line.replace('\n', '').replace(' ', '').split(',')
        cat_name = arr[2]
        designs = arr[4:]
        cat[cat_name] = designs
    
    # Remove duplicates
    name2cat = {}
    has_dup = False
    for cat_name in cat:
        for design in cat[cat_name]:
            if design in name2cat:
                print('Duplicate: {} in {} and {}'.format(design, cat_name, name2cat[design]))
                has_dup = True
            name2cat[design] = cat_name
    if has_dup:
        print('There are duplicates !!!')
        exit(0)
            
    # Read all designs 
    f = open('./repo_list.txt', 'r')
    lines = f.readlines()
    f.close()
    all_designs = []
    for line in lines:
        all_designs.append(line.replace('\n', ''))
    
    # Find all designs that are not in the categories
    not_found = []
    for design in all_designs:
        if design not in name2cat:
            not_found.append(design)
            
    for design in not_found:
        is_succ = True
        for ex in exclude:
            if ex.lower() in design.lower():
                is_succ = False
                break
        if is_succ:
            print(design)
    print('# Not found: {}'.format(len(not_found)))