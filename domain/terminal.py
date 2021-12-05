from db.personDB import PersonDB
from domain.fan_id_card import FanIDCard
from domain.person import Person


class InvalidAgeError(Exception):
    pass


class UserAlreadyExistsError(Exception):
    pass


class IncorrectInputFormat(Exception):
    pass


class Terminal(Person):

    MAX_LENGTH = 20

    def __init__(self, username, first_name, last_name, age, password):
        super().__init__(username, first_name, last_name, age, password, role="terminal")

    def is_format_incorrect(self, customer):
        return len(customer.username) > self.MAX_LENGTH or len(customer.first_name) > self.MAX_LENGTH or len(customer.last_name) > self.MAX_LENGTH or customer.age > 99

    def register(self, customer):
        if self.is_format_incorrect(customer):
            raise IncorrectInputFormat("The input does not correspond to system format. "
                                       "The age must be in range from 12 to 99 and other fields must not exceed the length of {} symbols".format(self.MAX_LENGTH))
        if PersonDB.does_exist(customer.username):
            raise UserAlreadyExistsError("User already exists in the system")
        PersonDB.register(customer, self.username)
        customer.fan_id_card = self.create_fan_id(customer.username)

    def create_fan_id(self, username):
        return FanIDCard.create(username)

    @staticmethod
    def block_fan_id_card(customer):
        customer.fan_id_card.block()

    @staticmethod
    def unblock_fan_id_card(customer):
        customer.fan_id_card.unblock()

    @staticmethod
    def construct(username):
        row = PersonDB.get_by_id(username)
        return Terminal(row[0], row[1], row[2], row[3], row[5])