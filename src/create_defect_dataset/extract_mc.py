import javalang
from typing import Set, Tuple
import os
import sys


def parse_java_func_intervals(content: str) -> Set[Tuple[int, int]]:
    func_intervals = set()
    try:
        for _, node in javalang.parse.parse(content):
            if isinstance(
                node,
                (javalang.tree.MethodDeclaration, javalang.tree.ConstructorDeclaration),
            ):
                func_intervals.add(
                    (
                        node.start_position.line,
                        node.end_position.line,
                    )
                )
        return func_intervals
    except javalang.parser.JavaSyntaxError:
        return func_intervals


def main(project):

    deprecated_bugs = {'Cli': ['6'], 'Closure': ['63', '93'], 'Collections': [str(x) for x in range(1,25)], 'Lang': ['2'], 'Time': ['21']}
    deprecated_bugs.setdefault(project, [])

    # use which defects4j and store the path here
    os.system('which defects4j > defects4j_path.txt')
    with open('defects4j_path.txt', 'r') as f:
        defects4j_path = f.read().strip().split('bin')[0]
        os.system(f'rm defects4j_path.txt')

    path_ = f'/{defects4j_path}/projects/{project}/patches'

    os.makedirs(f'data/defect/{project}/fixed', exist_ok=True)
    os.makedirs(f'data/defect/{project}/buggy', exist_ok=True)

    for patch in os.listdir(path_):

        if not patch.endswith('.src.patch'):
            continue

        fp = os.path.join(path_, patch)

        lines = []
        with open(fp, 'r', encoding="ISO-8859-1", errors='ignore') as f:
            lines = f.readlines()

        metadata = {}
        recent_path = ''
        for l in lines:

            if l.startswith('---'):
                temp_path = l.split(' ')[1].strip()

                if temp_path.startswith('source'):
                    recent_path = temp_path
                else:
                    recent_path = temp_path[2:].strip()
                
                if not recent_path.endswith('.java'):
                    recent_path = recent_path.split('\t')[0].strip()

                metadata.setdefault(recent_path, [])

            elif l.startswith('+++'):
                temp_path = l.split(' ')[1].strip()

                if temp_path.startswith('source'):
                    recent_path = temp_path
                else:
                    recent_path = temp_path[2:].strip()
                
                if not recent_path.endswith('.java'):
                    recent_path = recent_path.split('\t')[0].strip()
                    
                metadata.setdefault(recent_path, [])

            elif l.startswith('@@'):
                splitted = l.split(' ')
                metadata[recent_path].append((int(splitted[1].strip().split(',')[0][1:]), int(splitted[2].strip().split(',')[0][1:])))

        bug_id = patch.split('.')[0]

        if bug_id in deprecated_bugs[project]:
            print(f'Deprecated bug detected. Skipping bug {bug_id}')
            continue

        if os.path.exists(f'data/defect/{project}/fixed/' + bug_id):
            print(f'Already exists: {bug_id}')
            continue

        os.makedirs(f'data/defect/{project}/fixed/' + bug_id, exist_ok=True)
        os.makedirs(f'data/defect/{project}/buggy/' + bug_id, exist_ok=True)

        os.makedirs('buggy', exist_ok=True)
        os.makedirs('fixed', exist_ok=True)

        os.system(f'defects4j checkout -p {project} -v {bug_id}b -w buggy')
        os.system(f'defects4j checkout -p {project} -v {bug_id}f -w fixed')

        os.system(f'chmod -R 777 buggy')
        os.system(f'chmod -R 777 fixed')

        c = 0
        for path in metadata:
            
            if not path.endswith('.java'):
                continue

            fix_ls = [x[0] for x in metadata[path]]
            buggy_ls = [x[1] for x in metadata[path]]
            fixed_path = path
            buggy_path = path

            for i in range(len(fix_ls)):
                fixed_line = fix_ls[i]

                with open('fixed/' + fixed_path, 'r', encoding="ISO-8859-1", errors='ignore') as f:
                    fixed_content = f.read()
                    fixed_lines = fixed_content.split('\n')
                    intervals = parse_java_func_intervals(fixed_content)

                    while True:
                        if fixed_lines[fixed_line].strip().startswith('*') or fixed_lines[fixed_line].strip().startswith('@') or fixed_lines[fixed_line].strip() == '':
                            fixed_line += 1
                            continue
                        else:
                            fixed_line += 1
                            break
                    
                    for interval in intervals:
                        if interval[0] <= fixed_line <= interval[1]:
                            start_line = interval[0]
                            end_line = interval[1]
                            func = '\n'.join(fixed_lines[start_line-1:end_line])

                            with open(f'data/defect/{project}/fixed/{bug_id}/{c}.txt', 'w') as f:
                                f.write(func)

                            break


                buggy_line = buggy_ls[i]
                with open('buggy/' + buggy_path, 'r', encoding="ISO-8859-1", errors='ignore') as f:
                    buggy_content = f.read()
                    buggy_lines = buggy_content.split('\n')
                    intervals = parse_java_func_intervals(buggy_content)

                    while True:
                        if buggy_lines[buggy_line].strip().startswith('*') or buggy_lines[buggy_line].strip().startswith('@') or buggy_lines[buggy_line].strip() == '':
                            buggy_line += 1
                            continue
                        else:
                            buggy_line += 1
                            break

                    for interval in intervals:  
                        if interval[0] <= buggy_line <= interval[1]:
                            start_line = interval[0]
                            end_line = interval[1]
                            buggy_func = '\n'.join(buggy_lines[start_line-1:end_line])

                            with open(f'data/defect/{project}/buggy/{bug_id}/{c}.txt', 'w') as f:
                                f.write(buggy_func)

                            break

                c += 1


if __name__ == '__main__':
    main(sys.argv[1])
