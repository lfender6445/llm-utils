# Setup

Python 3.11.1

```
pip install -r requirements.txt
```

## Usage

```
MODEL="gpt-4" python ~/source/llm-utils/conversate.py -f ./someFile.ts --prompt 'add documentation to the typescript file for each method'
```

```
MODEL="gpt-4" python ~/source/llm-utils/conversate.py --help

usage: conversate.py [-h] [--mock] [--skip-logs] [--llama] [--prompt PROMPT] [--speech] [--system-prompt SYSTEM_PROMPT] [--ext EXT] [-f FILES]

options:
  -h, --help            show this help message and exit
  --mock                save money, avoid an api request, test script ops
  --skip-logs           skip logging to disk
  --llama               add llama response
  --prompt PROMPT       Supply and skip initial prompt
  --speech              convert result to speech using tts.py
  --system-prompt SYSTEM_PROMPT
                        system prompt. appended to existing ext prompts if present
  --ext EXT             Language specific prompts. file path
  -f FILES, --files FILES
                        List of filenames `-f foo.ts -f bar.ts`
```
