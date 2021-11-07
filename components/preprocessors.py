import re
import typing
from typing import Any, Optional, Text, Dict, List, Type

from rasa.nlu.components import Component
from rasa.nlu.config import RasaNLUModelConfig
from rasa.shared.nlu.training_data.training_data import TrainingData
from rasa.shared.nlu.training_data.message import Message

if typing.TYPE_CHECKING:
    from rasa.nlu.model import Metadata


class ExcludePreprocessor(Component):
    """Preprocessors that substitutes exclude characters with substitute character"""
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
        phrase = message.data["text"]
        excludes = self.component_config["exclude"]
        sub = self.component_config["substistute"]
        table = str.maketrans(excludes, sub * len(excludes))
        phrase = phrase.translate(table)
        phrase = re.sub(sub + r'{2,}', sub, phrase)

        # Trim leading or trailing spaces...
        phrase = phrase.strip()

        found = []
        entry = {
            "original": message.text,
            "cleansed": phrase
        }
        print(f"{entry=}")
        found.append(entry)
        message.set(self.name, message.get(self.name, []) + found,
                    add_to_output=True)
        message.data["text"] = phrase

    def persist(self, file_name: Text, model_dir: Text) -> Optional[Dict[Text, Any]]:
        pass