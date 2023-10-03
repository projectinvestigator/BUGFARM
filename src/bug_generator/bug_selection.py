import ast
import argparse
import torch
import numpy as np
import math
import json
import difflib
import os
import time
import tqdm
import logging
from transformers import AutoTokenizer, AutoModel, T5EncoderModel, RobertaTokenizer, AutoModelForSeq2SeqLM
from utils import visual_atn_matrix, adjust_tokens


def get_least_attended_stmts(model_attentions, decoded_token_types):
    decoded_tokens = [x for x,y in decoded_token_types]

    col_averaged = np.average(model_attentions, axis=0)

    k = 10
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

    return least_attended_statements


def main(args):

    start = time.time()

    os.makedirs(f'logs', exist_ok=True)
    logging.basicConfig(filename=f"logs/{args.log_file}", level=logging.INFO, format='%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logging.info(f'parsing chatgpt - {args.project_name} using {args.model_type}-{args.model_size}')

    global tokenizer, model, stats, json_file, device

    project = args.project_name
    model_type = args.model_type
    model_size = args.model_size

    device = torch.device(f"cuda:{args.gpu_id}" if torch.cuda.is_available() else "cpu")

    if args.model_type == 'codet5':
        tokenizer = RobertaTokenizer.from_pretrained(f"salesforce/{args.model_type}-{args.model_size}")
        model = T5EncoderModel.from_pretrained(f"salesforce/{args.model_type}-{args.model_size}")
    elif args.model_type == 'codebert':
        tokenizer = AutoTokenizer.from_pretrained(f"microsoft/{args.model_type}-{args.model_size}")
        model = AutoModel.from_pretrained(f"microsoft/{args.model_type}-{args.model_size}")
    elif args.model_type == 'NatGen':
        tokenizer = AutoTokenizer.from_pretrained(f'saikatc/{args.model_type}')
        model = AutoModelForSeq2SeqLM.from_pretrained(f'saikatc/{args.model_type}')

    model.to(device)

    filename = f'data/{project}/unique_methods_{model_type}-{model_size}_Nbugs.jsonl'

    json_file = open(f'data/{project}/unique_methods_{model_type}-{model_size}_selected_bugs.jsonl', 'w')

    lines = []
    with open(filename, 'r') as f:
        lines = f.readlines()

    stats = {'total_selected_bugs': 0}

    for line in tqdm.tqdm(lines):
        dct = ast.literal_eval(line)

        dct['selected_bugs'] = []
        for bug_num in range(3):

            method = dct[f'buggy_method{bug_num+1}']

            if method.strip() == '':
                continue

            nl_tokens = tokenizer.tokenize("")
            statements = method.split('\n')
            statements = [x.strip() for x in statements if x.strip() != '']
            code = '\n'.join(statements)

            code_tokens = tokenizer.tokenize(code)

            if len(code_tokens) > tokenizer.model_max_length - 3:
                continue

            tokens = [tokenizer.cls_token]+nl_tokens+[tokenizer.sep_token]+code_tokens+[tokenizer.eos_token]

            # Convert tokens to ids
            tokens_ids = tokenizer.convert_tokens_to_ids(tokens)
            decoded_tokens = [tokenizer.decode(id_) for id_ in tokens_ids]

            # Extract the attentions
            key = 'encoder_attentions' if args.model_type == 'NatGen' else 'attentions'

            if args.model_type == 'NatGen':
                attentions = model(torch.tensor(tokens_ids, device=device)[None,:], output_attentions=True, decoder_input_ids=torch.tensor(tokens_ids, device=device)[None,:])[key]
            else:
                attentions = model(torch.tensor(tokens_ids, device=device)[None,:], output_attentions=True)[key]

            num_layers = len(attentions)

            # Post-process attentions
            zeros = np.zeros((len(decoded_tokens), len(decoded_tokens)))
            for i in range(num_layers):
                zeros += visual_atn_matrix(decoded_tokens, attentions, layer_num=i, head_num='average')
            
            model_attentions = zeros / num_layers

            try:
                model_attentions, decoded_token_types = adjust_tokens(decoded_tokens, dct[f'buggy_method_{bug_num}_tokens'], model_attentions)
            except Exception:
                continue

            least_attended_stmts = get_least_attended_stmts(model_attentions, decoded_token_types)

            original_code = dct['method']

            f1 = [line.strip() + '\n' for line in original_code.strip().split('\n')]
            f2 = [line.strip() + '\n' for line in code.strip().split('\n')]

            delta = difflib.unified_diff(f1, f2, fromfile='original', tofile='current')

            check = True
            for line in delta:
                if not line.strip().startswith('+++') and line.strip().startswith('+'):
                    changed_added_stmt = line.strip()[1:].strip()
                    for idx in least_attended_stmts:
                        if ''.join(idx[1][0].strip().split()) != ''.join(changed_added_stmt.split()):
                            check = False

            if check and bug_num+1 not in dct['selected_bugs']:
                dct['selected_bugs'].append(bug_num+1)
                stats['total_selected_bugs'] += 1
        
        json_file.write(json.dumps(dct) + '\n')
        json_file.flush()


    total_selected_bugs = stats['total_selected_bugs']

    logging.info(f'total selected bugs: {total_selected_bugs}')
    logging.info(f'total time in secs for selecting bugs of {args.project_name} using {args.model_type}-{args.model_size}: ' + str(round(time.time() - start, 2)))


def parse_args():
    parser = argparse.ArgumentParser("bug selection")
    parser.add_argument('--project_name', type=str, default='commons-cli', help='project name to select bugs for')
    parser.add_argument('--model_type', type=str, default='codebert', help='LLM to use in this experiment')
    parser.add_argument('--model_size', type=str, default='base', help='model size to use in this experiment')
    parser.add_argument('--log_file', type=str, default='bug_selection.log', help='log file to store the logs')
    parser.add_argument('--gpu_id', type=int, default=0, help='gpu id to use')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    main(args)
