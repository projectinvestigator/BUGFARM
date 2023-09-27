import javalang
from typing import Set, Tuple
import os


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


def main():

    path_ = 'data/defect/bugswarm'

    dirs = os.listdir(path_)

    for dir in dirs:
        bug_id = os.listdir(path_ + '/' + dir)

        for id in bug_id:

            diff = path_ + '/' + dir + '/' + id + '/patch.txt'

            lines = []
            try:
                with open(diff, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
            except UnicodeDecodeError:
                with open(diff, 'r', encoding='ISO-8859-1') as f:
                    lines = f.readlines()

            line_num = 0
            while not lines[line_num].startswith('diff'):
                line_num += 1

            metadata = {}
            recent_path = ''
            for l in lines[line_num:]:
                if l.startswith('---') and len(l.split()) == 1:
                    continue

                if l.startswith('---'):
                    recent_path = l.split(' ')[1].strip()[2:]
                    metadata.setdefault(recent_path, [])

                elif l.startswith('+++'):
                    recent_path = l.split(' ')[1].strip()[2:]
                    metadata.setdefault(recent_path, [])

                elif l.startswith('@@'):
                    splitted = l.split(' ')
                    metadata[recent_path].append((int(splitted[1].strip().split(',')[0][1:]), int(splitted[2].strip().split(',')[0][1:])))

            os.makedirs(path_ + '/' + dir + '/' + id + '/fixed', exist_ok=True)
            os.makedirs(path_ + '/' + dir + '/' + id + '/buggy', exist_ok=True)

            c = 0
            for path in metadata:
                fix_ls = [x[0] for x in metadata[path]]
                buggy_ls = [x[1] for x in metadata[path]]
                
                if not path.endswith('.java'):
                    continue

                if 'test' in path.split('/')[-1].lower():
                    continue

                fixed_path = path_ + '/' + dir + '/' + id + '/success/' + path
                buggy_path = path_ + '/' + dir + '/' + id + '/fail/' + path

                if not os.path.exists(fixed_path) or not os.path.exists(buggy_path):
                    continue

                for i in range(len(fix_ls)):
                    fixed_line = fix_ls[i]

                    with open(fixed_path, 'r') as f:
                        fixed_content = f.read()
                        fixed_lines = fixed_content.split('\n')
                        intervals = parse_java_func_intervals(fixed_content)

                        while True:
                            if fixed_line < len(fixed_lines) and fixed_lines[fixed_line].strip().startswith('*') or fixed_lines[fixed_line].strip().startswith('@') or fixed_lines[fixed_line].strip() == '':
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

                                with open(f'{path_}/{dir}/{id}/fixed/{c}.txt', 'w') as f:
                                    f.write(func)

                                break


                    buggy_line = buggy_ls[i]
                    with open(buggy_path, 'r') as f:
                        buggy_content = f.read()
                        buggy_lines = buggy_content.split('\n')
                        intervals = parse_java_func_intervals(buggy_content)

                        while True:
                            if buggy_line < len(buggy_lines) and buggy_lines[buggy_line].strip().startswith('*') or buggy_lines[buggy_line].strip().startswith('@') or buggy_lines[buggy_line].strip() == '':
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

                                with open(f'{path_}/{dir}/{id}/buggy/{c}.txt', 'w') as f:
                                    f.write(buggy_func)

                                break

                    c += 1


if __name__ == '__main__':
    main()
