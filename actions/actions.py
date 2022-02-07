import sys
from typing import Any, Text, Dict, List
from collections import OrderedDict

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, FollowupAction
from rasa_sdk.types import DomainDict


class ActionItem(Action):
    def name(self) -> Text:
        return "action_item"

    @classmethod
    def sanitize_itemquantity(cls, item, quantity):
        item = "" if item is None else item
        quantity = "" if quantity is None else quantity

        # If they were already right just return them
        item_cond = all(not word.isnumeric() for word in item.split())
        quantity_cond = quantity.replace(" ", '').isnumeric()

        if item_cond and quantity_cond:
            return item, quantity

        final_quantity = ""
        for word in (quantity + " " + item).split():
            if word.isnumeric():
                final_quantity = word
                break

        # concatenate, remove numbers and duplicates
        itemquantity = (item + " " + quantity).split()

        duplicated_list = list(
            filter(lambda x: not x.isnumeric(), itemquantity))

        item = " ".join(OrderedDict.fromkeys(duplicated_list).keys())
        return item, final_quantity

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        operation = tracker.get_slot("operation")
        item = tracker.get_slot("item")
        quantity = tracker.get_slot("CARDINAL")
        user = tracker.get_slot("user")

        item, quantity = self.sanitize_itemquantity(item, quantity)

        if quantity == "":
            # when I say "remove item" I want to remove all of them
            quantity = '1' if operation == "add" else "all"

        dispatcher.utter_message(text=f"__{operation}__,{quantity},{item}")

        return [SlotSet("item", None), SlotSet("operation", None), SlotSet("CARDINAL", None)]


class ActionIdentification(Action):
    commands = ["configure", "localsearch"]

    def name(self) -> Text:
        return "action_identification"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        username = tracker.get_slot("user")
        should_know_user = tracker.get_slot("should_know_user")

        dispatcher.utter_message(text=f"__{self.commands[int(should_know_user)]}__,{username}")

        return [SlotSet("should_know_user", None), SlotSet("_user", username)]


class ActionShowItems(Action):
    def name(self) -> Text:
        return "action_show_items"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(text="__show__")
        return []


class ActionStopForm(Action):
    def name(self) -> Text:
        return "action_stop_form"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(response="utter_stop")
        return [SlotSet("item", None), SlotSet("operation", None), SlotSet("CARDINAL", None)]


class ValidateItemForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_item_form"

    def remove_numbers(self, string: str):
        return " ".join([s for s in string.split() if not s.isnumeric()])

    def validate_item(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        quantity = tracker.get_slot("CARDINAL")
        quantity = "" if quantity is None else quantity

        item = slot_value
        if isinstance(item, list):
            item = " ".join(slot_value)
        item = self.remove_numbers(item)

        if len(item) > 0:
            return {"item": item}

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


class ActionGreet(Action):
    def name(self) -> Text:
        return "action_greet"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        greeted = tracker.get_slot("greeted")

        dispatcher.utter_message(
            response="utter_greet" if not greeted else "utter_already_greet")

        return [SlotSet("greeted", True)]


class ActionUser(Action):
    def name(self) -> Text:
        return "action_manage_user"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        current_user = tracker.get_slot("user")
        active_user = tracker.get_slot("_user")
        if not current_user:
            print("ERROR: Unexpected slot value", file=sys.stderr)
            return []
        if not active_user:
            return [*ActionGreet().run(dispatcher, tracker, domain), SlotSet("_user", current_user)]

        if active_user != current_user:
            dispatcher.utter_message(text=f"__help_new_session__")
            return [SlotSet("user", active_user)]
        else:
            intent = tracker.get_intent_of_latest_message()
            if intent == "greet":
                return ActionGreet().run(dispatcher, tracker, domain)
                # return[FollowupAction("action_greet")]
            elif intent == "introduce_myself":
                dispatcher.utter_message(response="utter_pleased")
                dispatcher.utter_message(response="utter_help")
            return []
