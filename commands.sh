#! /bin/bash

# describe
function gptd() {
    python ~/source/llm-utils/cgpt.py -d "$(git diff)" -s 'Describe the changes in the diff' | bat -p
}

# review
function gptr() {
    python ~/source/llm-utils/cgpt.py -r "$(git diff)" -s 'Leave some comments about how the code can be improved' | bat -p
}

# conversate
function gptc() {
    # gpt-4 head build
    # gpt-4-0314 - no updates for 3 months, june 14 2023
    # gpt-4-32k-0314 same as prev but 32k token support
    MODEL="gpt-4" python ~/source/llm-utils/conversate.py "$@"
}

function gptc4() {
    python ~/source/llm-utils/conversate.py "$@"
}

function assist() {
    python ~/source/llm-utils/assistant2.py "$@"
}

function llama() {
   echo "🦙 says:\n" 
   /Users/lfender-mba/dalai/alpaca/main --seed -1 --threads 4 --n_predict 400 --model  ~/dalai/alpaca/models/7B/ggml-model-q4_0.bin --top_k 40 --top_p 0.9 --temp 0.8 --repeat_last_n 64 --repeat_penalty 1.3 -p "Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
$1

### Response:
" 
}

function img_gpt () {
   echo "Authorization: Bearer $OPENAI_API_KEY" 
    create_img=$(curl https://api.openai.com/v1/images/generations \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $OPENAI_API_KEY" \
        -d '{
          "prompt": "'"$1"'",
          "n": 1,
          "size": "1024x1024"
        }')
    url=$(echo "$create_img" | jq -r '.data[0].url')
    echo "$url"
    rand_num=$(shuf -i 1-1000000 -n 1)
    curl -s "$url" -o "img-$rand_num.png"
}

alias conversate=gptc
