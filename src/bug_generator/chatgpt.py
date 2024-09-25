import json
import ast
import time
import argparse
from tqdm import tqdm
import openai


def main(args):
    
    config = {}
    with open('configs/configs.json', 'r') as f:
        config = json.load(f)

    openai.api_key = config['openai_api_key']

    lines = []
    with open(f'data/{args.project_name}/unique_methods.jsonl', 'r') as f:
        lines = f.readlines()

    json_file = open(f'data/{args.project_name}/unique_methods_{args.model_type}-{args.model_size}_chatgpt.jsonl', 'a')

    num_lines = 0
    with open(f'data/{args.project_name}/unique_methods_{args.model_type}-{args.model_size}_chatgpt.jsonl', 'r') as f:
        num_lines = len(f.readlines())

    if num_lines == len(lines):
        print('all lines have been processed')
        return

    lines = lines[num_lines:]

    loop_index = 0
    bar = tqdm(total=len(lines))
    while loop_index < len(lines):
        l = lines[loop_index]
        bar.update(1)

        start_time = time.time()

        dct = ast.literal_eval(l)

        method = dct['method'].strip().split('\n')

        least_attended_statement_indices = []
        if args.model_type != 'no_loc':
            least_attended_statement_indices = dct['least_attended_statements']

        index_code = []
        counter = 0
        for i in range(len(method)):
            stripped_statement = method[i].strip()
            if stripped_statement == '':
                continue
            index_code.append(f'{counter}- {method[i].strip()}')
            counter += 1

        change_statements = []
        for i in least_attended_statement_indices:
            change_statements.append("\"" + index_code[i] + "\"")

        change_statements_str = ''
        if len(change_statements) == 0:
            pass
        elif len(change_statements) > 1:
            change_statements_str = 'statements ' + ' and '.join(change_statements)
        else:
            change_statements_str = 'statement ' + ' and '.join(change_statements)

        prompt = ''
        if args.model_type == 'no_loc':
            prompt =  """Observe the following java method where each statement has a specific ID starting from 0. Can you produce 3 different buggy versions of this method?\n\nYou have to write each buggy method again. Do not write anything else in your response. Make sure your generated buggy java code is compilable and does not have syntax errors and compile-time errors. Do not use a variable which does not exist in the scope of the given method. You should put <start1> <start2> <start3> and <end1> <end2> <end3> in the beginning and end of each buggy method so I could parse your response later.\n\n{}""".format('\n'.join(index_code))
        else:
            prompt =  """Observe the following java method where each statement has a specific ID starting from 0. Can you produce 3 different buggy versions of this method by changing {} only? Do not change other statements in the given java code.\n\nYou have to write each buggy method again. Do not write anything else in your response. Make sure your generated buggy java code is compilable and does not have syntax errors and compile-time errors. Do not use a variable which does not exist in the scope of the given method. You should put <start1> <start2> <start3> and <end1> <end2> <end3> in the beginning and end of each buggy method so I could parse your response later.\n\n{}""".format(change_statements_str, '\n'.join(index_code))

        try:
            response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}])
            dct['chatgpt_response'] = response.choices[0].message.content
        except openai.error.InvalidRequestError as e:
            dct['chatgpt_response'] = f'Token size exceeded. {e}'
        except openai.error.Timeout as e:
            continue
        except openai.error.ServiceUnavailableError as e:
            continue
        except openai.error.APIError as e:
            continue

        dct['duration'] = time.time() - start_time

        json_file.write(json.dumps(dct) + '\n')
        json_file.flush()

        loop_index += 1


def parse_args():
    parser = argparse.ArgumentParser("prompting chatgpt")
    parser.add_argument('--project_name', type=str, default='commons-cli', help='project name to prompt its methods')
    parser.add_argument('--model_type', type=str, default='codebert', help='code-language model to use in this experiment')
    parser.add_argument('--model_size', type=str, default='base', help='code-language model size to use in this experiment')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    main(args)
