import datetime

from db.fan_id_card_db import FanIDCard_db
from db.ticket_db import Ticket_db


class NotEnoughMoneyError(Exception):
    pass


class FanIDCard:

    EXPIRATION_PERIOD_IN_YEARS = 1

    def __init__(self, card_id, username, expiration_date, balance, is_blocked):
        self.id = card_id
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
        if self.balance < ticket.price:
            raise NotEnoughMoneyError("Not enough money to pay for the ticket")
        Ticket_db.reserve_ticket(ticket.id, self.id)
        FanIDCard_db.reduce_balance(self.id, ticket.price)
        self.balance -= ticket.price

    def return_ticket(self, ticket):
        Ticket_db.return_ticket(ticket.id)
        refund_price = FanIDCard.calculate_refund_price(ticket.price)
        FanIDCard_db.increase_balance(self.id, refund_price)
        self.balance += refund_price

    @staticmethod
    def calculate_refund_price(price):
        return 0.9 * price

    def increase_balance(self, value):
        FanIDCard_db.increase_balance(self.id, value)
        self.balance += value

    def block(self):
        self.is_blocked = True
        FanIDCard_db.save(self)

    def unblock(self):
        self.is_blocked = False
        FanIDCard_db.save(self)

    def __str__(self):
        return "ID: {}\nBalance: ${}\nExpiration date: {}\nState: {}".format(
            self.id, self.balance, self.expiration_date, "blocked" if self.is_blocked else "normal")

    @staticmethod
    def construct(card_id):
        row = FanIDCard_db.get_by_id(card_id)
        return FanIDCard(*row)

    @staticmethod
    def construct_by_username(username):
        row = FanIDCard_db.get_card_by_username(username)
        return FanIDCard(*row)

    @staticmethod
    def create(username):
        new_card_id = int(FanIDCard_db.get_max_card_id()) + 1
        card = FanIDCard(new_card_id, username, FanIDCard.get_expiration_date(), 0, False)
        FanIDCard_db.save(card)
        return card