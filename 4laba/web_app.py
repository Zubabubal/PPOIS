from flask import Flask, render_template, request, redirect, url_for, flash
from bank_system.bank import Bank
from bank_system.atm import ATM
from bank_system.card import Card
from bank_system.account import Account
from bank_system.pin import PIN
from bank_system.cash import Cash
from bank_system.check import Check

app = Flask(__name__)
app.secret_key = "your-secret-key"  # Needed for flash messages

# Global state for current session
session_state = {
    "bank": None,
    "atm": None,
    "card": None,
    "account": None,
    "pin": None,
    "cash": None,
    "check": None,
    "pin_attempts": 3,  # Initialize attempts counter
    "card_file": None,  # Store the filename of the card data file
    "money_file": None  # Store the filename of the money file
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/select_bank", methods=["POST"])
def select_bank():
    atm_bank = request.form.get("atm_bank")
    if atm_bank in ["1", "2", "3"]:
        bank_name = {"1": "Belarusbank", "2": "Priorbank", "3": "Alfabank"}[atm_bank]
        session_state["bank"] = Bank(bank_name)
        session_state["atm"] = ATM(bank_name)
        session_state["cash"] = Cash(bank_name, session_state["atm"].atm_number)
        try:
            with open(f"{session_state['atm'].atm_number}atm.txt", "r") as file:
                session_state["cash"].available_cash = float(file.readline().strip())
            flash(f"Selected ATM: {bank_name}, ATM Number: {session_state['atm'].atm_number}")
            return redirect(url_for("insert_card"))
        except FileNotFoundError:
            flash(f"Error: ATM file {session_state['atm'].atm_number}atm.txt not found.")
            return redirect(url_for("index"))
    else:
        flash("Error: Please select a number from 1 to 3.")
        return redirect(url_for("index"))

@app.route("/insert_card")
def insert_card():
    if not session_state["bank"]:
        flash("Please select a bank first.")
        return redirect(url_for("index"))
    return render_template("insert_card.html")

@app.route("/load_card", methods=["POST"])
def load_card():
    card_number = request.form.get("card_number")
    if card_number in ["1", "2", "3", "4", "5"]:
        session_state["card"] = Card()
        filename = f"{card_number}data.txt"
        try:
            session_state["card"].load_information(filename)
            session_state["card_file"] = filename
            session_state["account"] = Account(session_state["card"].name, session_state["card"].account_number)
            # Load money from file
            for i in range(1, 6):
                money_file = f"{i}money.txt"
                if session_state["account"].money(money_file):
                    session_state["money_file"] = money_file
                    break
            else:
                flash("Account number not found in money files.")
                return redirect(url_for("insert_card"))
            # Load PIN from file
            session_state["pin"] = PIN(session_state["card"].name, session_state["card"].account_number)
            pin_file = f"{card_number}pin.txt"
            if session_state["pin"].send_pin(pin_file):
                session_state["pin_attempts"] = 3  # Reset attempts to 3 when card is inserted
                flash("Card inserted successfully.")
                return redirect(url_for("enter_pin"))
            else:
                flash("Error: PIN file not found.")
                return redirect(url_for("insert_card"))
        except FileNotFoundError:
            flash(f"Error: File {filename} not found.")
            return redirect(url_for("insert_card"))
    else:
        flash("Error: Enter a number from 1 to 5.")
        return redirect(url_for("insert_card"))

@app.route("/enter_pin")
def enter_pin():
    if not session_state["card"]:
        flash("Please insert a card first.")
        return redirect(url_for("insert_card"))
    return render_template("enter_pin.html")

@app.route("/check_pin", methods=["POST"])
def check_pin():
    if not session_state["pin"]:
        flash("Please insert a card first.")
        return redirect(url_for("insert_card"))
    check_pin = request.form.get("pin")
    try:
        in_pin = int(check_pin)
        if in_pin == int(session_state["pin"].pin_code):
            flash("PIN accepted.")
            session_state["pin_attempts"] = 3  # Reset attempts on success
            return redirect(url_for("operations"))
        else:
            session_state["pin_attempts"] -= 1
            if session_state["pin_attempts"] > 0:
                flash(f"Incorrect PIN, try again. Attempts left: {session_state['pin_attempts']}")
                return redirect(url_for("enter_pin"))
            else:
                flash("Too many incorrect attempts. Exiting...")
                session_state.clear()
                session_state["pin_attempts"] = 3  # Reset for next session
                return redirect(url_for("index"))
    except ValueError:
        session_state["pin_attempts"] -= 1
        if session_state["pin_attempts"] > 0:
            flash(f"Error: Please enter a valid integer. Attempts left: {session_state['pin_attempts']}")
            return redirect(url_for("enter_pin"))
        else:
            flash("Too many incorrect attempts. Exiting...")
            session_state.clear()
            session_state["pin_attempts"] = 3  # Reset for next session
            return redirect(url_for("index"))

@app.route("/operations")
def operations():
    if not session_state["pin"] or not session_state["account"] or not session_state["atm"] or not session_state["cash"]:
        flash("Please complete card and PIN steps first.")
        return redirect(url_for("insert_card"))
    try:
        # Ensure all attributes are accessible
        bank_name = session_state["account"].name
        atm_number = session_state["atm"].atm_number
        return render_template("operations.html", account=session_state["account"], atm=session_state["atm"])
    except AttributeError as e:
        flash("Error: Session data is incomplete or corrupted. Please start over.")
        session_state.clear()
        session_state["pin_attempts"] = 3
        return redirect(url_for("index"))

@app.route("/check_balance", methods=["POST"])
def check_balance():
    if not session_state["account"]:
        flash("Please complete card and PIN steps first.")
        return redirect(url_for("insert_card"))
    session_state["check"] = Check(
        operation_type="Check Balance",
        amount=session_state["account"].available_money,
        account_number=session_state["account"].account_number,
        atm_number=session_state["cash"].atm_number,
        bank_name=session_state["account"].name
    )
    check_text = session_state["check"].generate_check()
    flash("Balance checked successfully.")
    return render_template("check.html", check=check_text)

@app.route("/withdraw", methods=["POST"])
def withdraw():
    if not session_state["account"] or not session_state["cash"]:
        flash("Please complete card and PIN steps first.")
        return redirect(url_for("insert_card"))
    input_money = request.form.get("amount")
    try:
        money = float(input_money)
        if session_state["cash"].cash_withdraw(money):
            if session_state["account"].cash_withdraw(money):
                # Update money file
                session_state["account"].update_money_file(session_state["account"].available_money, session_state["money_file"])
                # Update ATM file
                with open(f"{session_state['cash'].atm_number}atm.txt", "w") as file:
                    file.write(f"{session_state['cash'].available_cash:.2f}\n")
                session_state["check"] = Check(
                    operation_type="Withdraw",
                    amount=money,
                    account_number=session_state["account"].account_number,
                    atm_number=session_state["cash"].atm_number,
                    bank_name=session_state["account"].name
                )
                check_text = session_state["check"].generate_check()
                flash(f"Successfully withdrew {money:.2f} BYN.")
                return render_template("check.html", check=check_text)
            else:
                flash("Account withdrawal failed.")
        else:
            flash("ATM withdrawal failed.")
    except ValueError:
        flash("Error: Please enter a valid number for withdrawal.")
    return redirect(url_for("operations"))

@app.route("/add_money", methods=["POST"])
def add_money():
    if not session_state["account"] or not session_state["cash"]:
        flash("Please complete card and PIN steps first.")
        return redirect(url_for("insert_card"))
    input_money = request.form.get("amount")
    try:
        money = float(input_money)
        if session_state["cash"].add_cash(money):
            if session_state["account"].add_cash(money):
                # Update money file
                session_state["account"].update_money_file(session_state["account"].available_money, session_state["money_file"])
                # Update ATM file
                with open(f"{session_state['cash'].atm_number}atm.txt", "w") as file:
                    file.write(f"{session_state['cash'].available_cash:.2f}\n")
                session_state["check"] = Check(
                    operation_type="Add Money",
                    amount=money,
                    account_number=session_state["account"].account_number,
                    atm_number=session_state["cash"].atm_number,
                    bank_name=session_state["account"].name
                )
                check_text = session_state["check"].generate_check()
                flash(f"Successfully added {money:.2f} BYN.")
                return render_template("check.html", check=check_text)
            else:
                flash("Account addition failed.")
        else:
            flash("ATM addition failed.")
    except ValueError:
        flash("Error: Please enter a valid number for adding money.")
    return redirect(url_for("operations"))

@app.route("/send_money", methods=["POST"])
def send_money():
    if not session_state["account"]:
        flash("Please complete card and PIN steps first.")
        return redirect(url_for("insert_card"))
    target_account = request.form.get("target_account").strip()
    input_money = request.form.get("amount").strip()
    try:
        money = float(input_money)
        if money <= 0:
            flash("Error: Please enter a positive amount.")
        else:
            if session_state["account"].send_money(target_account, money):
                session_state["check"] = Check(
                    operation_type="Send Money",
                    amount=money,
                    account_number=session_state["account"].account_number,
                    atm_number=session_state["cash"].atm_number,
                    bank_name=session_state["account"].name,
                    target_account=target_account
                )
                check_text = session_state["check"].generate_check()
                flash(f"Successfully sent {money:.2f} BYN to card {target_account}.")
                return render_template("check.html", check=check_text)
            else:
                flash("Transfer failed.")
    except ValueError:
        flash("Error: Please enter a valid number for sending money.")
    return redirect(url_for("operations"))

@app.route("/exit")
def exit():
    session_state.clear()
    session_state["pin_attempts"] = 3
    flash("Exiting... Session reset.")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)