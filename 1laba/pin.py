from bank_system.bank import Bank

class PIN:
    def __init__(self, name, account_number):
        self.name = name
        self.account_number = account_number
        self.pin_code = None

    def send_pin(self, filename):
        try:
            with open(filename, "r") as file:
                loaded_account_num = file.readline().strip()
                loaded_pin = file.readline().strip()
            if loaded_account_num == self.account_number:
                self.pin_code = loaded_pin
                return True
        except FileNotFoundError:
            print("Pin error.")

    def check_pin(self):
        attempts = 0
        while attempts < 3:
            check_pin = input("Enter your PIN code: ")
            try:
                in_pin = int(check_pin)
                if in_pin == int(self.pin_code):
                    print("PIN accepted.")
                    return True
                else:
                    attempts += 1
                    print(f"Incorrect PIN, try again. Attempts left: {3 - attempts}")
            except ValueError:
                print("Error: Please enter a valid integer.")

        if attempts == 3:
            print("Too many incorrect attempts. Exiting...")
            return False