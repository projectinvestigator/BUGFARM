import ast
import os
import argparse
import multiprocessing
import sys
import logging
import time
import shutil


def main(args):

    os.makedirs(f'logs', exist_ok=True)
    logging.basicConfig(filename=f"logs/testing.log", level=logging.INFO, format='%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logging.info(f'testing project={args.project_name} model_name={args.model_name} model_size={args.model_size}')

    start_time = time.time()

    lines = []
    with open(f'data/{args.project_name}/unique_methods_{args.model_name}-{args.model_size}_selected_bugs.jsonl') as f:
        lines = f.readlines()

    os.makedirs(f'test_results_{args.model_name}-{args.model_size}/{args.project_name}', exist_ok=True)

    pool = multiprocessing.Pool(args.num_workers)
    for i, _ in enumerate(pool.imap_unordered(process_instance, lines), 1):
        sys.stderr.write('\rpercentage of source code files completed: {0:%}'.format(i/len(lines)))

    end_time = time.time()
    time_minutes = round((end_time-start_time)/60,2)
    logging.info(f'testing project={args.project_name} model_name={args.model_name} model_size={args.model_size} time={round(end_time-start_time,2)} seconds ({time_minutes} minutes)')


def process_instance(l):

    dct = ast.literal_eval(l)

    index = dct['index']

    if args.model_name == 'no_loc':
        dct['selected_bugs'] = [1, 2, 3]

    if dct['selected_bugs'] == []:
        return

    project = dct['project']
    main_dir = os.getcwd()
    os.makedirs(f'temp_project_{args.model_name}-{args.model_size}_{project}_{index}', exist_ok=True)
    os.system(f'cp -r projects/{project} temp_project_{args.model_name}-{args.model_size}_{project}_{index}/')
    
    for bug_id in dct['selected_bugs']:

        if os.path.exists(f'test_results_{args.model_name}-{args.model_size}/{project}/{project}.{index}.{bug_id}.{args.model_name}-{args.model_size}.build.log'):
            continue

        os.system(f'rm -rf temp_project_{args.model_name}-{args.model_size}_{project}_{index}/{project}/target')

        buggy_method = dct[f'buggy_method{bug_id}']

        file_path = dct['file_path']
        start_line = int(dct['start_line'])
        end_line = int(dct['end_line'])

        relative_path = '/'.join(file_path.split('/')[1:])

        file_lines = []
        with open(f'temp_project_{args.model_name}-{args.model_size}_{project}_{index}/{relative_path}', 'r', encoding="ISO-8859-1", errors='ignore') as f:
            file_lines = f.readlines()
        
        file_lines[start_line-1:end_line] = buggy_method

        with open(f'temp_project_{args.model_name}-{args.model_size}_{project}_{index}/{relative_path}', 'w') as f:
            f.writelines(file_lines)

        os.chdir(f'temp_project_{args.model_name}-{args.model_size}_{project}_{index}/{project}')
        if project in ['commons-lang', 'joda-time']:
            os.system(f'JAVA_HOME="/usr/lib/jvm/java-1.8.0/jre" timeout 300 mvn clean test -Drat.skip=true 2> /dev/null | grep ERROR > ../../test_results_{args.model_name}-{args.model_size}/{project}/{project}.{index}.{bug_id}.{args.model_name}-{args.model_size}.build.log')
        else:
            os.system(f'timeout 300 mvn clean test -Drat.skip=true 2> /dev/null | grep ERROR > ../../test_results_{args.model_name}-{args.model_size}/{project}/{project}.{index}.{bug_id}.{args.model_name}-{args.model_size}.build.log')

        os.system(f'cp {main_dir}/projects/{relative_path} {main_dir}/temp_project_{args.model_name}-{args.model_size}_{project}_{index}/{relative_path}')
        os.chdir(main_dir)
    
    shutil.rmtree(f'temp_project_{args.model_name}-{args.model_size}_{project}_{index}', ignore_errors=True)


def parse_args():
    parser = argparse.ArgumentParser("test buggy methods on projects")
    parser.add_argument('--project_name', type=str, default='commons-cli', help='project name to test buggy methods on')
    parser.add_argument('--model_name', type=str, default='codebert', help='model name to test buggy methods on')
    parser.add_argument('--model_size', type=str, default='base', help='model name to test buggy methods on')
    parser.add_argument('--num_workers', type=int, default=8, help='number of cpu cores to use for threading')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    main(args)
