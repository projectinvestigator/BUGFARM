import javalang
import json
import os
import multiprocessing
import argparse
import sys
import subprocess
import glob
import time
from typing import Set, Tuple
from utils import tokenize
import logging


class Counter(object):
    def __init__(self):
        self.val = multiprocessing.Value('i', 0)


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


def process_file(target_file):

    with open(target_file, mode='r', encoding="ISO-8859-1", errors='ignore') as r:
        codelines = r.readlines()
        code_text = ''.join(codelines)

    intervals = parse_java_func_intervals(code_text)
    unique_name = target_file.replace('/', '.')
    unique_name = unique_name.replace('$', '')

    for start, end in intervals:
        with counter.val.get_lock():
            index = counter.val.value
            counter.val.value += 1

        method_text =  ''.join(codelines[start-1:end])

        if method_text.strip() == "": continue

        with open(f'{unique_name}.{index}.java', mode='w', encoding="ISO-8859-1", errors='ignore') as fw:
            fw.write(method_text)

        os.system(f'tokenizer {unique_name}.{index}.java > {unique_name}.{index}.txt')
        tokens = tokenize(f'{unique_name}.{index}.txt')

        instance = {}
        instance['index'] = str(index)
        instance['project'] = args.project_name
        instance['file_path'] = target_file
        instance['start_line'] = str(start)
        instance['end_line'] = str(end)
        instance['method'] = method_text
        instance['tokens'] = tokens

        json_file.write(json.dumps(instance) + '\n')
        json_file.flush()
        
        os.remove(f'{unique_name}.{index}.txt')
        os.remove(f'{unique_name}.{index}.java')


def main(args):

    start = time.time()

    global json_file
    global counter

    os.makedirs(f'logs', exist_ok=True)
    logging.basicConfig(filename=f"logs/{args.log_file}", level=logging.INFO, format='%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logging.info(f'extracting methods from {args.project_name}')

    counter = Counter()

    files = subprocess.Popen(["ls"] + glob.glob(f'projects/{args.project_name}/**/src/main/java/**/*.java', recursive=True), stdout=subprocess.PIPE)
    source_paths = [x.decode('ascii').strip() for x in files.stdout.readlines()]

    os.makedirs(f'data/{args.project_name}', exist_ok=True)

    json_file = open(f"data/{args.project_name}/unique_methods.jsonl", "wt")
    pool = multiprocessing.Pool(args.num_workers)

    for i, _ in enumerate(pool.imap_unordered(process_file, source_paths), 1):
        sys.stderr.write('\rpercentage of source code files completed: {0:%}'.format(i/len(source_paths)))

    logging.info(f'total time in secs for {args.project_name}: ' + str(round(time.time() - start, 2)))
    logging.info(f'total methods extracted from {args.project_name}: ' + str(counter.val.value))


def parse_args():
    parser = argparse.ArgumentParser("extract methods of a given java project")
    parser.add_argument('--project_name', type=str, default='commons-cli', help='project name to process and extract methods')
    parser.add_argument('--log_file', type=str, default='method_extractor.log', help='log file name for method extractor')
    parser.add_argument('--num_workers', type=int, default=8, help='number of cpu cores to use for threading')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    main(args)
