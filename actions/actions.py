from typing import Any, Text, Dict, List, Union

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

# def get_entity_from_list(slots: Union[Any, List[Any]]):
#     print(slots)
#     if isinstance(slots, list):
#         return slots[0] if len(set(slots)) == 1 else None
#     return slots

class ActionItem(Action):
    def name(self) -> Text:
        return "action_item"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        operation = tracker.get_slot("operation")
        item = tracker.get_slot("item")

        dispatcher.utter_message(text=f"{operation=}")
        if operation == "add":
            dispatcher.utter_message(text=f"Adding item {item}.")
        elif operation == "remove":
            dispatcher.utter_message(text=f"Removing item {item}.")
        else:
            dispatcher.utter_message(text=f"Operation {operation} is invalid.")

        return [SlotSet("item", None), SlotSet("operation", None)]
