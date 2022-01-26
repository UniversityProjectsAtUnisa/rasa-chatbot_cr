# RASA AI Project

Nella cartella script abbiamo:
- generate_operation_examples.py che genera a partire da un set di operazioni, informazioni e cardinalità degli esempi per l'intento operation_on_item. Gli esempi saranno nella cartella "examples" nel file "operation_on_item.txt"
- test_generator.py che genera delle storie a partire da elementi, operazioni e cardinalità. Il report della generazione dei test sarò nella cartella "tests" nel file "test_stories_python.yml"
- find_mismatch.py che apre il report generato da "rasa test" e scrive su file per quali elemento, operazione e cardinalità non ha ottenuto una precision pari a 1.0. Il risulato sarà consultabile nella cartella "errors" nel file "LUT.txt"

## PER TESTARE
1. python3 test_generator.py
2. rasa test
3. python3 find_mismatch.py

## REQUISITI
Prima di avviare installare le dipendenze\
`pip install -r requirements.txt`