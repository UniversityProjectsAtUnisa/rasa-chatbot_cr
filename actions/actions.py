from typing import Any, ItemsView, Text, Dict, List, Union, Optional, Tuple
from collections import defaultdict, OrderedDict

from word2number import w2n
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.types import DomainDict
from nltk.stem import PorterStemmer

stemmer = PorterStemmer()

DATA = defaultdict(int)


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
        # TODO: Use stem as id in the final database
        quantity = tracker.get_slot("CARDINAL")
        print(f"received: {operation=} {item=} {quantity=}")

        item, quantity = self.sanitize_itemquantity(item, quantity)

        item = stemmer.stem(item)

        if quantity == "":
            # when I say "remove item" I want to remove all of them
            quantity = '1' if operation == "add" else DATA[item]

        dispatcher.utter_message(text=f"{operation=}")
        if operation == "add":
            dispatcher.utter_message(text=f"Adding: {quantity=}, {item=}.")
            DATA[item] += int(quantity)
        elif operation == "remove":
            if DATA[item] == 0:
                dispatcher.utter_message(text=f"No {item=} found in the shopping list. {quantity=}.")
            else:
                dispatcher.utter_message(text=f"Removing: {quantity=}, {item=}.")
                new_quantity = DATA[item] - int(quantity)
                if new_quantity <= 0:
                    DATA.pop(item)
                else:
                    DATA[item] = new_quantity
        else:
            dispatcher.utter_message(text=f"Operation {operation} is invalid.")

        print(f"set: {operation=} {item=} {quantity=}")
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
        item = slot_value
        quantity = tracker.get_slot("CARDINAL")
        quantity = "" if quantity is None else quantity

        print(f"{item=} {quantity=}")

        nonnumeric_amount = len(list(filter(lambda x: not x.isnumeric(), quantity.split(
        )))) + len(list(filter(lambda x: not x.isnumeric(), item.split())))

        if nonnumeric_amount > 0:
            # azione
            return {"item": item if item is not None else ""}

        dispatcher.utter_message(response="utter_default")
        return {"item": None}

        # if item.replace(" ", '').isnumeric():
        #     if quantity.replace(" ", '').isnumeric():
        #         # item: quantity, quantity: quantity
        #         dispatcher.utter_message(response="utter_default")
        #         return {"item": None}
        #     else:
        #         # item: quantity, quantity: item
        #         return {"item": slot_value}

        # quantity=quantity+item, item: ?
        # numbers = list(filter(lambda x: x.isnumeric(), quantity.split()))
        # if 0 < len(numbers) < len(slot_value.split()):
        #     return {"item": slot_value}

        # if quantity is not None and quantity in slot_value:
        #     slot_value = slot_value.replace(quantity, '').strip()
        # return {"item": None if len(slot_value) == 0 else slot_value}

    # def validate_CARDINAL(
    #     self,
    #     slot_value: Any,
    #     dispatcher: CollectingDispatcher,
    #     tracker: Tracker,
    #     domain: DomainDict,
    # ) -> Dict[Text, Any]:
    #     quantity = "1"
    #     if slot_value is not None:
    #         for word in slot_value.split(" "):
    #             if word.isnumeric():
    #                 quantity = word
    #     return {"CARDINAL": quantity}

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

