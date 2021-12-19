import telebot
import datetime
from entity.mongo import Mongo
from entity.matchesEntity import MatchEntity, MatchExpired, MatchDelitionRestricted
from entity.personEntity import PersonEntity
from entity.ticketEntity import TicketEntity
from domain.terminal import Terminal, UserAlreadyExistsError, IncorrectInputFormat
from domain.customer import Customer, TicketDoesNotBelongToCustomerError, CustomerDoesNotExistError
from domain.fan_id_card import FanIDCard, NotEnoughMoneyError, TicketAlreadyBlocked, TicketAlreadyUnblocked
from domain.match import Match, MatchDoesNotExistError
from domain.organizer import Organizer
from domain.seat import Seat
from domain.ticket import SingleTicket, TicketDoesNotExistError

token = "2130797376:AAENz9nRcdRj0GiHnnzFOOQvY8XSpvTEzfs"
bot = telebot.TeleBot(token)

class CurrentUser:
    def __init__(self):
        self.authenticated = False
        self.username = self.password = self.operation = self.role = self.person = None

class NewCustomer:
    def __init__(self):
        self.username = self.age = self.first_name = self.last_name = None

class NewMatch:
    def __init__(self):
        self.host_team = self.guest_team = self.date = self.match_type = None

user = CurrentUser()
new_customer = None
new_match = None
match = None

def send(message, text, next_handler=None):
    sent = bot.send_message(message.chat.id, text)
    if next_handler is not None:
        bot.register_next_step_handler(sent, next_handler)


@bot.message_handler(commands=["start"], regexp="start")
def show(message):
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    if not user.authenticated:
        user_markup.row("Show info")
        user_markup.row("Register new customer")
        user_markup.row("Login")
        user_markup.row("Show matches")
    else:
        user_markup.row("Show info")
        if user.role == "customer":
            user_markup.row("Show balance")
            user_markup.row("Show tickets")
            user_markup.row("Add balance")
            user_markup.row("Show matches")
            user_markup.row("Buy ticket", "Return ticket")
        elif user.role == "terminal":
            user_markup.row("Reset System")
            user_markup.row("Show Users")
            user_markup.row("Register new organizer")
            user_markup.row("Block Fan ID Card", "Unblock Fan ID Card")
        elif user.role == "organizer":
            user_markup.row("Show matches")
            user_markup.row("Add match", "Update match")
            user_markup.row("Delete match", "Cancel match")
        user_markup.row("My credentials")
        user_markup.row("Logout")
        user_markup.row("Confirm logout")
        user_markup.row("Cancel logout")
    bot.send_message(message.chat.id, "Choose command", reply_markup=user_markup)

@bot.message_handler(regexp="Show info")
def show_info(message):
    if not user.authenticated:
        bot.send_message(message.chat.id, "Hello, friend! I am Football-Seller-bot.\n\n" 
        + "Press <<Show info>> to get this message.\n\n"
        + "Press <<Login>> if you have account or <<Register new customer>> if you haven't yet.\n\n"
        + "Also you can press <<Show matches>> to see available matches.\n\n"
        + "Press any botton to get to user menu page after you succesfully logged in.")
    else:
        if user.role == "customer":
            bot.send_message(message.chat.id, "Press <<Show info>> to get this message.\n\n"
            + "Press <<Show balance>> to see your balance.\n\n"
            + "Press <<Show tickets>> to see your tickets.\n\n" 
            + "Press <<Add balance>> to send money to your fan_id_card.\n\n"
            + "Press <<Show matches>> to see available matches.\n\n"
            + "Press <<Buy ticket>> to purchase ticket.\n\n"
            + "Press <<Return tciket>> to return ticket and get your money back. Warning!!! You will get 90 percents of ticket price.\n\n"
            + "Press <<My credentials>> to see your account information.\n\n"
            + "Press <<Logout>> to be logged out.\n\n"
            + "Press <<Confirm logout>> and any botton to get to start page after you press <<Logout>>.")
        elif user.role == "terminal":
            bot.send_message(message.chat.id, "Press <<Show info>> to get this message.\n\n"
            + "Press <<Reset System>> if you really want to clear System Database from all documents. At least, there will be terminal user.\n\n"
            + "Press <<Show Users>> to get all user's usernames and roles.\n\n"
            + "Press <<Register new organizer>> to add new organizer to system.\n\n"
            + "Press <<Block Fan ID Card>> to block someone.\n\n"
            + "Press <<Unblock Fan ID Card>> to unblock user who has been blocket yet.\n\n"
            + "Press <<My credentials>> to see your account information.\n\n"
            + "Press <<Logout>> to be logged out.\n\n"
            + "Press <<Confirm logout>> and any botton to get to start page after you press <<Logout>>.")
        else:
            bot.send_message(message.chat.id, "Press <<Add Match>> to create new match in system.\n\n" 
            + "Press <<Update Match>> to update info about match in system.\n\n"
            + "Press <<Delete Match>> to remove match from system after canceling.\n\n"
            + "Press <<Cancel Match>> to cancel match in system.\n\n"
            + "Press <<My credentials>> to see your account information.\n\n"
            + "Press <<Logout>> to be logged out.\n\n"
            + "Press <<Confirm logout>> and any botton to get to start page after you press <<Logout>>.")

@bot.message_handler(regexp="Reset System")
def full_reset(message):
    if user.role == "terminal":
        send(message, "Enter password to confirm reset", enter_password_to_confirm)
def enter_password_to_confirm(message):
    passwd = message.text
    if passwd == user.password:
        Mongo.reset()
        send(message, "Database was reseted")


@bot.message_handler(regexp="Show matches")
def show_matches(message):
    matches = get_matches()
    send(message, matches if matches != 0 else "There are no available matches")

def get_matches():
    result = MatchEntity.get_matches()
    if not result == 0:
        matches = ""
        for row in result:
            matches += str(Match(*row)) + "\n\n"
        return matches
    else:
        return 0

@bot.message_handler(regexp="Show balance")
def show_money(message):
    send(message, "Balance: {}$".format(user.person.fan_id_card.balance))

@bot.message_handler(regexp="Show Users")
def show_users(message):
    if user.role == "terminal":
        users = get_users()
        send(message, users if users != 0 else "There are no users")


def get_users():
    result = PersonEntity.get_users_info()
    if not result == 0:
        users = ""
        for row in result:
            users += "Username: {}\nRole: {}\n\n".format(
                row[0], row[-1]
            )
        return users
    else:
        return 0


@bot.message_handler(regexp="My credentials")
def show_credentials(message):
    send(message, str(user.person))


@bot.message_handler(regexp="Logout")
def logout(message):
    send(message, "You sure to be logged out? If yes, press <<Confirm logout>>, else press <<Cancel logout>>", answer)

def answer(message):
    if message.text == "Confirm logout":
        user.authenticated = False
        user.role = ""
        send(message, "You have been logged out, press any button to continue", show)
    elif message.text == "Cancel logout":
        send(message, "Logout stopped")

@bot.message_handler(regexp="Login")
def login(message):
    if not user.authenticated:
        send(message, "Enter your username", enter_username)

def enter_username(message):
    username = message.text
    if PersonEntity.does_exist(username):
        user.username = username
        send(message, "Enter your password", enter_password)
    else:
        send(message, "The entered username does not exist. Check if you have all correct credentials to login")

def enter_password(message):
    password = message.text
    if PersonEntity.is_password_correct(user.username, password):
        user.password = password
        user.authenticated = True
        user.role = PersonEntity.get_role_by_username(user.username)
        print(user.username, user.password, user.role)
        if user.role == "customer":
            try:
                user.person = Customer.construct(user.username)
                send(message, "You have been successfully logged in, press any button to continue", show)
            except:
                send(message, "User wasn't found. Check if you have your fun_id_card")
        elif user.role == "terminal":
            try:
                user.person = Terminal.construct(user.username)
                send(message, "You have been successfully logged in, press any button to continue", show)
            except:
                send(message, "User wasn't found. Check if you have all credentials to login")
        elif user.role == "organizer":
            try:
                user.person = Organizer.construct(user.username)
                send(message, "You have been successfully logged in, press any button to continue", show)
            except:
                send(message, "User wasn't found. Check if you have all credentials to login")
    else:
        send(message, "The entered password is wrong. Check if you have all correct credentials to login")

@bot.message_handler(regexp="Show tickets")
def show_tickets(message):
    if user.role == "customer":
        tickets = get_tickets()
        if not tickets == 0:
            send(message,tickets) 
        else:
            send(message,"You do not have any tickets")


def get_tickets():
    card_id = user.person.fan_id_card
    result = TicketEntity.get_tickets_id_by_card_id(card_id.card_id)
    if not result == 0:
        tickets = ""
        for row in result:
            ticket_id = row[0]
            match_id = row[1]
            tickets += str(SingleTicket.construct(ticket_id, match_id)) + "\n\n"
        return tickets
    else:
        return 0


@bot.message_handler(regexp="Add balance")
def add_balance(message):
    if user.role == "customer":
        if user.person.is_blocked():
            send(message, "Your Fan ID Card is blocked")
        else:
            send(message, "Your current balance: ${}\nEnter the value you would like to increase your balance".format(round(user.person.fan_id_card.balance, 2)), enter_value)


def enter_value(message):
    try:
        value = round(float(message.text), 2)
        if value <= 0:
            send(message, "The value in $ can only be positive. Please enter the value again", enter_value)
            return
        user.person.increase_balance(value)
        send(message, "Your balance was increased and now equals ${}".format(round(user.person.fan_id_card.balance, 2)))
    except ValueError:
        send(message, "Wrong input format. You should enter the value in $. Please enter the value again", enter_value)

@bot.message_handler(regexp="Buy ticket")
def buy_ticket(message):
    if user.role == "customer":
        if user.person.is_blocked():
            send(message, "Your Fan ID Card is blocked")
        else:
            matches = get_matches()
            if matches == 0:
                send(message, "There are no available matches")
            else:
                tickets_exist = MatchEntity.get_tickets_cnt()
                if tickets_exist > 0:
                    send(message, "Enter match ID you would like to attend")
                    send(message, matches, enter_match_id_to_buy_ticket)
                else:
                    send(message, "There are no tickets at all. Come back later")
                    return



def enter_match_id_to_buy_ticket(message):
    global match_id
    try:
        match_id = int(message.text)
        if not MatchEntity.does_exist(match_id):
            send(message, "The entered match id does not exist. Please enter the match id again", enter_match_id_to_buy_ticket)
            return
        if MatchEntity.did_expired(match_id):
            raise MatchExpired()
        try:
            available_seats = get_available_seats(match_id)
            send(message, "Choose an available seat for this match. Your balance: ${}".format(round(user.person.fan_id_card.balance, 2)))
            send(message, available_seats, choose_seat)
        except:
            send(message, "There are no available seats for this match. Please choose another match", enter_match_id_to_buy_ticket)
            return
    except ValueError:
        send(message, "Match ID must be an integer. Please enter the match id again", enter_match_id_to_buy_ticket)
    except MatchExpired:
        send(message, "The entered match is expired. You can't buy ticket for it")
def choose_seat(message):
    try:
        ticket_id = int(message.text)
        if not TicketEntity.does_exist(ticket_id):
            send(message, "The entered ID does not exist. Please enter the ID again", choose_seat)
            return
        ticket = TicketEntity.get_by_id(ticket_id, match_id)
        user.person.buy_ticket(ticket)
        send(message, "The seat and ticket were successfully reserved. Balance: ${}".format(round(user.person.fan_id_card.balance, 2)))
    except ValueError:
        send(message, "You should enter an ID for choosing a seat. Please enter the ID again", choose_seat)
    except NotEnoughMoneyError as error:
        send(message, str(error))
        return



def get_available_seats(match_id):
    result = TicketEntity.get_available_tickets_id_and_seats_and_price(match_id)
    ans = []
    tickets_id_and_seats_and_prices = ""
    for row in result:
        tickets_id_and_seats_and_prices += str(row[0]) + ": " + str(Seat(row[2], row[3], row[4])) + ". Price: ${}\n".format(row[1])
        ans.append([row[0], row[2], row[3], row[4], row[1]])
    return tickets_id_and_seats_and_prices
    
@bot.message_handler(regexp="Return ticket")
def return_ticket(message):
    if user.role == "customer":
        if user.person.is_blocked():
            send(message, "Your Fan ID Card is blocked")
        else:
            tickets = get_tickets()
            if tickets == 0:
                send(message, "You do not have any tickets")
            else:
                send(message, "Enter ticket ID you would like to return")
                send(message, tickets, enter_ticket_id_to_return)


def enter_ticket_id_to_return(message):
    try:
        card_id = user.person.fan_id_card
        result = TicketEntity.get_tickets_id_by_card_id(card_id.card_id)
        ticket_id = int(message.text)
        cnt = 0
        for row in result:
            if row[0] == ticket_id:
                cnt += 1
        for row in result:
            if cnt > 1:
                send(message, "There are lots of matches with same ID")
                return
            ticket_id = row[0]
            match_id = row[1]
            if MatchEntity.did_expired(match_id):
                raise MatchExpired()
            ticket = TicketEntity.get_by_id(ticket_id, match_id)
            user.person.return_ticket(ticket)
            send(message, "Ticket {} was successfully returned. Balance: ${}".format(ticket_id, round(user.person.fan_id_card.balance, 2)))
            return
    except ValueError:
        send(message, "Ticket ID must be an integer. Please enter the ticket ID again", enter_ticket_id_to_return)
    except TicketDoesNotExistError:
        send(message, "The entered ticket ID does not exist. Please enter the ticket ID again", enter_ticket_id_to_return)
    except TicketDoesNotBelongToCustomerError:
        send(message, "Entered ticket ID does not belong to you. Please enter another ticket ID", enter_ticket_id_to_return)
    except MatchExpired:
        send(message, "The entered match is expired. You can't return your money for it")

@bot.message_handler(regexp="Register")
def register_new_customer(message):
    if user.role == "terminal" or not user.authenticated:
        global new_customer
        new_customer = NewCustomer()
        send(message, "Enter username", enter_new_username)


def enter_new_username(message):
    res = PersonEntity.username_check(message.text)
    if res[1] == 1:
        if not PersonEntity.name_exists(message.text):
            send(message, res[0])
            if user.role == "terminal":
                new_customer.username = message.text
                send(message, "Enter password", enter_password_of_new_user)
            elif not user.authenticated:
                new_customer.username = message.text
                send(message, "Enter age", enter_age)
        else:
            send(message, "User with name {} exists. Please choose another one.".format(message.text), enter_new_username)
    else:
        send(message, res[0], enter_new_username)

def enter_age(message):
    try:
        new_customer.age = int(message.text)
        if new_customer.age < 12:
            send(message, "The minimum age must be at least 12")
        elif new_customer.age > 110:
            send(message, "It's not joking club, enter real age or go away", enter_age)
        else:
            send(message, "Enter first name", enter_first_name)
    except ValueError:
        send(message, "Age must be an integer. Please enter the age again in the correct format", enter_age)


def enter_first_name(message):
    new_customer.first_name = message.text
    send(message, "Enter last name", enter_last_name)


def enter_last_name(message):
    new_customer.last_name = message.text
    send(message, "Enter password", enter_password_of_new_user)

def enter_password_of_new_user(message):
    res = PersonEntity.password_check(message.text)
    if res[1] == 1:
        new_customer.password = message.text
        send(message, res[0])
    else:
        send(message, res[0], enter_password_of_new_user)
        return
    role = "customer"
    if user.role == "terminal":
        role = ""
        role += "organizer"
    customer = Customer(new_customer.username, new_customer.first_name, new_customer.last_name, None, role, new_customer.password, "NULL", None)
    try:
        if customer.role == "organizer":
            PersonEntity.register(customer, creator="terminal")
        else:
            PersonEntity.register(customer, creator="terminal")
            FanIDCard.create(customer.username)
        send(message, "The customer was successfully registered".format(customer.username))
        send(message, "Username: {}\nPassword: {}".format(customer.username, customer.password))
    except IncorrectInputFormat as error:
        send(message, error)
    except UserAlreadyExistsError as error:
        send(message, error)


@bot.message_handler(regexp="Unblock Fan ID Card")
def unblock_fan_id_card(message):
    if user.role == "terminal":
        send(message, "Enter Fan ID Card holder's username you would like to unblock", enter_username_to_unblock)


def enter_username_to_unblock(message):
    username = message.text
    try:
        customer = Customer.construct(username)
        user.person.unblock_fan_id_card(customer)
        send(message, "The Fan ID Card {} was successfully unblocked".format(customer.fan_id_card.card_id))
    except CustomerDoesNotExistError:
        send(message, "Customer with username \"{}\" does not exist. Or you have choosen yourself or organizer, which restricted.".format(username))
    except TicketAlreadyUnblocked:
        send(message, "The Fan ID Card {} has already unblocked".format(customer.fan_id_card.card_id))


@bot.message_handler(regexp="Block Fan ID Card")
def block_fan_id_card(message):
    if user.role == "terminal":
        send(message, "Enter Fan ID Card holder's username you would like to block", enter_username_to_block)


def enter_username_to_block(message):
    username = message.text
    try:
        customer = Customer.construct(username)
        user.person.block_fan_id_card(customer)
        send(message, "The Fan ID Card {} was successfully blocked".format(customer.fan_id_card.card_id))
    except CustomerDoesNotExistError:
        send(message, "Customer with username \"{}\" does not exist. Or you have choosen yourself or organizer, which restricted.".format(username))
    except TicketAlreadyBlocked:
        send(message, "The Fan ID Card {} has already blocked".format(customer.fan_id_card.card_id))


@bot.message_handler(regexp="Add match")
def add_match(message):
    if user.role == "organizer":
        global new_match
        new_match = NewMatch()
        send(message, "Enter host team", enter_host_team)


def enter_host_team(message):
    new_match.host_team = message.text
    send(message, "Enter guest team", enter_guest_team)


def enter_guest_team(message):
    new_match.guest_team = message.text
    send(message, "Enter match date in format YYYY-MM-DD", enter_match_date)


def is_valid_date(datestring):
    try:
        datetime.datetime.strptime(datestring, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def enter_match_date(message):
    new_match.date = message.text
    if not is_valid_date(new_match.date):
        send(message, "The entered date is not in the format YYYY-MM-DD.", show)
        return
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row("Group")
    user_markup.row("Quarterfinal")
    user_markup.row("Semifinal")
    user_markup.row("Final")
    user_markup.row("Continue")
    sent = bot.send_message(message.chat.id, "Choose match type", reply_markup=user_markup)
    bot.register_next_step_handler(sent, enter_match_type)


def enter_match_type(message):
    match_type = message.text
    if not (match_type == "Group" or match_type == "Quarterfinal" or match_type == "Semifinal" or match_type == "Final"):
        send(message, "\"{}\" does not exist as a match type.".format(match_type), show)
        return
    new_match.match_type = match_type
    match = Match(None, new_match.host_team, new_match.guest_team, new_match.date, user.person.username, new_match.match_type)
    user.person.add_match(match)
    send(message, "The match {} between {} and {} was successfully added".format(match.id, match.host_team, match.guest_team) + " press <<Continue>>", show)

@bot.message_handler(regexp='Update match')
def update_match(message):
    if user.role == "organizer":
        send(message, "Enter match ID you would like to update", enter_match_id_to_update)


def enter_match_id_to_update(message):
    try:
        match_id = int(message.text)
        global match
        match = Match.construct(match_id)
        user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
        user_markup.row("Host team", "Guest team")
        user_markup.row("Match date", "Match type")
        user_markup.row("Cancel")
        sent = bot.send_message(message.chat.id, "Choose field you would like to update", reply_markup=user_markup)
        bot.register_next_step_handler(sent, enter_field_to_udpate)
    except ValueError:
        send(message, "Match ID must be an integer.",show)
        return
    except MatchDoesNotExistError:
        send(message, "The entered match ID does not exist.", show)
        return


def enter_field_to_udpate(message):
    field = message.text
    if field == "Host team":
        send(message, "Enter new name of host team", enter_new_host_team)
    elif field == "Guest team":
        send(message, "Enter new name of guest team", enter_new_guest_team)
    elif field == "Match date":
        send(message, "Enter new match date in format YYYY-MM-DD", enter_new_match_date)
    elif field == "Match type":
        user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
        user_markup.row("Group")
        user_markup.row("Quarterfinal")
        user_markup.row("Semifinal")
        user_markup.row("Final")
        user_markup.row("Cancel")
        sent = bot.send_message(message.chat.id, "Choose match type", reply_markup=user_markup)
        bot.register_next_step_handler(sent, enter_new_match_type)
    else:
        send(message, "The chosen field does not exist.")
        return


def enter_new_host_team(message):
    match.host_team = message.text
    user.person.update_match(match)
    send(message, "Host team name was successfully updated", show)


def enter_new_guest_team(message):
    match.guest_team = message.text
    user.person.update_match(match)
    send(message, "Guest team name was successfully updated", show)


def enter_new_match_date(message):
    match.date = message.text
    if not is_valid_date(match.date):
        send(message, "The entered date is not in the format YYYY-MM-DD.", show)
        return
    user.person.update_match(match)
    send(message, "Match date was successfully updated", show)


def enter_new_match_type(message):
    match.match_type = message.text
    if not (match.match_type == "Group" or match.match_type == "Quarterfinal" or match.match_type == "Semifinal" or match.match_type == "Final"):
        send(message, "\"{}\" does not exist as a match type.",show)
        return
    user.person.update_match(match)
    send(message, "Match type name was successfully updated", show)


@bot.message_handler(regexp='Delete match')
def delete_match(message):
    if user.role == "organizer":
        send(message, "Enter match ID you would like to delete", enter_match_id_to_delete)


def enter_match_id_to_delete(message):
    try:
        match_id = int(message.text)
        if not MatchEntity.does_exist(match_id):
            raise MatchDoesNotExistError()
        if not MatchEntity.did_expired(match_id) and TicketEntity.get_tickets_cnt_for_match_id(match_id) > 0 or not MatchEntity.did_expired(match_id):
            raise MatchDelitionRestricted()
        user.person.delete_match(match_id)
        send(message, "The match {} was successfully deleted".format(match_id))
    except ValueError:
        send(message, "Match ID must be an integer. Please enter the match ID again", enter_match_id_to_delete)
    except MatchDoesNotExistError:
        send(message, "The entered match ID does not exist.", show)
    except MatchDelitionRestricted:
        send(message, "You can't delete match while it hasn't expired or there are users with tickets for this match. ", show)


@bot.message_handler(regexp='Cancel match')
def cancel_match(message):
    if user.role == "organizer":
        send(message, "Enter match ID you would like to cancel", enter_match_id_to_cancel)


def enter_match_id_to_cancel(message):
    try:
        match_id = int(message.text)
        if not MatchEntity.does_exist(match_id):
            raise MatchDoesNotExistError()
        if MatchEntity.did_expired(match_id):
            raise MatchExpired()
        user.person.cancel_match(match_id)
        send(message, "The match {} was successfully cancelled".format(match_id))
    except ValueError:
        send(message, "Match ID must be an integer.")
    except MatchDoesNotExistError:
        send(message, "The entered match ID does not exist.")
    except MatchExpired:
        send(message, "The entered match is expired. Go <<Delete match>> to get success", show)


bot.polling()