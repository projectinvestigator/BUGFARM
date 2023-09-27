import javalang
from typing import Set, Tuple
import sys

def get_string(data, start, end):
    if start is None:
        return ""

    # positions are all offset by 1. e.g. first line -> lines[0], start.line = 1
    end_pos = None

    if end is not None:
        end_pos = end.line #- 1

    lines = data.splitlines(True)
    string = "".join(lines[start.line:end_pos])
    string = lines[start.line - 1] + string

    # When the method is the last one, it will contain a additional brace
    if end is None:
        left = string.count("{")
        right = string.count("}")
        if right - left == 1:
            p = string.rfind("}")
            string = string[:p]

    return string


def parse_java_func_intervals(content: str,path:str) -> Set[Tuple[int, int]]:
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
                        get_string(content,node.start_position,node.end_position),
                        path,
                        #node,
                    )
                )

        # for each in func_intervals:
        #     print(each)
        return func_intervals
    except javalang.parser.JavaSyntaxError:
        return func_intervals

def read_java(f):
    fh = open(f, 'r', errors='ignore')
    data = fh.read()
    return parse_java_func_intervals(data,f)

# file = sys.argv[1]
# read_java(file)
