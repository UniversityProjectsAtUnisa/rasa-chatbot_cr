from word2number import w2n

american_number_system = {
        'zero': 0,
        'one': 1,
        'two': 2,
        'three': 3,
        'four': 4,
        'five': 5,
        'six': 6,
        'seven': 7,
        'eight': 8,
        'nine': 9,
        'ten': 10,
        'eleven': 11,
        'twelve': 12,
        'thirteen': 13,
        'fourteen': 14,
        'fifteen': 15,
        'sixteen': 16,
        'seventeen': 17,
        'eighteen': 18,
        'nineteen': 19,
        'twenty': 20,
        'thirty': 30,
        'forty': 40,
        'fifty': 50,
        'sixty': 60,
        'seventy': 70,
        'eighty': 80,
        'ninety': 90,
        'hundred': 100,
        'thousand': 1000,
        'million': 1000000,
        'billion': 1000000000,
        'point': '.'
    }

def _find_end_of_number(booleans_list, left):
        idx = left
        if not booleans_list[idx]:
            return -1
        while idx + 2 < len(booleans_list):
            if booleans_list[idx+1] == False and booleans_list[idx+2] == False:
                return idx
            idx += 1
        return (idx + 1) if booleans_list[idx + 1] else idx

def process(message: str):
    phrase = message
    if phrase is None:
        return
    phrase = phrase.replace('-', ' ').replace(",", ' ').replace('.', ' ')
    number_sentence = phrase.lower()
    split_words = number_sentence.strip().split()

    booleans_list = [
        word in american_number_system for word in split_words]

    numbers_boundaries = list()
    left, right = 0, 0
    while left < len(booleans_list):
        if booleans_list[left]:
            right = _find_end_of_number(booleans_list, left)
            numbers_boundaries.append((left, right))
            left = right
        left += 1

    text = phrase.strip().split()

    newtext = []
    idx = 0

    for left, right in numbers_boundaries:
        newtext += text[idx:left]
        number = w2n.word_to_num(" ".join(split_words[left:right + 1]))
        newtext.append(str(number))
        idx = right+1

    newtext += text[idx:]
    newtext = " ".join(newtext)

    print(f"{newtext=}")



# four hundred fifteen
# two thousand three hundred fifty-six
# five hundred twenty-one thousand three hundred sixty-seven
# two thousand one hundred thirty-four

t1 = "is simply dummy four hundred fifteen text of the printing two thousand three hundred fifty-six and typesetting industry. Lorem Ipsum has"
t2 = "dummy text of the printing five hundred twenty-one thousand three hundred sixty-seven and typesetting industry. Lorem Ipsum has"
t3 = "dummy text of the printing and typesetting industry. two thousand one hundred thirty-four Lorem Ipsum has"

process(t1)
process(t2)
process(t3)