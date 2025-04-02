from bank_system.bank import Bank
from bank_system.atm import ATM
from bank_system.account import Account
from bank_system.card import Card
from bank_system.cash import Cash
from bank_system.pin import PIN
from bank_system.check import Check

def atm_operations():
    def select_atm_bank():
        while True:
            input_atm_bank = input("""Select ATM:
            1 - Belarusbank
            2 - Priorbank
            3 - Alfabank
            """)

            try:
                atm_bank = int(input_atm_bank)
                if 1 <= atm_bank <= 3:
                    if atm_bank == 1:
                        return "Belarusbank"
                    elif atm_bank == 2:
                        return "Priorbank"
                    elif atm_bank == 3:
                        return "Alfabank"
                else:
                    print("Error: Please enter a number from 1 to 3.")
            except ValueError:
                print("Error: Please use only numbers.")

    my_bank = Bank(select_atm_bank())
    my_atm = ATM(my_bank.name)
    my_atm.atm_info()
    my_cash = Cash(my_atm.name, my_atm.atm_number)

    def load_info():
        while True:
            user_input = input("Enter your card from 1 to 5: ")
            try:
                number = int(user_input)
                if 1 <= number <= 5:
                    return number
                else:
                    print("Error: enter number from 1 to 5.")
            except ValueError:
                print("Error: please enter a valid integer.")

    my_card = Card()
    filename = f"{load_info()}data.txt"
    my_card.load_information(filename)

    while True:
        to_work = input("To insert card enter 1 (or 0 to exit): ")
        try:
            work = int(to_work)
            if work == 0:
                print("Exiting...")
                break
            elif work == 1:
                print("Card inside ATM")
                my_account = Account(my_card.name, my_card.account_number)
                for i in range(1, 6):
                    filename = f"{i}money.txt"
                    if my_account.money(filename):
                        filename = f"{i}pin.txt"
                        my_pin = PIN(my_account.name, my_account.account_number)
                        my_pin.send_pin(filename)
                        break
                else:
                    print("Account number not found in database.")

                if my_pin.check_pin():
                    while True:
                        input_choose = input("""Chose operation:
                        1-check balance
                        2-withdraw money
                        3-add money
                        4-send money
                        0-exit
                        """)

                        try:
                            choose = int(input_choose)
                            if choose == 0:
                                print("Exiting...")
                                break
                            elif choose == 1:
                                check = Check(
                                    operation_type="Check Balance",
                                    amount=my_account.available_money,
                                    account_number=my_account.account_number,
                                    atm_number=my_cash.atm_number,
                                    bank_name=my_account.name
                                )
                                check.print_check()
                                check.save_check_to_file()
                            elif choose == 2:
                                while True:
                                    input_money = input("Enter sum to withdraw (or 0 to cancel): ")
                                    if input_money == "0":
                                        print("Operation canceled.")
                                        break
                                    try:
                                        money = float(input_money)
                                        if my_cash.cash_withdraw(money):
                                            if my_account.cash_withdraw(money):
                                                check = Check(
                                                    operation_type="Withdraw",
                                                    amount=money,
                                                    account_number=my_account.account_number,
                                                    atm_number=my_cash.atm_number,
                                                    bank_name=my_account.name
                                                )
                                                check.print_check()
                                                check.save_check_to_file()
                                                break
                                    except ValueError:
                                        print("Error: Please enter a valid number for withdrawal.")
                            elif choose == 3:
                                while True:
                                    input_money = input("Enter sum to add (or 0 to cancel): ")
                                    if input_money == "0":
                                        print("Operation canceled.")
                                        break
                                    try:
                                        money = float(input_money)
                                        if my_cash.add_cash(money):
                                            if my_account.add_cash(money):
                                                check = Check(
                                                    operation_type="Add Money",
                                                    amount=money,
                                                    account_number=my_account.account_number,
                                                    atm_number=my_cash.atm_number,
                                                    bank_name=my_account.name
                                                )
                                                check.print_check()
                                                check.save_check_to_file()
                                                break
                                    except ValueError:
                                        print("Error: Please enter a valid number for adding money.")
                            elif choose == 4:
                                while True:
                                    target_account = input("Enter target card number (or 0 to cancel): ").strip()
                                    if target_account == "0":
                                        print("Operation canceled.")
                                        break
                                    input_money = input("Enter sum to send (or 0 to cancel): ").strip()
                                    if input_money == "0":
                                        print("Operation canceled.")
                                        break

                                    cleaned_input = input_money.replace(" ", "")
                                    if cleaned_input.replace(".", "").isdigit() and cleaned_input.count(".") <= 1:
                                        try:
                                            money = float(cleaned_input)
                                            if money <= 0:
                                                print("Error: Please enter a positive amount.")
                                            else:
                                                if my_account.send_money(target_account, money):
                                                    check = Check(
                                                        operation_type="Send Money",
                                                        amount=money,
                                                        account_number=my_account.account_number,
                                                        atm_number=my_cash.atm_number,
                                                        bank_name=my_account.name,
                                                        target_account=target_account
                                                    )
                                                    check.print_check()
                                                    check.save_check_to_file()
                                                    break
                                        except ValueError:
                                            print("Error: Invalid number format. Please enter a valid number (e.g., 200 or 200.50).")
                                    else:
                                        print(f"Error: Invalid input '{input_money}'. Please enter a valid number (e.g., 200 or 200.50).")
                            else:
                                print("Error: Please enter a number from 0 to 4.")
                        except ValueError:
                            print("Error: Invalid input.")
                else:
                    break
            else:
                print("Error: Please enter 0 or 1.")
        except ValueError:
            print("Error: Please enter a valid number.")

    pass