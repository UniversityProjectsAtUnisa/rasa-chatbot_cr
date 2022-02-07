from collections import defaultdict
import re
import typing
from typing import Any, Optional, Text, Dict, List, Tuple, Type
from num2words import num2words


from rasa.nlu.components import Component
from rasa.nlu.config import RasaNLUModelConfig
from rasa.shared.nlu.training_data.training_data import TrainingData
from rasa.shared.nlu.training_data.message import Message

if typing.TYPE_CHECKING:
    from rasa.nlu.model import Metadata


class ExcludePreprocessor(Component):
    """Preprocessors that replaces exclude characters with substitute character"""
    @classmethod
    def required_components(cls) -> List[Type[Component]]:
        return []

    defaults = {"exclude": "-", "substitute": " "}
    supported_language_list = None
    not_supported_language_list = None

    def __init__(self, component_config: Optional[Dict[Text, Any]] = None) -> None:
        super().__init__(component_config)
        if "substitute" in component_config and len(component_config["substitute"]) != 1:
            raise Exception("substitute config must be one single character")

    def train(
        self,
        training_data: TrainingData,
        config: Optional[RasaNLUModelConfig] = None,
        **kwargs: Any,
    ) -> None:
        pass

    def process(self, message: Message, **kwargs: Any) -> None:
        phrase = message.get('text')
        if phrase is None:
            return

        excludes = self.component_config["exclude"]
        sub = self.component_config["substitute"]

        table = str.maketrans(excludes, sub * len(excludes))
        phrase = phrase.translate(table)
        phrase = re.sub(sub + r'{2,}', sub, phrase)
        phrase = phrase.strip()         # Trim leading or trailing spaces...

        message.set('text', phrase, True)

    def persist(self, file_name: Text, model_dir: Text) -> Optional[Dict[Text, Any]]:
        pass


class W2NPreprocessor(Component):
    """Preprocessors that replaces numbers written in english to decimal numbers"""
    @classmethod
    def required_components(cls) -> List[Type[Component]]:
        return []

    _italian_number_system = (
        ('dieci', '10'),
        ('undici', '11'),
        ('dodici', '12'),
        ('tredici', '13'),
        ('quattordici', '14'),
        ('quindici', '15'),
        ('sedici', '16'),
        ('diciasette', '17'),
        ('diciotto', '18'),
        ('diciannove', '19'),
        ('venti', '20'), ('vent', '20'),
        ('trenta', '30'), ('trent', '30'),
        ('quaranta', '40'), ('quarant', '40'),
        ('cinquanta', '50'), ('cinquant', '50'),
        ('sessanta', '60'), ('sessant', '60'),
        ('settanta', '70'), ('settant', '70'),
        ('ottanta', '80'), ('ottant', '80'),
        ('novanta', '90'), ('novant', '90'),
        ('cento', '100'),
        ('mille', '1000'), ('mila', '1000'),
        ('milione', '1000000'), ('milioni', '1000000'),
        ('miliardo', '1000000000'), ('miliardi', '1000000000'),
        ('uno', '1'), ('un', '1'),
        ('due', '2'),
        ('tre', '3'),
        ('quattro', '4'),
        ('cinque', '5'),
        ('sei', '6'),
        ('sette', '7'),
        ('otto', '8'),
        ('nove', '9'),
    )

    defaults = {"exclude": ",-.", "substitute": " "}
    supported_language_list = "it"
    not_supported_language_list = None

    def __init__(self, component_config: Optional[Dict[Text, Any]] = None) -> None:
        super().__init__(component_config)
        if "substitute" in component_config and len(component_config["substitute"]) != 1:
            raise Exception("substitute config must be one single character")

    def train(
        self,
        training_data: TrainingData,
        config: Optional[RasaNLUModelConfig] = None,
        **kwargs: Any,
    ) -> None:
        pass

    _NUMBERS = dict(_italian_number_system)

    _TOKEN_REGEX = re.compile('|'.join(f'({num})' for num, val in _italian_number_system))

    @staticmethod
    def normalize_text(num_repr):
        '''Return a normalized version of *num_repr* that can be passed to w2n.'''
        return "".join(num_repr.lower().split())

    def w2n(self, num_repr):
        '''Yield the numeric representation of *num_repr*.'''

        result = ''

        for token in (tok for tok in self._TOKEN_REGEX.split(num_repr) if tok):
            try:
                value = self._NUMBERS[token]
            except KeyError:
                if token not in ('di', 'e'):
                    raise ValueError(f'Invalid number representation: {num_repr}')
                continue

            if token == 'miliardi':
                result += '0'*9
            elif token in ('mila', 'milioni'):
                zeros = '0' * value.count('0')
                piece = result[-3:].lstrip('0')
                result = (result[:-len(piece)-len(zeros)] + piece + zeros)
            elif not result:
                result = value
            else:
                length = len(value)
                non_zero_values = len(value.strip('0'))
                if token in ('cento', 'milione', 'miliardo'):
                    if result[-1] != '0':
                        result = (result[:-length] + result[-1] + '0' * value.count('0'))
                        continue
                result = (result[:-length] +
                          value.rstrip('0') +
                          result[len(result) - length + non_zero_values:])
        return result

    @staticmethod
    def _n2w(number_sentence):
        chunks = number_sentence.split()
        for i in range(len(chunks)):
            if chunks[i].isnumeric():
                chunks[i] = num2words(int(chunks[i]), lang="it")
        return " ".join(chunks)

    def _is_valid_word(self, word):
        try:
            self.w2n(word)
            return True
        except:
            return False

    @staticmethod
    def _find_end_of_number(booleans_list: List[bool], left: int) -> int:
        idx = left
        if not booleans_list[idx]:
            return -1
        while idx + 1 < len(booleans_list):
            if booleans_list[idx+1] == False:
                return idx
            idx += 1
        if idx + 1 >= len(booleans_list):
            return idx
        return (idx + 1) if booleans_list[idx+1] else idx

    @staticmethod
    def _split_with_indices(text: str) -> List[Tuple[str, int, int]]:
        res = []

        idx = 0
        while idx < len(text):
            if text[idx].isalpha():
                start = idx
                while idx < len(text) and text[idx].isalpha():
                    idx += 1
                res.append((text[start:idx], start, idx))
            else:
                idx += 1

        return res

    def process(self, message, **kwargs: Any) -> None:
        phrase = message.get('text')
        if phrase is None:
            return
        number_sentence = phrase.lower()

        excludes = self.component_config["exclude"]
        sub = self.component_config["substitute"]

        table = str.maketrans(excludes, sub * len(excludes))
        number_sentence = number_sentence.translate(table)

        # Split su "uno o più spazi"
        # Tupla di (parola, inizio, fine)
        # Quando metti insieme: text [:inizio1] numero1 text[fine1:inizio2]...
        number_sentence = self._n2w(number_sentence)
        split_data = self._split_with_indices(number_sentence)

        split_words = [word[0] for word in split_data]

        booleans_list = [self._is_valid_word(word) for word in split_words]

        numbers_boundaries = list()
        left, right = 0, 0
        while left < len(booleans_list):
            if booleans_list[left]:
                right = self._find_end_of_number(booleans_list, left)
                numbers_boundaries.append((left, right))
                left = right
            left += 1

        newtext = ""
        idx = 0

        for left, right in numbers_boundaries:
            origin_left = split_data[left][1]
            origin_right = split_data[right][2]

            newtext += number_sentence[idx:origin_left]
            number = self.w2n(self.normalize_text(" ".join(split_words[left:right + 1])))
            newtext += str(number)

            idx = origin_right

        newtext += number_sentence[idx:]
        message.set('text', newtext, True)

    def persist(self, file_name: Text, model_dir: Text) -> Optional[Dict[Text, Any]]:
        pass
