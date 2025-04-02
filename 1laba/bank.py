class Bank:
    def __init__(self, name):
        self.name = name

    def get_information(self):
        print("Bank name: " + self.name)