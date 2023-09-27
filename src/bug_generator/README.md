## Prompting LLM
The fourth step is to use the LASs/LATs, craft custom prompts, and query an LLM (i.e., ChatGPT). Execute the following to send custom prompts of codebert-base to ChatGPT and store its responses inside `data/$project/unique_methods_codebert-base_chatgpt.jsonl`. If a connection error happens because of OpenAI API, you may execute the same command and the requests will resume without deleting existing responses. You may want to change `python3` to point to a higher version (i.e., 3.9) because OpenAI API is not compatible with older versions of python.

`bash scripts/prompting.sh codebert base`

## Parsing LLM Response
The fifth step is to parse the LLM response. Execute the following to parse ChatGPT responses from codebert-base using 8 CPU cores, and save each buggy method inside `data/$project/unique_methods_codebert-base_NBugs.jsonl`:

`bash scripts/parse_response.sh parse_chatgpt.log codebert base 8`

## Bug Selection
The sixth step is to perform bug selection (Algorithm 2 in paper). Execute the following to select codebert-base bugs using 8 CPU cores and save it inside `data/$project/unique_methods_codebert-base_selected_bugs.jsonl`:

`bash scripts/bug_selection.sh bug_selection.log codebert base 8`
