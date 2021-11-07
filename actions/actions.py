from typing import Any, Text, Dict, List, Union, Optional, Tuple

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.types import DomainDict

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
        quantity = tracker.get_slot("CARDINAL")

        dispatcher.utter_message(text=f"{operation=}")
        if operation == "add":
            dispatcher.utter_message(text=f"Adding {quantity} item {item}.")
        elif operation == "remove":
            dispatcher.utter_message(text=f"Removing {quantity} item {item}.")
        else:
            dispatcher.utter_message(text=f"Operation {operation} is invalid.")

        return [SlotSet("item", None), SlotSet("operation", None), SlotSet("CARDINAL", None)]


# class ValidateItemForm(FormValidationAction):
#     def name(self) -> Text:
#         return "validate_item_form"

#     async def required_slots(
#         self,
#         slots_mapped_in_domain: List[Text],
#         dispatcher: "CollectingDispatcher",
#         tracker: "Tracker",
#         domain: "DomainDict",
#     ) -> Optional[List[Text]]:
#         required_slots = slots_mapped_in_domain + ["CARDINAL"]
#         return required_slots

#     @classmethod
#     def _filter_number(cls, text, default_quantity=1) -> Tuple[Text, int]:
#         if text is None:
#             return None, None
#         print(text)
#         words = []
#         quantity = default_quantity
#         for word in text.split(" "):
#             if word.isnumeric():
#                 quantity = word
#             else:
#                 words.append(word)
#         return " ".join(words), quantity

#     async def extract_CARDINAL(
#         self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
#     ) -> Dict[Text, Any]:
#         quantity = tracker.get_slot("CARDINAL")
#         quantity_item, quantity = self._filter_number(quantity, 1)

#         item = tracker.get_slot("item")
#         item, item_quantity = self._filter_number(item, 1)

#         item = quantity_item if item is None else item
#         quantity = item_quantity if quantity is None else quantity

#         return {"item": item, "CARDINAL": str(quantity)}

#     def validate_CARDINAL(
#         self,
#         slot_value: Any,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: DomainDict,
#     ) -> Dict[Text, Any]:

#         return {"CARDINAL": slot_value}

#     def validate_item(
#         self,
#         slot_value: Any,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: DomainDict,
#     ) -> Dict[Text, Any]:

#         return {"item": slot_value}

#     def validate_operation(
#         self,
#         slot_value: Any,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: DomainDict,
#     ) -> Dict[Text, Any]:

#         return {"operation": slot_value}
