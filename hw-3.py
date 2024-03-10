from collections import UserDict
import datetime


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        super().__init__(value)
        if not self.validate():
            raise ValueError('Invalid phone number')

    def validate(self):
        return len(self.value) == 10 and self.value.isdigit()


class Birthday(Field):
    def __init__(self, date_string):
        self.value = self.validate(date_string)
        if not self.value:
            raise ValueError('Invalid birthday format. Use DD.MM.YYYY')

    def validate(self, date_string):
        try:
            return datetime.datetime.strptime(date_string, '%d.%m.%Y')
        except ValueError:
            return None


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))

    def remove_phone(self, phone_number):
        self.phones = [phone for phone in self.phones if phone.value != phone_number]

    def edit_phone(self, old_number, new_number):
        for phone in self.phones:
            if phone.value == old_number:
                phone.value = new_number
                break

    def find_phone(self, phone_number):
        return next((phone for phone in self.phones if phone.value == phone_number), None)

    def add_birthday(self, birthday):
        self.birthday = birthday
        return True

    def days_to_birthday(self):
        if not self.birthday:
            return None

        today = datetime.date.today()
        birthday_date = datetime.date(today.year, self.birthday.month, self.birthday.day)

        if birthday_date < today:
            birthday_date = birthday_date.replace(year=today.year + 1)

        return (birthday_date - today).days

    def __str__(self):
        return (f"Contact name: {self.name.value}, "
                f"phones: {'; '.join(p.value for p in self.phones)}, "
                f"birthday: {self.birthday}" if self.birthday else "")


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        del self.data[name]

    def change_phone(self, name, new_phone):
        record = self.data.get(name)
        if record and record.phones:
            old_phone = record.phones[0].value
            record.edit_phone(old_phone, new_phone)

    def show_phone(self, name):
        record = self.data.get(name)
        if record:
            return '; '.join(phone.value for phone in record.phones)

    def show_all(self):
        return '\n'.join(str(record) for record in self.data.values())


def add_handler(args):
    if len(args) != 3:
        return 'Invalid command usage: add <name> <phone>'
    name, phone = args[1:]
    record = Record(name)
    record.add_phone(phone)
    book.add_record(record)
    return f"Contact {name} added"


def change_handler(args):
    if len(args) != 3:
        return 'Invalid command usage: change <name> <new_phone>'
    name, new_phone = args[1:]
    book.change_phone(name, new_phone)
    return f"Phone number for {name} changed"


def phone_handler(args):
    if len(args) != 2:
        return 'Invalid command usage: phone <name>'
    name = args[1]
    return book.show_phone(name) or f"Contact {name} not found"


def all_handler(args):
    return book.show_all()


def add_birthday_handler(args):
    if len(args) != 3:
        return 'Invalid command usage: add_birthday <name> <birthday>'
    name, birthday = args[1:]
    contact = book.find(name)
    if contact:
        birthday_obj = Birthday(birthday)
        contact.add_birthday(birthday_obj)
        return f"Birthday added for {name}"
    else:
        return f"Contact {name} not found"


def show_birthday_handler(args):
    if len(args) != 2:
        return 'Invalid command usage: show_birthday <name>'

    name = args[1]
    contact = book.find(name)

    if contact and contact.birthday:
        return f"Birthday for {name}: {contact.birthday}"
    else:
        return f"Contact {name} does not have a birthday or not found"


def birthdays_handler(args):
    today = datetime.date.today()
    next_week = today + datetime.timedelta(days=7)
    birthdays = []

    for contact in book.values():
        if contact.birthday:
            birthday_date = datetime.date(contact.birthday.value.year, contact.birthday.value.month, contact.birthday.value.day)
            if (birthday_date.day, birthday_date.month) >= (today.day, today.month) and (birthday_date.day, birthday_date.month) <= (next_week.day, next_week.month):
                birthdays.append(contact)
    if birthdays:
        for birthday in birthdays:
            print(f"Upcoming birthdays within the next week:\n {birthday}")
    else: 'No birthdays within the next week.'

    return ''


def hello_handler(args):
    return 'Hello, how can I assist you today?'


def close_handler(args):
    exit(0)


handlers = {
    'add': add_handler,
    'change': change_handler,
    'phone': phone_handler,
    'all': all_handler,
    'add-birthday': add_birthday_handler,
    'show-birthday': show_birthday_handler,
    'birthdays': birthdays_handler,
    'hello': hello_handler,
    'close': close_handler,
    'exit': close_handler,
}


book = AddressBook()


while True:
    command = input().split()
    handler = handlers.get(command[0])
    if handler:
        print(handler(command))
    else:
        print('Unknown command')
