from bank_system.bank import Bank

class Cash:
    def __init__(self, name, atm_number):
        self.name = name
        self.atm_number = atm_number
        self.available_cash = None
        self.atm_money()

    def atm_money(self):
        try:
            with open(f"{self.atm_number}atm.txt", 'r') as file:
                self.available_cash = float(file.readline().strip())
        except FileNotFoundError:
            print("Error.")

    def cash_withdraw(self, money):
        if self.available_cash >= money > 0 and money % 5 == 0:
            self.available_cash -= money
            with open(f"{self.atm_number}atm.txt", 'w') as file:
                file.write(f"{self.available_cash:.2f}\n")
            print(f"You withdrew {money} BYN")
            return True
        elif money % 5 != 0:
            print("Enter correct sum")
            return False
        else:
            print("Not enough money in ATM")
            return False

    def add_cash(self, money):
        if money % 5 == 0 and money>0:
            self.available_cash += money
            with open(f"{self.atm_number}atm.txt", 'w') as file:
                file.write(f"{self.available_cash:.2f}\n")
            print(f"You added on your account {money} BYN")
            return True
        else:
            print("Enter correct sum")
            return False