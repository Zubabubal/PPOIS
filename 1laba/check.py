from bank_system.bank import Bank

class Check:
    def __init__(self, operation_type, amount, account_number, atm_number, bank_name, target_account=None):
        self.operation_type = operation_type
        self.amount = amount
        self.account_number = account_number
        self.atm_number = atm_number
        self.bank_name = bank_name
        self.target_account = target_account

    def generate_check(self):
        check = (
            f"----------------------------\n"
            f"Bank: {self.bank_name}\n"
            f"ATM Number: {self.atm_number}\n"
            f"Account Number: {self.account_number}\n"
            f"Operation: {self.operation_type}\n"
        )
        if self.target_account:
            check += f"Target Account: {self.target_account}\n"
        check += (
            f"Amount: {self.amount:.2f} BYN\n"
            f"----------------------------\n"
        )
        return check

    def save_check_to_file(self, filename="check.txt"):
        with open(filename, "w") as file:
            file.write(self.generate_check())
        print(f"Check saved to {filename}")

    def print_check(self):
        print(self.generate_check())