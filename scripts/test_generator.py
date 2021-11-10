#!/usr/bin/python3
import yaml
from yaml.loader import Loader
import random
from functools import reduce
from pathlib import Path
from num2words import num2words



def map_idx_to_synonym(idx, n_synonyms: dict):
    for k, v in n_synonyms.items():
        if len(v) > idx:
            return k, v[idx]
        idx -= len(v)

def get_obj_from_yml(filename):
    with open(filename) as yamlfile:
        return yaml.load(yamlfile, Loader=Loader)

def dump_obj_on_yml(filename, data):
    with open(filename, "w") as testfile:
        yaml.dump(data, testfile)

def get_items_from_yml(filename):
    obj = get_obj_from_yml(filename)
    raw_items: str = obj['nlu'][0]['examples']
    items = [item[2:] for item in raw_items.split('\n')]
    return items




def main():
    random.seed(0)

    item_lut = "data/lookups/item.yml"

    test_file = "tests/test_stories_python.yml"
    Path(test_file).parent.mkdir(parents=True, exist_ok=True)

    items = get_items_from_yml(item_lut)

    tests = {"stories": []}

    synonyms = {"add": ["add", "put", "buy", "insert"],
                "remove": ["remove", "delete", "destroy"]}

    n_synonyms = reduce(lambda acc, n: acc+len(synonyms[n]), synonyms, 0)
    r = random.randint(0, n_synonyms - 1)

    for (idx, item) in enumerate(items):
        ret = map_idx_to_synonym((idx+r) % n_synonyms, synonyms)
        synonym, operation = ret

        r_number = (idx+r) % 2
        number = ""
        if r_number == 0:
            number = f"[{idx}](CARDINAL)"

        single_test = {
            "story": f"LUT test {operation}({synonym}) {item}",
            "steps": [
                {"action": "action_listen"},
                {"user": f'[{operation}]' + r'{"entity": "operation", "value": "'+synonym+'"}',
                "intent": "operation_on_item"},
                {"action": "item_form"},
                {"active_loop": "item_form"},
                {"action": "action_listen"},
                {"user": f"{number} [{item}](item)",
                "intent": "operation_on_item"},
                {"action": "item_form"},
                {"active_loop": None},
                {"action": "action_item"},
            ]
        }
        tests["stories"].append(single_test)

    dump_obj_on_yml(test_file, tests)

    

if __name__ == "__main__":
    main()