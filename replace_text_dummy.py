class DummyTextGenerator:
    def __init__(self):
        pass

    def get_greeting(self):
        return "Hello, World!"

    ### BEGIN_REPLACE
    def get_farewell(self):
        return "Goodbye, New World!"

    ### BEGIN_REPLACE

    def get_welcome_message(self):
        return "Welcome to the Dummy Text Generator!"

    def get_parting_message(self):
        return "Thank you for using the Dummy Text Generator! See you soon!"


if __name__ == "__main__":
    dummy = DummyTextGenerator()
    print(dummy.get_greeting())
    print(dummy.get_farewell())
    print(dummy.get_welcome_message())
    print(dummy.get_parting_message())
