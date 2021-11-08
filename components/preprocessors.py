from collections import defaultdict
import re
import typing
from typing import Any, Optional, Text, Dict, List, Type

from rasa.nlu.components import Component
from rasa.nlu.config import RasaNLUModelConfig
from rasa.shared.nlu.training_data.training_data import TrainingData
from rasa.shared.nlu.training_data.message import Message
from word2number import w2n

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

    defaults = {}
    supported_language_list = "en"
    not_supported_language_list = None

    def __init__(self, component_config: Optional[Dict[Text, Any]] = None) -> None:
        super().__init__(component_config)

    def train(
        self,
        training_data: TrainingData,
        config: Optional[RasaNLUModelConfig] = None,
        **kwargs: Any,
    ) -> None:
        pass

    @classmethod
    def _find_end_of_number(cls, booleans_list: List[Text], left: int) -> bool:
        idx = left
        if not booleans_list[idx]:
            return -1
        while idx + 2 < len(booleans_list):
            if booleans_list[idx+1] == False and booleans_list[idx+2] == False:
                return idx
            idx += 1
        return (idx + 1) if booleans_list[idx + 1] else idx

    def process(self, message: Message, **kwargs: Any) -> None:
        phrase = message.get('text')
        if phrase is None:
            return
        number_sentence = phrase.lower()
        split_words = number_sentence.strip().split()

        booleans_list = [
            word in self.american_number_system for word in split_words]

        numbers_boundaries = list()
        left, right = 0, 0
        while left < len(booleans_list):
            if booleans_list[left]:
                right = self._find_end_of_number(booleans_list, left)
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

        message.set('text', newtext, True)

    def persist(self, file_name: Text, model_dir: Text) -> Optional[Dict[Text, Any]]:
        pass
