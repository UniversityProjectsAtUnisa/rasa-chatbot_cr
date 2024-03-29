#!/usr/bin/python3

import json
from test_generator import get_examples_from_yml
import random
import argparse
from pathlib import Path


PROJECT_PATH = Path(__file__).absolute().parent.parent
DATA_FOLDER = "data"
DATA_PATH = PROJECT_PATH.joinpath(DATA_FOLDER)

PREFIX_CHANCE = 0.5
SUFFIX_CHANCE = 0.8


def item_generator():
    item_file = DATA_PATH.joinpath('lookups/item.yml')
    items = get_examples_from_yml(item_file)
    while True:
        yield random.choice(items)


def operation_generator():
    all_operations = [
        '[aggiungere]{"entity":"operation", "value": "add"}',
        '[aggiungi]{"entity":"operation", "value": "add"}',
        '[inserire]{"entity":"operation", "value": "add"}',
        '[inserisci]{"entity":"operation", "value": "add"}',
        '[comprare]{"entity":"operation", "value": "add"}',
        '[compra]{"entity":"operation", "value": "add"}',
        '[mettere]{"entity":"operation", "value": "add"}',
        '[metti]{"entity":"operation", "value": "add"}',
        '[rimuovere]{"entity":"operation", "value": "remove"}',
        '[rimuovi]{"entity":"operation", "value": "remove"}',
        '[cancellare]{"entity":"operation", "value": "remove"}',
        '[cancella]{"entity":"operation", "value": "remove"}',
        '[distruggere]{"entity":"operation", "value": "remove"}',
        '[distruggi]{"entity":"operation", "value": "remove"}',
        '[sottrarre]{"entity":"operation", "value": "remove"}',
        '[sottrai]{"entity":"operation", "value": "remove"}',
        '[togliere]{"entity":"operation", "value": "remove"}',
        '[togli]{"entity":"operation", "value": "remove"}',
    ]
    while True:
        yield random.choice(all_operations)


def add_operation_generator():
    add_operations = [
        '[aggiungere]{"entity":"operation", "value": "add"}',
        '[aggiungi]{"entity":"operation", "value": "add"}',
        '[inserire]{"entity":"operation", "value": "add"}',
        '[inserisci]{"entity":"operation", "value": "add"}',
        '[comprare]{"entity":"operation", "value": "add"}',
        '[compra]{"entity":"operation", "value": "add"}',
        '[mettere]{"entity":"operation", "value": "add"}',
        '[metti]{"entity":"operation", "value": "add"}',
    ]
    while True:
        yield random.choice(add_operations)


def remove_operation_generator(add_tutto=False):
    remove_operations = [
        '[rimuovere]{"entity":"operation", "value": "remove"}',
        '[rimuovi]{"entity":"operation", "value": "remove"}',
        '[cancellare]{"entity":"operation", "value": "remove"}',
        '[cancella]{"entity":"operation", "value": "remove"}',
        '[distruggere]{"entity":"operation", "value": "remove"}',
        '[distruggi]{"entity":"operation", "value": "remove"}',
        '[sottrarre]{"entity":"operation", "value": "remove"}',
        '[sottrai]{"entity":"operation", "value": "remove"}',
        '[togliere]{"entity":"operation", "value": "remove"}',
        '[togli]{"entity":"operation", "value": "remove"}',
    ]
    tutto_chunks = ['tutto', 'tutto il', 'tutto lo', 'tutti', 'tutti i', 'tutte le', 'tutta', 'tutta la']
    while True:
        op = random.choice(remove_operations)
        if add_tutto:
            op += f" {random.choice(tutto_chunks)}"
        yield op


def _clamp(n, _min, _max):
    return max(min(n, _max), _min)


def CARDINAL_generator():
    range = (0, 1 << 31)
    while True:
        r = random.gauss(0, 1000)
        positive_int = int(abs(r)) + 1
        clamped = _clamp(positive_int, *range)
        yield str(clamped)


def user_generator():
    user_file = DATA_PATH.joinpath('lookups/user.yml')
    users = get_examples_from_yml(user_file)
    while True:
        yield random.choice(users)


def get_example_from_template(template):
    if isinstance(template, dict):
        example = template['example']
        pre = random.choice(template.get('prefixes', ['']))
        suff = random.choice(template.get('suffixes', ['']))
        if random.random() > PREFIX_CHANCE and pre:
            example = f'{pre} {example}'
        if random.random() > SUFFIX_CHANCE and suff:
            example = f'{example} {suff}'
        return example
    return template


def main(seed: int, template_amt: int, intent: str, basic_only: bool):
    random.seed(seed)
    AMOUNT_PER_TEMPLATE = template_amt
    OUTPUT_FILE = PROJECT_PATH.joinpath(f"examples/{intent}.txt")
    TEMPLATE_FILE = PROJECT_PATH.joinpath(f"scripts/templates_ita/{intent}.json")

    with open(TEMPLATE_FILE) as f:
        data = json.load(f)

    templates = data
    if isinstance(templates, dict):
        templates = data["basic"]
        if not basic_only:
            templates += data["full"]

    entity_mapper = {
        "(item)": item_generator(),
        "(operation)": None,
        "(remove_tutto_operation)": remove_operation_generator(True),
        "(CARDINAL)": CARDINAL_generator(),
        "(user)": user_generator()
    }

    operation_generators = {
        "add": add_operation_generator(),
        "remove": remove_operation_generator(),
        "all": operation_generator()
    }

    examples = set()

    for t in templates:
        multiplier = 1.0
        if isinstance(t, dict) and 'amount_multiplier' in t:
            multiplier = t['amount_multiplier']
        for _ in range(int(multiplier*AMOUNT_PER_TEMPLATE)):
            example = get_example_from_template(t)

            op_generator = operation_generators["all"]
            if "alla" in example:
                op_generator = operation_generators["add"]
            if "dalla" in example:
                op_generator = operation_generators["remove"]

            for k, v in entity_mapper.items():
                if k in example:
                    if k == "(operation)":
                        example = example.replace(k, next(op_generator))
                    elif k == "(remove_tutto_operation)":
                        example = example.replace(k, next(v))
                    else:
                        example = example.replace(k, f"[{next(v)}]{k}")

            examples.add(example)

    result = "- "+"\n- ".join(sorted(examples))
    print(f"generated {len(examples)} examples")

    Path(OUTPUT_FILE).parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        f.write(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=0,
                        help="Seed identifier for the random generation")
    parser.add_argument("--template-amt", type=int,
                        default=100, help="How many phrases per template")
    parser.add_argument("--intent", type=str,
                        required=True, help="Intent for which generate examples")

    parser.add_argument('--all', dest='basic_only', action='store_false')
    parser.add_argument('--basic-only', dest='basic_only', action='store_true')
    parser.set_defaults(basic_only=False)

    kwargs = vars(parser.parse_args())
    main(**kwargs)
