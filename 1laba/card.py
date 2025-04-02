import re
from bank_system.bank import Bank

class Card:
    def __init__(self):
        self.name = None
        self.account_number = None
        self.card_number = None

    def load_information(self, filename):
        with open(filename, 'r') as file:
            self.account_number = file.readline().strip()
            self.card_number = file.readline().strip()

        self.identify_bank()

    def identify_bank(self):
        cleaned_card_number = self.card_number.replace(" ", "")
        cleaned_prefix = self.account_number.replace(" ", "")[:8]

        if re.match(r'BY[0-9][0-9]AKBB', cleaned_prefix):
            self.name = "Belarusbank"
        elif re.match(r'BY[0-9][0-9]ALFB', cleaned_prefix):
            self.name = "Alphabank"
        elif re.match(r'BY[0-9][0-9]PRIB', cleaned_prefix):
            self.name = "Priorbank"
        else:
            self.name = "Unknown bank"