#!/usr/bin/python3
import yaml
from yaml.loader import Loader
import random
from functools import reduce
from pathlib import Path

random.seed(0)

item_lut = "data/lookups/item.yml"

test_file = "tests/test_stories_python.yml"
Path(test_file).parent.mkdir(parents=True, exist_ok=True)

def map_idx_to_synonym(idx, n_synonyms: dict):
    for k, v in n_synonyms.items():
        if len(v) > idx:
            return k, v[idx]
        idx -= len(v)


with open(item_lut) as yamlfile:
    obj = yaml.load(yamlfile, Loader=Loader)
    raw_items: str = obj['nlu'][0]['examples']
    items = [item[2:] for item in raw_items.split('\n')]

tests = {"stories": []}

synonyms = {"add": ["add", "put", "buy", "insert"],
            "remove": ["remove", "delete", "destroy"]}

n_synonyms = reduce(lambda acc, n: acc+len(synonyms[n]), synonyms, 0)
r = random.randint(0, n_synonyms - 1)

for (idx, item) in enumerate(items):
    ret = map_idx_to_synonym((idx+r) % n_synonyms, synonyms)
    synonym, operation = ret
    single_test = {
        "story": f"LUT test {operation}({synonym}) {item}",
        "steps": [
            {"action": "action_listen"},
            {"user": f'[{operation}]' + r'{"entity": "operation", "value": "'+synonym+'"}',
             "intent": "operation_on_item"},
            {"action": "item_form"},
            {"active_loop": "item_form"},
            {"action": "action_listen"},
            {"user": f"[{item}](item)",
             "intent": "operation_on_item"},
            {"action": "item_form"},
            {"active_loop": None},
            {"action": "action_item"},
        ]
    }
    tests["stories"].append(single_test)

with open(test_file, "w") as testfile:
    yaml.dump(tests, testfile)


# stories:
# - story: A basic story test
#   steps:
#   - action: action_listen
#   - user: |
#       [add](operation)
#     intent: operation_on_item
#   - action: item_form
#   - active_loop: item_form
#   - action: action_listen
#   - user: |
#      [jam](item)
#     intent: operation_on_item
#   - action: item_form
#   - active_loop: null
#   - action: action_item
