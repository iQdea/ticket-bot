from db.fan_id_card_db import FanIDCard_db
from db.matches_db import Match_db
from db.person_db import Person_db
from db.ticket_db import Ticket_db
from domain.person import Person
from domain.seat import Seat
from domain.ticket import SingleTicket


class Organizer(Person):

    def __init__(self, username, first_name, last_name, age):
        super().__init__(username, first_name, last_name, age, "organizer")

    @staticmethod
    def add_match(match):
        new_match_id = Match_db.add_match(match)
        match.id = new_match_id
        seats = Seat.get_seats()
        for seat in seats:
            price = 20 * seat.block + 5 * seat.row + 3 * seat.place + 0.99
            ticket = SingleTicket(None, None, price, match, seat)
            Ticket_db.add_ticket(ticket)

    @staticmethod
    def update_match(match):
        Match_db.update_match(match)

    @staticmethod
    def delete_match(match_id):
        Ticket_db.delete_tickets_by_match_id(match_id)
        Match_db.delete_match(match_id)

    @staticmethod
    def cancel_match(match_id):
        paid_money = Ticket_db.get_paid_money(match_id)
        for card_id, price in paid_money:
            if card_id is not None:
                FanIDCard_db.increase_balance(card_id, price)
        Ticket_db.delete_tickets_by_match_id(match_id)
        Match_db.delete_match(match_id)

    @staticmethod
    def construct(username):
        row = Person_db.get_by_id(username)
        return Organizer(row[0], row[2], row[3], row[5])