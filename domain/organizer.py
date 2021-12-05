from db.fan_id_cardDB import FanIDCardDB
from db.matchesDB import MatchDB
from db.personDB import PersonDB
from db.ticketDB import TicketDB
from domain.person import Person
from domain.seat import Seat
from domain.ticket import SingleTicket


class Organizer(Person):

    def __init__(self, username, first_name, last_name, age):
        super().__init__(username, first_name, last_name, age, "organizer")

    @staticmethod
    def add_match(match):
        new_match_id = MatchDB.add_match(match)
        match.id = new_match_id
        seats = Seat.get_seats()
        for seat in seats:
            price = 20 * seat.block + 5 * seat.row + 3 * seat.place + 0.99
            ticket = SingleTicket(None, None, price, match, seat)
            TicketDB.add_ticket(ticket)

    @staticmethod
    def update_match(match):
        MatchDB.update_match(match)

    @staticmethod
    def delete_match(match_id):
        TicketDB.delete_tickets_by_match_id(match_id)
        MatchDB.delete_match(match_id)

    @staticmethod
    def cancel_match(match_id):
        paid_money = TicketDB.get_paid_money(match_id)
        for card_id, price in paid_money:
            if card_id is not None:
                FanIDCardDB.increase_balance(card_id, price)
        TicketDB.delete_tickets_by_match_id(match_id)
        MatchDB.delete_match(match_id)

    @staticmethod
    def construct(username):
        row = PersonDB.get_by_id(username)
        return Organizer(row[0], row[2], row[3], row[5])