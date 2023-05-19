import os
import openai
import tiktoken

from transformers import GPT2TokenizerFast, logging

logging.set_verbosity_error()

# Set up the OpenAI API credentials
openai.api_key = os.environ['OPENAI_API_KEY']

cached_tokenizer = None

def gpt2_tokenizer():
  global cached_tokenizer
  if cached_tokenizer is None:
    cached_tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
  return cached_tokenizer

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def token_count3(text):
  return num_tokens_from_string(text, "cl100k_base")

def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301"):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model == "gpt-3.5-turbo":
        print("Warning: gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-0301.")
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301")
    elif model == "gpt-4":
        print("Warning: gpt-4 may change over time. Returning num tokens assuming gpt-4-0314.")
        return num_tokens_from_messages(messages, model="gpt-4-0314")
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif model == "gpt-4-0314":
        tokens_per_message = 3
        tokens_per_name = 1
    else:
        raise NotImplementedError(f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens

def token_count(text):
  tokenizer = gpt2_tokenizer()
  token_dict = tokenizer(text)
  return len(token_dict['input_ids'])

def truncate(text, max_tokens=4096, split_str="\n", token_counter=token_count):
  keep = ""
  for piece in text.split(split_str):
    if token_counter(keep + split_str + piece) > max_tokens:
      break
    keep += split_str + piece
  return keep

def chunk(text, max_tokens=4096, split_str="\n", token_counter=token_count):
  chunks = []
  while len(text) > 0:
    chunk = truncate(text, max_tokens=max_tokens, split_str=split_str)
    text = text[len(chunk):]
    if len(chunk) < 3:
      break
    chunks.append(chunk)
  return chunks

# Call Openai completion API.
def complete(prompt, max_tokens=1000, temperature=0.7, model='text-davinci-003', best_of=3):
  api_params = {
    'engine': model,
    'prompt': prompt,
    'temperature': temperature,
    'max_tokens': max_tokens,
    'best_of': best_of,
  }
  for _ in range(3):
    try:
      response = openai.Completion.create(**api_params)
      generated_text = response.choices[0].text
      return generated_text
    except openai.error.APIConnectionError as e:
      pass
  raise e

def truncate_and_complete(prompt, max_tokens=1000, temperature=0.7, model='text-davinci-003', best_of=3, model_max_tokens=4096, split_str="\n"):
  truncated_prompt = truncate(
    prompt,
    max_tokens=model_max_tokens-response_max_tokens,
    split_str=split_str
  )
  return complete(
    truncated_prompt,
    max_tokens=max_tokens,
    temperature=temperature,
    model=model,
    best_of=best_of
  )


def usermsg(msg):
  return {"role":"user","content":msg}

def agentmsg(msg):
  return {"role":"assistant","content":msg}

def sysmsg(msg):
  return {"role":"system","content":msg}


def chat_complete(prompt, system="You are a helpful assistant.", model="gpt-3.5-turbo"):
  if type(prompt) == str:
    prompt = [{"role": "system", "content": system }, usermsg(prompt)]

  response = openai.ChatCompletion.create(model=model, messages=prompt)
  response_text = response.choices[0].message.content
  prompt.append(agentmsg(response_text))
  return prompt, response_text

def truncate_convo(convo, max_tokens=4096):
  while num_tokens_from_messages(convo) > max_tokens:
    convo = convo[1:]
  return convo