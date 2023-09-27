import multiprocessing
import numpy as np
import ast
import json
import os
import math
import sys
import argparse
import time
import logging
from json import JSONEncoder


class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)


def main(args):

    start = time.time()

    global json_file

    os.makedirs(f'logs', exist_ok=True)
    logging.basicConfig(filename=f"logs/{args.log_file}", level=logging.INFO, format='%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logging.info(f'analyzing attention weights of {args.project_name} using {args.model_type}-{args.model_size}')

    lines = []
    with open(f'data/{args.project_name}/unique_methods_{args.model_type}-{args.model_size}_attnw.jsonl') as fr:
        lines = fr.readlines()

    json_file = open(f"data/{args.project_name}/unique_methods_{args.model_type}-{args.model_size}_las_lat.jsonl", "wt")

    pool = multiprocessing.Pool(args.num_workers)
    for i, _ in enumerate(pool.imap_unordered(process_instance, lines), 1):
        sys.stderr.write('\rpercentage of methods analyzed: {0:%}'.format(i/len(lines)))

    logging.info(f'total time in secs for analyzing attention weights of {args.project_name} using {args.model_type}-{args.model_size}: ' + str(round(time.time() - start, 2)))


def process_instance(input):
    dct = ast.literal_eval(input)
    model_attentions = dct['model_attentions']
    decoded_token_types = dct['tokens']
    decoded_tokens = [x for x,y in decoded_token_types]

    col_averaged = np.average(model_attentions, axis=0)

    k = args.threshold
    token_attn = list(zip(decoded_token_types, col_averaged))
    token_attn.sort(key = lambda i:i[1])

    least_attended_tokens = token_attn[:math.ceil((k/100) * len(token_attn))]

    counter = 0
    record = {}
    statement = ''
    score = []
    for i in range(len(decoded_tokens)):
        if decoded_tokens[i].strip() in ['<s>', '</s>']: continue

        if decoded_tokens[i] == '\n':
            record[counter] = [statement, np.sum(score), len(score)]
            counter += 1
            statement, score = '', []
            continue

        statement += decoded_tokens[i] + ' '

        if decoded_tokens[i] in list(zip(*list(zip(*least_attended_tokens))[0]))[0]:
            score.append(1)
        else:
            score.append(0)
    
    record[counter] = [statement, np.sum(score), len(score)]

    unnormalized_lengths = []
    for i in sorted(record):
        unnormalized_lengths.append(record[i][2])
    
    unnormalized_lengths = np.array(unnormalized_lengths) / np.linalg.norm(unnormalized_lengths)
    for i in sorted(record):
        record[i].append(unnormalized_lengths[i])
        record[i].append(record[i][1] / record[i][3])

    attended_statements = sorted(record.items(), key=lambda item: item[1][4])

    res = []
    for pair in attended_statements:
        if pair[0] == 0:
            res.append(pair)
        elif pair[1][0].strip().startswith('//'):
            res.append(pair)
        else:
            res.insert(0, pair)

    least_attended_statements = res[:math.ceil((k/100) * len(res))]

    dct['least_attended_tokens'] = [x[0][0] for x in least_attended_tokens]
    dct['least_attended_statements'] = [x[0] for x in least_attended_statements]

    json_file.write(json.dumps(dct, cls=NumpyArrayEncoder) + '\n')
    json_file.flush()


def parse_args():
    parser = argparse.ArgumentParser("analyze attention weights and locate least attended statements")
    parser.add_argument('--project_name', type=str, default='commons-cli', help='project name to analyze its attentions')
    parser.add_argument('--model_type', type=str, default='codebert', help='model to use in this experiment')
    parser.add_argument('--model_size', type=str, default='base', help='model size to use in this experiment')
    parser.add_argument('--log_file', type=str, default='attention_analyzer.log', help='log file name')
    parser.add_argument('--threshold', type=int, default=10, help='threshold for least attended tokens and statements')
    parser.add_argument('--num_workers', type=int, default=8, help='number of cpu cores to use for threading')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    main(args)
