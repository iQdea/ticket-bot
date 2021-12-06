import datetime

from db.fan_id_cardDB import FanIDCardDB
from db.ticketDB import TicketDB


class NotEnoughMoneyError(Exception):
    pass

class TicketAlreadyReserved(Exception):
    pass

class TicketAlreadyReturned(Exception):
    pass

class FanIDCard:

    EXPIRATION_PERIOD_IN_YEARS = 1

    def __init__(self, card_id, username, expiration_date, balance, is_blocked):
        self.card_id = card_id
        self.username = username
        self.balance = balance
        self.expiration_date = FanIDCard.get_expiration_date() if expiration_date is None else expiration_date
        self.is_blocked = is_blocked

    @staticmethod
    def get_expiration_date():
        now = datetime.datetime.now()
        year = str(now.year + FanIDCard.EXPIRATION_PERIOD_IN_YEARS)
        month = str(now.month) if len(str(now.month)) == 2 else "0" + str(now.month)
        day = str(now.day) if len(str(now.day)) == 2 else "0" + str(now.day)
        return year + "-" + month + "-" + day

    def reserve_ticket(self, ticket):
        if self.balance < ticket[2]:
            raise NotEnoughMoneyError("Not enough money to pay for the ticket")
        result = TicketDB.reserve_ticket(ticket[0], self.card_id)
        if result.modified_count == 0:
            raise TicketAlreadyReserved("Ticket already reserved by another person")
        FanIDCardDB.reduce_balance(self.card_id, ticket[2])
        self.balance -= ticket[2]

    def return_ticket(self, ticket):
        result = TicketDB.return_ticket(ticket[0])
        if result.modified_count == 0:
            raise TicketAlreadyReturned("Ticket already returned")
        refund_price = FanIDCard.calculate_refund_price(ticket[2])
        FanIDCardDB.increase_balance(self.card_id, refund_price)
        self.balance += refund_price

    @staticmethod
    def calculate_refund_price(price):
        return 0.9 * price

    def increase_balance(self, value):
        FanIDCardDB.increase_balance(self.card_id, value)
        self.balance += value

    def block(self):
        self.is_blocked = True
        FanIDCardDB.save(self)

    def unblock(self):
        self.is_blocked = False
        FanIDCardDB.save(self)

    def __str__(self):
        return "ID: {}\nBalance: ${}\nExpiration date: {}\nState: {}".format(
            self.card_id, self.balance, self.expiration_date, "blocked" if self.is_blocked else "normal")

    @staticmethod
    def construct(card_id):
        row = FanIDCardDB.get_by_id(card_id)
        return FanIDCard(*row)

    @staticmethod
    def construct_by_username(username):
        row = FanIDCardDB.get_card_by_username(username)
        return FanIDCard(*row)

    @staticmethod
    def create(username):
        new_card_id = int(FanIDCardDB.get_max_card_id()) + 1
        card = FanIDCard(new_card_id, username, FanIDCard.get_expiration_date(), 0, False)
        FanIDCardDB.save(card)
        return card