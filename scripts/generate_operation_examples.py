#!/usr/bin/python3

import json
from test_generator import get_examples_from_yml
import random
import argparse
from pathlib import Path


PROJECT_PATH = Path(__file__).absolute().parent.parent


def item_generator():
    item_file = PROJECT_PATH.joinpath('data/lookups/item.yml')
    items = get_examples_from_yml(item_file)
    while True:
        yield random.choice(items)


def operation_generator():
    operations = ["[add](operation)",
                  '[put]{"entity": "operation", "value": "add"}',
                  '[buy]{"entity": "operation", "value": "add"}',
                  '[insert]{"entity": "operation", "value": "add"}',
                  "[remove](operation)",
                  '[delete]{"entity": "operation", "value": "remove"}',
                  '[destroy]{"entity": "operation", "value": "remove"}']
    while True:
        yield random.choice(operations)


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
    user_file = PROJECT_PATH.joinpath('data/lookups/user.yml')
    users = get_examples_from_yml(user_file)
    while True:
        yield random.choice(users)


def main(seed: int, template_amt: int, intent: str, basic_only: bool):
    random.seed(seed)
    AMOUNT_PER_TEMPLATE = template_amt
    OUTPUT_FILE = PROJECT_PATH.joinpath(f"examples/{intent}.txt")
    TEMPLATE_FILE = PROJECT_PATH.joinpath(f"scripts/templates/{intent}.json")

    with open(TEMPLATE_FILE) as f:
        data = json.load(f)

    templates = data["basic"]

    if not basic_only:
        templates += data["full"]

    entity_mapper = {
        "(item)": item_generator(),
        "(operation)": operation_generator(),
        "(CARDINAL)": CARDINAL_generator(),
        "(user)": user_generator()
    }

    examples = set()

    for _ in range(AMOUNT_PER_TEMPLATE):
        for t in templates:
            example = t
            for k, v in entity_mapper.items():
                if k in example:
                    if k == "(operation)":
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
