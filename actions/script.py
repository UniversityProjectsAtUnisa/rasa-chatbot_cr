import csv
from functools import reduce

filename = "../data/Groceries_dataset.csv"
output_filename = "../data/groceries.txt"

with open(filename, newline="") as csvfile:
    table = list(csv.reader(csvfile))

    names = [row[-1] for row in table[1:]]
    splitted_names = [name.split("/") for name in names]
    set_names = set(reduce(lambda acc, n: acc+n, splitted_names, []))
    with open(output_filename, "w") as wfile:
        wfile.write("\n".join(set_names))
    print("done")