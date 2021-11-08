from typing import Any, Text, Dict, List, Union, Optional, Tuple
from collections import defaultdict

from word2number import w2n
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.types import DomainDict

DATA = defaultdict(int)


class ActionItem(Action):
    def name(self) -> Text:
        return "action_item"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        operation = tracker.get_slot("operation")
        item = tracker.get_slot("item")
        quantity = tracker.get_slot("CARDINAL")
        print(f"{operation=} {item=} {quantity=}")
        if quantity is None:
            quantity = '1'

        dispatcher.utter_message(text=f"{operation=}")
        if operation == "add":
            dispatcher.utter_message(text=f"Adding: {quantity=}, {item=}.")
            DATA[item] += int(quantity)
        elif operation == "remove":
            dispatcher.utter_message(text=f"Removing: {quantity=}, {item=}.")
            new_quantity = DATA[item] - int(quantity)
            if new_quantity <= 0:
                DATA.pop(item)
            else:
                DATA[item] = new_quantity
        else:
            dispatcher.utter_message(text=f"Operation {operation} is invalid.")

        return [SlotSet("item", None), SlotSet("operation", None), SlotSet("CARDINAL", None)]


class ActionShowItems(Action):
    def name(self) -> Text:
        return "action_show_items"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if len(DATA) == 0:
            dispatcher.utter_message(text='Your shopping list is empty')
        else:
            title = '# -------- SHOPPING LIST  -------- #\n'
            rows = (f'{name} - {quantity}' for name, quantity in DATA.items())
            dispatcher.utter_message(text=title + '\n'.join(rows))
        return []


class ValidateItemForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_item_form"

    def validate_item(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        quantity = tracker.get_slot("CARDINAL")
        if quantity is not None and quantity in slot_value:
            slot_value = slot_value.replace(quantity, '').strip()
        return {"item": slot_value}

    def validate_CARDINAL(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {"CARDINAL": slot_value}

    def validate_operation(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {"operation": slot_value}
