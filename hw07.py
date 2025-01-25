from collections import UserDict
from datetime import datetime, date, timedelta

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)
    
class Name(Field):
    def __init__(self, name):
        super().__init__(name)

class Phone(Field):
    def __init__(self, phone):
        if len(phone) == 10 and phone.isdigit():
            super().__init__(phone)
        else:
            raise ValueError('Phone number is not valid.')
        
class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError
        else:
            super().__init__(value)

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone_number):
        phone = self.find_phone(phone_number)
        self.phones.remove(phone)

    def edit_phone(self, old_phone, new_phone):
        if self.find_phone(old_phone):
            self.add_phone(new_phone)
            self.remove_phone(old_phone)
        else:
            raise ValueError('Phone number is not valid.')

    def find_phone(self, phone_number):
        phone = list(filter(lambda phone: phone.value == phone_number, self.phones))
        if phone:
            return phone[0]
        else:
            return None

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}, bithday: {self.birthday}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record
    
    def find(self, name):
        if name in self.data.keys():
            return self.data[name]
        else:
            return None

    def delete(self, name):
        del self.data[name]

    def get_upcoming_birthdays(self, days=7):
        upcoming_birthdays = []
        today = date.today()
        users = self.data

        for user in users.items():
            try:
                birthday = datetime.strptime(user[1].birthday.value, "%d.%m.%Y")
            except AttributeError:
                continue
            birthday_this_year = birthday.replace(year=today.year).date()
            if birthday_this_year < today:
                birthday_this_year = birthday.replace(year=today.year + 1)

            if 0 <= (birthday_this_year - today).days <= days:
                birthday_this_year = adjust_for_weekend(birthday_this_year)
                congratulation_date_str = date_to_string(birthday_this_year)
                upcoming_birthdays.append({"name": user[1].name.value, "congratulation_date": congratulation_date_str})
        return upcoming_birthdays

    def __str__(self):
        result = ''
        for key, value in self.data.items():
            result += f'{key} - {value}\n'
        return result

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me valid name and phone please."
        except KeyError:
            return "There is no such contact."
        except IndexError:
            return "Something went wrong."

    return inner

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_contact(args, book):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None and Phone(phone):
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    message = "Contact updated"
    if record:
        record.edit_phone(old_phone, new_phone)
    else:
        message = "No such conctact"
    return message
 
@input_error
def show_contact(args, book):
    name, *_ = args
    record = book.find(name)
    if record:
        return record

@input_error
def all_contacts(book):
    result = ''
    for item in book.items():
        result += f"{item[1]} \n"
    return result

@input_error
def add_birthday(args, book):
    name, birthday, *_ = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return("Birthday added")
    else:
        raise ValueError

@input_error
def show_birthday(args, book):
    name, *_ = args
    record = book.find(name)
    if record:
        return datetime.strftime(record.birthday.value, "%d.%m.%Y")
    else:
        raise ValueError

@input_error
def birthdays(book):
    upcoming_birthdays = book.get_upcoming_birthdays()
    result = ''
    for user in upcoming_birthdays:
        result += f'{user['name']} - {user['congratulation_date']} \n'
    return result

def string_to_date(date_string):
    return datetime.strptime(date_string, "%d.%m.%Y").date()

def date_to_string(date):
    return date.strftime("%d.%m.%Y")

def prepare_user_list(user_data):
    prepared_list = []
    for user in user_data:
        prepared_list.append({"name": user["name"], "birthday": string_to_date(user["birthday"])})
    return prepared_list

def find_next_weekday(start_date, weekday):
    days_ahead = weekday - start_date.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return start_date + timedelta(days=days_ahead)

def adjust_for_weekend(birthday):
    if birthday.weekday() >= 5:
        return find_next_weekday(birthday, 0)
    return birthday

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_contact(args, book))
        elif command == "all":
            print(all_contacts(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(book))
        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()