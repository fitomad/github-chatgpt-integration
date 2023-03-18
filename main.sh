#!/bin/sh -l
python /main.py --openai-api-key "$1" --github-token "$2" --github-pr-id "$3" --openai-engine "$4" --openai-temperature "$5" --openai-max-tokens "$6" --mode "$7"