from typing import Any, ItemsView, Text, Dict, List, Union, Optional, Tuple
from collections import defaultdict, OrderedDict

from word2number import w2n
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.types import DomainDict


class ActionItem(Action):
    def name(self) -> Text:
        return "action_item"

    @classmethod
    def sanitize_itemquantity(cls, item, quantity):
        item = "" if item is None else item
        quantity = "" if quantity is None else quantity

        # Se andavano già bene esci
        item_cond = all(not word.isnumeric() for word in item.split())
        quantity_cond = quantity.replace(" ", '').isnumeric()

        if item_cond and quantity_cond:
            return item, quantity

        final_quantity = ""
        for word in (quantity + " " + item).split():
            if word.isnumeric():
                final_quantity = word
                break

        # concatena togli numeri togli duplicati
        itemquantity = (item + " " + quantity).split()

        duplicated_list = list(filter(lambda x: not x.isnumeric(), itemquantity))

        item = " ".join(OrderedDict.fromkeys(duplicated_list).keys())
        return item, final_quantity

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        operation = tracker.get_slot("operation")
        item = tracker.get_slot("item")
        quantity = tracker.get_slot("CARDINAL")

        item, quantity = self.sanitize_itemquantity(item, quantity)

        if quantity == "":
            # when I say "remove item" I want to remove all of them
            quantity = '1' if operation == "add" else "all"

        dispatcher.utter_message(text=f"__{operation}__,{quantity},{item}")

        return [SlotSet("item", None), SlotSet("operation", None), SlotSet("CARDINAL", None)]


class ActionShowItems(Action):
    def name(self) -> Text:
        return "action_show_items"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="__show__")
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
        item = slot_value
        quantity = tracker.get_slot("CARDINAL")
        quantity = "" if quantity is None else quantity

        nonnumeric_amount = len(list(filter(lambda x: not x.isnumeric(), quantity.split(
        )))) + len(list(filter(lambda x: not x.isnumeric(), item.split())))

        if nonnumeric_amount > 0:
            # azione
            return {"item": item if item is not None else ""}

        dispatcher.utter_message(response="utter_default")
        return {"item": None}

    def validate_operation(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if slot_value not in ["add", "remove"]:
            dispatcher.utter_message(response="utter_default")
            return {"operation": None}
        return {"operation": slot_value}

