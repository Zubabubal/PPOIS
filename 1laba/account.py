import re
from bank_system.bank import Bank

class Account(Bank):
    def __init__(self, name, account_number):
        super().__init__(name)
        self.account_number = account_number
        self.available_money = None

    def money(self, filename):
        try:
            with open(filename, "r") as file:
                loaded_num = file.readline().strip()
                loaded_money = file.readline().strip()
            if loaded_num == self.account_number:
                self.available_money = float(loaded_money)
                return True
        except FileNotFoundError:
            print(f"File {filename} not found.")
        return False

    def update_money_file(self, amount, filename=None):
        if filename:
            try:
                with open(filename, "r") as file:
                    loaded_num = file.readline().strip()
                if loaded_num == self.account_number:
                    with open(filename, "w") as file:
                        file.write(self.account_number + "\n")
                        file.write(f"{amount:.2f}\n")
                    return True
            except FileNotFoundError:
                return False
        else:
            for i in range(1, 6):
                try:
                    with open(f"{i}money.txt", "r") as file:
                        loaded_num = file.readline().strip()
                    if loaded_num == self.account_number:
                        with open(f"{i}money.txt", "w") as file:
                            file.write(self.account_number + "\n")
                            file.write(f"{amount:.2f}\n")
                        return True
                except FileNotFoundError:
                    continue
            print("No matching money file found.")
            return False

    def cash_withdraw(self, money):
        if self.available_money is None:
            print("Money not loaded.")
            return False
        if self.available_money < money:
            print("Not enough money on the account.")
            return False
        self.available_money -= money
        return self.update_money_file(self.available_money)

    def add_cash(self, money):
        if self.available_money is None:
            print("Money not loaded.")
            return False
        self.available_money += money
        return self.update_money_file(self.available_money)

    def send_money(self, to_send_card_number, amount):
        if self.available_money < amount:
            print("Not enough money on the account.")
            return False

        for i in range(1, 6):
            try:
                with open(f"{i}data.txt", "r") as file:
                    target_account_number = file.readline().strip()
                    target_card_number = file.readline().strip()

                    cleaned_target_card = re.sub(r'\s+', '', target_card_number)
                    cleaned_input_card = re.sub(r'\s+', '', to_send_card_number)

                    if cleaned_input_card == cleaned_target_card:
                        self.available_money -= amount
                        self.update_money_file(self.available_money)

                        for j in range(1, 6):
                            try:
                                with open(f"{j}money.txt", "r") as target_file:
                                    loaded_num = target_file.readline().strip()
                                    if loaded_num == target_account_number:
                                        target_money = float(target_file.readline().strip())
                                        target_money += amount
                                        with open(f"{j}money.txt", "w") as target_file:
                                            target_file.write(target_account_number + "\n")
                                            target_file.write(f"{target_money:.2f}\n")
                                        break
                            except FileNotFoundError:
                                continue

                        print(f"Successfully sent {amount:.2f} BYN to account {target_account_number}.")
                        return True
            except FileNotFoundError:
                continue

        print("Target card number not found.")
        return False