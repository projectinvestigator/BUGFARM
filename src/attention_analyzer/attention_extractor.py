from transformers import AutoTokenizer, AutoModel, T5EncoderModel, RobertaTokenizer, AutoModelForSeq2SeqLM
import torch
from utils import visual_atn_matrix, adjust_tokens
import numpy as np
from json import JSONEncoder
import json
import ast
import argparse
import time
import tqdm
import os
import logging


class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)


def main(args):
    start = time.time()

    os.makedirs(f'logs', exist_ok=True)
    logging.basicConfig(filename=f"logs/{args.log_file}", level=logging.INFO, format='%(asctime)s %(levelname)s %(module)s - %(funcName)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logging.info(f'extracting method attentions from {args.project_name} using {args.model_type}-{args.model_size}')

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

    lines = []
    with open(f'data/{args.project_name}/unique_methods.jsonl') as fr:
        lines = fr.readlines()
    
    json_file = open(f"data/{args.project_name}/unique_methods_{args.model_type}-{args.model_size}_attnw.jsonl", "wt")

    for l in tqdm.tqdm(lines):

        dct = ast.literal_eval(l)

        # Tokenization 
        nl_tokens = tokenizer.tokenize("")

        method = dct['method']
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
            model_attentions, decoded_token_types = adjust_tokens(decoded_tokens, dct['tokens'], model_attentions)
        except Exception:
            continue

        dct['model_attentions'] = model_attentions
        dct['decoded_token_types'] = decoded_token_types

        json_file.write(json.dumps(dct, cls=NumpyArrayEncoder) + '\n')
        json_file.flush()

    logging.info(f'total time in secs for {args.project_name} using {args.model_type}-{args.model_size}: ' + str(round(time.time() - start, 2)))


def parse_args():
    parser = argparse.ArgumentParser("extract attention weights of a project using a given model")
    parser.add_argument('--project_name', type=str, default='commons-cli', help='project name to process and extract methods')
    parser.add_argument('--model_type', type=str, default='codebert', help='LLM to use in this experiment')
    parser.add_argument('--model_size', type=str, default='base', help='model size to use in this experiment')
    parser.add_argument('--log_file', type=str, default='attention_extractor.log', help='log file name')
    parser.add_argument('--gpu_id', type=int, default=0, help='gpu id to use')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    main(args)
