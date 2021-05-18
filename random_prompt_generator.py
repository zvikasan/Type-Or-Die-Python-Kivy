import requests
import re
from random import sample
import secret_keys

def random_war_and_peace_sentence():
    with open("war-and-peace.txt", encoding="utf8") as file:
        contents = file.read()

    sentences = []
    sentences += re.findall(r".*?[\.\!\?]+", contents)
    selected = sample(sentences, 1)[0]
    return selected

# Getting a randomly generated text paragraph from deepai.org using a random sentence from "War and Peace" as input

def random_prompt(num_of_sentences):
    r = requests.post(
        "https://api.deepai.org/api/text-generator",
        data={
            'text': random_war_and_peace_sentence(),
        },
        headers={'api-key': secret_keys.DEEPAI_API_KEY}
    )
    y = r.json()

    sentences = []
    # Splitting the random text paragraph into sentences.
    sentences += re.findall(r".*?[\.\!\?]+", y['output'])

    # Choosing random sentence(s) from the list of sentence generated above
    selected = sample(sentences, num_of_sentences)
    
    final_prompt = ''
    
    for item in selected:
        final_prompt += item
        final_prompt += ' '

    return final_prompt


