from typing import Text, List, Any, Dict

from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import AllSlotsReset
from rasa_sdk import Action, Tracker
import datetime
import json
import hashlib
import re

def clean_name(name):
    return "".join([c for c in name if c.isalpha()])

def generate_application_number(city, loan_name, first_name, last_name, mobile_no, pancard_no):
    input_string = f"{city}{loan_name}{first_name}{last_name}{mobile_no}{pancard_no}"
    hashed_input = hashlib.sha256(input_string.encode()).hexdigest()
    return hashed_input[:16]

class ValidateNameForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_name_form"

    def validate_loan_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `loan_name` value."""

        # If the name is super short, it might be wrong.
        name = clean_name(slot_value)
        types_of_loans = ['personal' , 'gold' , 'auto','business' , 'student','home']
        for i in types_of_loans:
            if i in name.lower():
                name = i 
        if len(name) == 0:
            dispatcher.utter_message(text="That must've been a typo.")
            return {"loan_name": None}
        return {"loan_name": name}

    def validate_first_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `first_name` value."""

        # If the name is super short, it might be wrong.
        name = clean_name(slot_value)
        if len(name) == 0:
            dispatcher.utter_message(text="That must've been a typo.")
            return {"first_name": None}
        return {"first_name": name}

    def validate_last_name(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `last_name` value."""

        # If the name is super short, it might be wrong.
        name = clean_name(slot_value)
        if len(name) == 0:
            dispatcher.utter_message(text="That must've been a typo.")
            return {"last_name": None}
        
        first_name = tracker.get_slot("first_name")
        if len(first_name) + len(name) < 3:
            dispatcher.utter_message(text="That's a very short name. We fear a typo. Restarting!")
            return {"first_name": None, "last_name": None}
        return {"last_name": name}


    def validate_mobile_no(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `mobile_no` value."""

        mobile_no = slot_value
        pattern = r"\b\d{10}\b"
        matches = re.findall(pattern, mobile_no)
        if len(matches) > 0:
            return {"mobile_no": matches[0]}
        else:
            dispatcher.utter_message(text="That must've been a typo.")
            return {"mobile_no": None}


    def validate_pancard_no(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `pancard_no` value."""

        pancard_no = slot_value
        pattern = r"[A-Z]{5}[0-9]{4}[A-Z]{1}"
        matches = re.findall(pattern, pancard_no)
        if len(matches) > 0:
            return {"pancard_no": matches[0]}
        else:
            dispatcher.utter_message(text="That must've been a typo.")
            return {"pancard_no": None}

    def validate_city(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `city` value."""

        city = slot_value

        return {"city": city}


class ActionFromGen(Action):
    def name(self) -> Text:
        return "action_from_gen"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        city = tracker.get_slot("city")
        loan_name = tracker.get_slot("loan_name")
        first_name = tracker.get_slot("first_name")
        last_name = tracker.get_slot("last_name")
        mobile_no = tracker.get_slot("mobile_no")
        pancard_no = tracker.get_slot("pancard_no")
        application_number = generate_application_number(city, loan_name, first_name, last_name, mobile_no, pancard_no)

        data = {"application_number":application_number,
                "loan_requirement": loan_name,
                "first_name": first_name,
                "last_name": last_name,
                "mobile_no": mobile_no,
                "city": city,
                "pancard_no": pancard_no}

        now = datetime.datetime.now()
        data["date/time"] = now.isoformat()
        with open("Applications.txt", "a") as outfile:
            json.dump(data, outfile , indent=4)
            outfile.write("\n")
        return []


class ActionResetAllSlots(Action):
    def name(self) -> Text:
        return "action_reset_all_slots"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        return [AllSlotsReset()]



class ActionPrintForm(Action):
    def name(self) -> Text:
        return "action_print_form"


    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:




        city = tracker.get_slot("city")
        loan_name = tracker.get_slot("loan_name")
        first_name = tracker.get_slot("first_name")
        last_name = tracker.get_slot("last_name")
        mobile_no = tracker.get_slot("mobile_no")
        pancard_no = tracker.get_slot("pancard_no")
        application_number = generate_application_number(city, loan_name, first_name, last_name, mobile_no, pancard_no)

        dispatcher.utter_message(text=f"Your Application Number is : {application_number} , loan requirement :{loan_name} , city : {city}  , first name : {first_name} , last name : {last_name} , mobile no is : {mobile_no} , pancard no is :{pancard_no} ")


        return []