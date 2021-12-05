import random
import abc


class Person:

    def __init__(self, username, first_name, last_name, age, role):
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        self.age = age
        self.role = role
        self.password = Person.generate_password()

    def __str__(self):
        return "Username: {}\nFirst name: {}\nLast name: {}\nAge: {}\nRole: {}".format(
            self.username, self.first_name, self.last_name, self.age, self.role
        )

    @staticmethod
    def generate_password():
        length = 8
        allowed_characters = []
        for symbol in "abcdefghijklmnopqrstuvwxyz0123456789":
            allowed_characters.append(symbol)
        password = []
        for i in range(length):
            password.append(allowed_characters[random.randint(0, len(allowed_characters) - 1)])
        return "".join(password)

