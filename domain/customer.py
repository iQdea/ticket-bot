from entity.personEntity import PersonEntity
from domain.fan_id_card import FanIDCard
from domain.person import Person


class TicketDoesNotBelongToCustomerError(Exception):
    pass


class CustomerDoesNotExistError(Exception):
    pass


class Customer(Person):

    def __init__(self, username, first_name, last_name, age, role, password, creator, fan_id_card):
        super().__init__(username, first_name, last_name, age, password, role)
        self.fan_id_card = fan_id_card

    def buy_ticket(self, ticket):
        self.fan_id_card.reserve_ticket(ticket)

    def return_ticket(self, ticket):
        if ticket[1] is None or self.fan_id_card.card_id != ticket[1]:
            raise TicketDoesNotBelongToCustomerError()
        self.fan_id_card.return_ticket(ticket)

    def increase_balance(self, value):
        self.fan_id_card.increase_balance(value)

    def is_blocked(self):
        return self.fan_id_card.is_blocked

    def __str__(self):
        result = super(Customer, self).__str__()
        result += "\n----- Fan ID card -----\n"
        result += str(self.fan_id_card)
        return result

    def restore_password(self):
        return self.password
        
    @staticmethod
    def construct(username):
        if not PersonEntity.does_exist(username) or PersonEntity.get_role_by_username(username) != "customer":
            raise CustomerDoesNotExistError()
        row = PersonEntity.get_by_id(username)
        card = FanIDCard.construct_by_username(username)
        return Customer(row[0], row[1], row[2], row[3], row[4], row[5], row[6], card)
    