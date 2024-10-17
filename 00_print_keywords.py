import os 

keyword = 'Computer'
exclude = [
    'Arbiter', 'control', 'shift', 'adder'
]

if __name__ == '__main__':
    f = open('./repo_list.txt', 'r')
    lines = f.readlines()
    f.close()
    keyword = keyword.lower()
    for ex_idx in range(len(exclude)):
        exclude[ex_idx] = exclude[ex_idx].lower()
    
    find_list = []
    
    for line in lines:
        line = line.replace('\n', '')
        line_lower = line.lower()
        if keyword in line_lower:
            is_succ = True
            for ex in exclude:
                if ex in line_lower:
                    is_succ = False
                    break
            if is_succ:
                print(line)
                find_list.append(line)
        
    print()
    print('=' * 20)
    print('Found {} keywords'.format(len(find_list)))
    
    output_line = ''
    for word in find_list:
        output_line += word + ', '
    output_line = output_line[:-2]
    
    print(output_line)    