#!/usr/bin/python3

from test_generator import get_items_from_yml
import random
from pathlib import Path


def item_generator():
    item_file = "data/lookups/item.yml"
    items = get_items_from_yml(item_file)
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


def main():
    random.seed(0)
    AMOUNT_PER_TEMPLATE = 100
    OUTPUT_FILE = "examples/operation_on_item.txt"

    templates = ["(CARDINAL) (item)",
                 "(item)",
                 "(operation)",
                 "(operation) (CARDINAL) (item)",
                 "(operation) (CARDINAL) (item) from the shopping list",
                 "(operation) (CARDINAL) (item) to the shopping list",
                 "(operation) (item)",
                 "(operation) (item) from the shopping list",
                 "(operation) (item) to the shopping list",
                 "(operation) a (item)",
                 "can I (operation) some (item)",
                 "i want to (operation)",
                 "i want to (operation) (CARDINAL) (item)",
                 "i want to (operation) (CARDINAL) (item) from my list",
                 "i want to (operation) (CARDINAL) (item) from my shopping list",
                 "i want to (operation) (CARDINAL) (item) to my list",
                 "i want to (operation) (CARDINAL) (item) to my shopping list",
                 "i want to (operation) (item)",
                 "i want to (operation) some (item)",
                 "i would like to (operation) (CARDINAL) (item)",
                 "i would like to (operation) (item)",
                 "i would like to (operation) a (item)",
                 "i'd like to (operation) (CARDINAL) (item)",
                 "i'd like to (operation) (CARDINAL) (item) from my list",
                 "i'd like to (operation) (CARDINAL) (item) from my shopping list",
                 "i'd like to (operation) (CARDINAL) (item) to my list",
                 "i'd like to (operation) (CARDINAL) (item) to my shopping list",
                 "i'd like to (operation) (item)",
                 "i'd like to (operation) (item) from my list",
                 "i'd like to (operation) (item) from my shopping list",
                 "i'd like to (operation) (item) to my list",
                 "i'd like to (operation) (item) to my shopping list",
                 "some (item)"
                 ]

    entity_mapper = {
        "(item)": item_generator(),
        "(operation)": operation_generator(),
        "(CARDINAL)": CARDINAL_generator()
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
    main()
