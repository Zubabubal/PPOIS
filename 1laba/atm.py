from bank_system.bank import Bank

class ATM(Bank):
    def __init__(self, name):
        super().__init__(name)
        self.atm_number = None
        self.get_num()

    def get_num(self):
        if self.name == "Belarusbank":
            self.atm_number = 1
        elif self.name == "Alfabank":
            self.atm_number = 2
        elif self.name == "Priorbank":
            self.atm_number = 3
        else:
            return False

    def atm_info(self):
        print("ATM Bank: ", self.name, '\n', "ATM number: ", self.atm_number)