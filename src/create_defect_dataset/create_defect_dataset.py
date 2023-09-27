import json
import argparse
import ast
import subprocess
import glob
import os
import extract_leam
import extract_mubert
import extract_regminer

def main(args):

    if args.type == 'closure-mockito':

        json_file = open(f'data/defect/defects4j/test.jsonl', 'wt')

        counter = 0
        instances = []
        for project in ['Chart', 'Cli', 'Closure', 'Codec', 'Collections', 'Compress', 'Csv', 'Gson', 'JacksonCore', 'JacksonDatabind', 'JacksonXml', 'Jsoup', 'JxPath', 'Lang', 'Math', 'Mockito', 'Time']:
            files = subprocess.Popen(["ls"] + glob.glob(f'data/defect/defects4j/{project}/**/*.txt', recursive=True), stdout=subprocess.PIPE)
            source_paths = [x.decode('ascii').strip() for x in files.stdout.readlines()]

            for source_path in source_paths:
                bug_id = source_path.split('/')[-2].strip()

                with open(source_path, 'r') as f:
                    func = f.read()
                    # func = ' '.join(func.split())
                
                if 'fixed' in source_path:
                    instances.append((func, 0))
                else:
                    instances.append((func, 1))
                json_file.flush()
        
        distinct_instances = set(instances)
        for instance in distinct_instances:
            json_file.write(json.dumps({"func": f"{instance[0]}", "target": instance[1], "idx": counter}) + '\n')
            counter += 1

    elif args.type == 'bugswarm':

        path_ = 'data/defect/bugswarm/'
        json_file = open(path_ + 'big_test.jsonl', 'wt')

        counter = 0
        instances = []
        
        dirs = os.listdir(path_)
        for dir_ in dirs:
            if not os.path.isdir(path_ + dir_):
                continue
            bug_ids = os.listdir(path_ + dir_)
            for bug_id in bug_ids:

                if not os.path.isdir(path_ + dir_ + '/' + bug_id + '/' + 'fixed') or not os.path.isdir(path_ + dir_ + '/' + bug_id + '/' + 'buggy'):
                    continue

                fixed_files = os.listdir(path_ + dir_ + '/' + bug_id + '/' + 'fixed')
                buggy_files = os.listdir(path_ + dir_ + '/' + bug_id + '/' + 'buggy')

                for fixed_file in fixed_files:
                    with open(path_ + dir_ + '/' + bug_id + '/' + 'fixed' + '/' + fixed_file, 'r') as f:
                        func = f.read()
                        # func = ' '.join(func.split())
                        instances.append((func, 0))
                        json_file.flush()
                
                for buggy_file in buggy_files:
                    with open(path_ + dir_ + '/' + bug_id + '/' + 'buggy' + '/' + buggy_file, 'r') as f:
                        func = f.read()
                        # func = ' '.join(func.split())
                        instances.append((func, 1))
                        json_file.flush()


        distinct_instances = set(instances)
        for instance in distinct_instances:
            json_file.write(json.dumps({"func": f"{instance[0]}", "target": instance[1], "idx": counter}) + '\n')
            counter += 1

    elif args.type == 'leam':
        jsonfiles_dir = "data/defect/leam_mutants"
        jsonline_file = os.path.join(jsonfiles_dir,"all_leam_mutants.jaonl")
        # args: mutants_input_dir, output_dir, json_file; here config output_dir same as input_dir
        extract_leam.extract(jsonfiles_dir,jsonfiles_dir,jsonline_file)
    
    elif args.type == 'mubert':
        jsonfiles_dir = "data/defect/mubert_mutants"
        jsonline_file = os.path.join(jsonfiles_dir,"all_mubert_mutants.jaonl")
        #args: mutants_input_dir, json_file
        extract_mubert.extract(jsonfiles_dir,jsonline_file) 

    elif args.type == 'regminer':
        regminer_mutants_dir = "data/defect/regminer_mutants"
        regminer_outputs_dir = "data/defect/regminer_mutants"
        # args: mutants_dir, output_dir; here config output_dir same as input_dir
        extract_regminer.extract(regminer_mutants_dir,regminer_outputs_dir)

    else:

        projects = ["commons-cli", "commons-codec", "commons-collections", "commons-compress", "commons-csv", "commons-jxpath", "commons-lang", "commons-math", "gson", "jackson-core", "jackson-databind", "jackson-dataformat-xml", "jfreechart", "joda-time", "jsoup"]

        json_file = open(f'data/defect/bugfarm-{args.model}/{args.model}.jsonl', 'wt')

        counter = 0
        for project in projects:

            with open(f'data/{project}/unique_methods_{args.model}_selected_bugs.jsonl', 'r') as f:
                lines = f.readlines()
                for line in lines:
                    dct = ast.literal_eval(line)
                    func = dct['method']
                    dct['method'] = func
                    fixed_idx = counter
                    json_file.write(json.dumps({"func": f"{dct['method']}", "target": 0, "idx": counter, "project": dct['project'], "file_path": dct['file_path']}) + '\n')
                    counter += 1

                    if 'selected_bugs' not in dct:
                        continue

                    for bug_id in dct['selected_bugs']:
                        func = dct[f'buggy_method{bug_id}']
                        dct[f'buggy_method{bug_id}'] = func
                        json_file.write(json.dumps({"func": f"{dct[f'buggy_method{bug_id}']}", "target": 1, "idx": counter, "project": dct['project'], "file_path": dct['file_path'], "fixed_method_idx": fixed_idx}) + '\n')
                        counter += 1

                    json_file.flush()


def parse_args():
    parser = argparse.ArgumentParser("create defect dataset")
    parser.add_argument('--type', type=str, default='bugfarm', help='bugfarm, bugswarm, leam, mubert, regminer')
    parser.add_argument('--model', type=str, default='codebert-base', help='codebert-base, codet5-base, NatGen-base')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    main(args)
