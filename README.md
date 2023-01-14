# PipeGPT

Integrate ChatGPT into your terminal pipelines.


## Gotchas

**You are sending all input and prompts to OpenAI API! Any personal privacy, customer data privacy or intellectual property concerns should be taken into account BEFORE USING.**

Output may look right but be totally wrong, use as one more source and not as unique source of truth, like wordlist extension.

Input is limited and will be truncated to less than 4Kb. 

## Usage

Usage:

    pipegpt [-h] [-l] [-rl REPLY_LEN] [-m MODEL] [task]

Integrate ChatGPT into your command pipelines.

Positional arguments:

    task                  The task to execute. Known prompt to prepend to input.

Options:

    -h, --help            show this help message and exit
    -l, --list            Results are an unsorted list, get alternatives.
    -rl REPLY_LEN, --reply-len REPLY_LEN
                          Maximum reply length in characters. Prompt plus reply length are contrained to max length 4097.
    -m MODEL, --model MODEL
                          ML Model to use 'text' (default) for 'text-davinci-003' or 'code' for 'code-davinci-002'.

By default it just passes the input to chatGPT.

    $ echo "The moons of Mars are called" | pipegpt
    > Phobos and Deimos.

You can pass inline prompts to prepend to the input.

    cat words.txt | pipegpt "Which of these are fruits? One per line."
    > Coconut
    > Mandarin

Or you can choose prompts from templates. Also present results as a unique list (-l).

    cat passwords.txt | pipegpt -l password_suggest

Add your own tasks.

    echo "Tell me a joke about " > ~/.local/bin/tasks/joke_about.txt
    echo "chatbots" | pipegpt joke_about


Guess, Confirm, Guess Again!

    ffuf -w common.txt -s -recursion -u http://target.com/FUZZ > known.txt
    for i in $(seq 1 6); do
      cat known.txt | pipegpt -l -m code path_discovery > guess.txt
      ffuf -w known.txt -w guess.txt -s -recursion -u http://target.com/FUZZ > confirmed.txt
      cat confirmed.txt >> known.txt
    done


## Installation

    git clone https://github.com/sudoaza/pipegpt.git
    cd pipegpt
    pip install -r requirements.txt
    ln -s "$(pwd)/pipegpt" "$HOME/.local/bin/pipegpt"

### API Key

You need an OpenAI account. Visit https://beta.openai.com/account/api-keys

    echo 'export OPENAI_API_KEY="sk-..." >> ~/.profile' 

## Tasks

Note: If you want to share your task templates please include an example and create a PR.

### password_suggest

Get password suggestions from a list of known passwords.

### path_discovery

Get possible paths from a list of known paths.

### brief

Get a brief of the input text (in English).

### resumen

Devuelve un resumen del texto ingresado (en Castellano).

