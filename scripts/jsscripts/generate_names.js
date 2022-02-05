import { faker } from "@faker-js/faker";
import { ArgumentParser } from "argparse";
import { writeFile, readFile } from "fs/promises";

const TO_ADD = ["marco", "alessandro", "oussama", "giandomenico", "alessia", "mario", "antonio", "gennaro"]

const parser = new ArgumentParser({
  description: "Generate fake names in both italian and english"
})

parser.add_argument('-n', '--per-lang', { help: 'How many names per language', default: 100 });
parser.add_argument('-O', '--output', { help: 'Output filename', default: 'output.txt' });
parser.add_argument('-I', '--input', { help: 'Input filename', default: "input.txt" });
const n = parseInt(parser.parse_args().per_lang);
const output = parser.parse_args().output;
const input = parser.parse_args().input;

const LOCALES = ["it", "en"]
const generate_surname = (lang) => {
  faker.setLocale(lang);
  return faker.name.lastName();
}
const parse_names = (names) => ([...new Set(names.map(s => s.trim().toLowerCase()))].sort())
const add_surnames = (name => {
  const ri = Math.floor(Math.random() * (LOCALES.length + 1));
  if (ri >= LOCALES.length) return name;
  return `${name} ${generate_surname(LOCALES[ri])}`
})


let names = []
names = await readFile(input, { encoding: "utf-8" });
names = names.split("\n");


let parsed_names = names.concat(TO_ADD).map(add_surnames)
parsed_names = parse_names(parsed_names)
writeFile(output, parsed_names.join("\n"), { encoding: "utf-8" });
