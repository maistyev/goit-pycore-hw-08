import re
import pickle
from typing import List, Optional, Dict, Tuple, Callable
from collections import UserDict
from datetime import datetime, timedelta


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено

def input_error(func: Callable) -> Callable:
    '''Decorator that handles exceptions in the input function'''
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return f"Error: {str(e)}"
        except KeyError as e:
            return f"Error: {str(e)}"
        except IndexError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            return f"An unexpected error occurred: {e}"
    return wrapper

def parse_input(user_input: str) -> Tuple[str, str]:
    cmd, *args = user_input.split() # Split the input into command and arguments.
    cmd = cmd.strip().lower() # Convert the command to lowercase.
    return cmd, *args



class Field:
    def __init__(self, value: str):
        self.value = value

    def __str__(self) -> str:
        return str(self.value)

class Name(Field):
    # Клас для зберігання імені контакту
    pass

class Birthday(Field):
    def __init__(self, value: str):
        if not self.validate(value):
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        birthday = datetime.strptime(value, "%d.%m.%Y")
        super().__init__(birthday)
        
    @staticmethod
    def validate(birthday: str) -> bool:
        # Перевірка, чи містить дата народження коректний формат
        return bool(re.match(r'^\d{2}\.\d{2}\.\d{4}$', birthday))

class Phone(Field):
    def __init__(self, value: str):
        # Валідація номера телефону перед ініціалізацією
        if not self.validate(value):
            raise ValueError("Phone number must contain 10 digits")
        super().__init__(value)

    @staticmethod
    def validate(phone: str) -> bool:
        # Перевірка, чи містить номер телефону рівно 10 цифр
        return bool(re.match(r'^\d{10}$', phone))
    
    def __str__(self) -> str:
        # Рядкове представлення номера телефону
        return str(self.value)

class Record:
    def __init__(self, name: str, phone: str):
        self.name: Name = Name(name)
        self.phones: List[Phone] = []
        self.add_phone(phone)
        self.birthday: Birthday = None

    def add_phone(self, phone: str) -> None:
        # Додавання нового номера телефону до запису
        self.phones.append(Phone(phone))

    def remove_phone(self, phone: str) -> None:
        # Видалення номера телефону з запису
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone: str, new_phone: str) -> None:
        # Редагування існуючого номера телефону
        for p in self.phones:
            if p.value == old_phone:
                p.value = new_phone
                break
        else:
            raise ValueError("Phone number not found")
        
    def add_birthday(self, birthday: str) -> None:
        # Додавання дати народження
        self.birthday = Birthday(birthday)

    def find_phone(self, phone: str) -> Optional[Phone]:
        # Пошук телефону за номером
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def __str__(self) -> str:
        # Рядкове представлення запису
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}, birthday: {self.birthday.value if self.birthday else 'No info'}"

class AddressBook(UserDict):
    def add_record(self, record: Record) -> None:
        # Додавання нового запису до адресної книги
        self.data[record.name.value] = record

    def find(self, name: str) -> Optional[Record]:
        # Пошук запису за ім'ям
        return self.data.get(name)

    def delete(self, name: str) -> None:
        # Видалення запису за ім'ям
        if name in self.data:
            del self.data[name]

    @staticmethod
    def next_monday(day: datetime) -> datetime:
        # Пошук наступного понеділка

        days_to_monday = (7 - day.weekday()) % 7
        return day + timedelta(days=days_to_monday)

    def get_upcoming_birthdays(self) -> List[Record]:
        # Пошук контактів, у яких найближчим часом буде день народження
        today = datetime.now()
        upcoming_birthdays = []
        record: Record

        for record in self.data.values():
            if record.birthday:
                birthday_this_year = record.birthday.value.replace(year=today.year)

                if birthday_this_year < today:
                    birthday_this_year = birthday_this_year.replace(year=today.year + 1)

                days_until_birthday = (birthday_this_year - today).days

                if 0 <= days_until_birthday <= 7:
                    congratulation_date = birthday_this_year if birthday_this_year.weekday() < 5 else self.next_monday(birthday_this_year)
                    upcoming_birthdays.append({
                        "name": self.data[record.name.value].name.value,
                        "congratulation_date": congratulation_date.strftime("%Y-%m-%d")
                    })

        return upcoming_birthdays
    

@input_error
def add_contact(book: AddressBook, name: str, phone: str) -> str:
    '''Function that adds a contact to the dictionary and returns a string with the result
    If the contact already exists, the function adds a new phone number to the existing contact'''

    if book.find(name) is None:    
        record = Record(name, phone)
        book.add_record(record)
        return f"Contact {name} has been added with phone number {phone}"
    else:
        book.data[name].add_phone(phone)
        return f"Phone number {phone} has been added to contact {name}"



@input_error
def edit_contact_phone(book: AddressBook, name: str, old_phone: str, new_phone: str) -> str:
    '''Function that changes the phone number of a contact in the dictionary and returns a string with the result
    If the contact does not exist, the function returns a string with an error message'''
    if book.find(name) is None:
        raise KeyError(f"Contact {name} does not exist")
    book.data[name].edit_phone(old_phone, new_phone)
    return f"Contact {name} has been changedphone number from {old_phone} to phone number {new_phone}"

@input_error
def show_phones(book: AddressBook, name: str) -> str:
    '''Function that returns the string with all phone numbers of a contact from the address book
    If the contact does not exist, the function returns a string with an error message'''
    if book.find(name) is None:
        raise KeyError(f"Contact {name} does not exist")    
    
    phone_numbers = ", ".join(phone.value for phone in book.data[name].phones)
    return f"Phone numbers for {name} are: {phone_numbers}"

@input_error
def show_all(book: AddressBook) -> str:
    '''Function that returns string with all contacts from the dictionary
    If the dictionary is empty, the function returns a string with an error message'''
    if not book.data:
        raise Exception("No contacts found")
    result = ""
    for record in book.data.values():
        result += f"{record}\n"

    return result

@input_error
def add_birthday(book: AddressBook, name: str, birthday: str) -> str:
    '''Function that adds a birthday to the contact in the dictionary and returns a string with the result
    If the contact does not exist, the function returns a string with an error message'''
    if book.find(name) is None:
        raise KeyError(f"Contact {name} does not exist")
    book.data[name].add_birthday(birthday)
    return f"Birthday {birthday} has been added to contact {name}"

@input_error
def show_birthday(book: AddressBook, name: str) -> str:
    '''Function that returns the string with the birthday of a contact from the address book
    If the contact does not exist or has no birthday, the function returns a string with an error message'''
    if book.find(name) is None:
        raise KeyError(f"Contact {name} does not exist")
    if not book.data[name].birthday:
        raise ValueError(f"Contact {name} has no birthday")
    return f"Birthday for {name} is {book.data[name].birthday.value.strftime('%d.%m.%Y')}"

@input_error
def birthdays(book: AddressBook) -> str:
    '''Function that returns a string with all upcoming birthdays from the address book'''
    upcoming_birthdays = book.get_upcoming_birthdays()
    if not upcoming_birthdays:
        return "No upcoming birthdays"
    result = ""
    for birthday in upcoming_birthdays:
        result += f"{birthday['name']} - {birthday['congratulation_date']}\n"
    return "Upcoming birthdays: \n" + result



def main():
    print("Welcome to the assistant bot!")
    book = load_data()
    try:
        while True:
            user_input = input("Enter a command: ").strip()
            command, *args = parse_input(user_input)
            
            match command:
                case "hello":
                    print("Hello! How can I help you?")
                case "add":
                    if len(args) != 2:
                        print("Invalid number of arguments for command 'add'. Please enter a name and phone number")
                        continue
                    print(add_contact(book, *args))
                case "change":
                    if len(args) != 3:
                        print("Invalid number of arguments for command 'change'. Please enter a name, old phone number and new phone number")
                        continue
                    print(edit_contact_phone(book, *args))
                case "phone":
                    if len(args) != 1:
                        print("Invalid number of arguments for command 'phone'. Please enter a name")
                        continue
                    print(show_phones(book, *args))
                case "all":
                    print(show_all(book))
                case "add-birthday":
                    if len(args) != 2:
                        print("Invalid number of arguments for command 'add-birthday'. Please enter a name and birthday")
                        continue
                    print(add_birthday(book, *args))
                case "show-birthday":
                    if len(args) != 1:
                        print("Invalid number of arguments for command 'show-birthday'. Please enter a name")
                        continue
                    print(show_birthday(book, *args))
                case "birthdays":
                    print(birthdays(book))
                case "close" | "exit":
                    save_data(book)
                    print("Goodbye!")
                    break
                case "help":
                    print("Commands:\n"
                        "hello - greet the bot\n"
                        "add [name] [phone] - add a contact\n"
                        "change [name] [phone] - change the phone number of a contact\n"
                        "phone [name] - show the phone number of a contact\n"
                        "all - show all contacts\n"
                        "add-birthday [name] [birthday] - add a birthday to a contact\n"
                        "show-birthday [name] - show the birthday of a contact\n"
                        "birthdays - show all upcoming birthdays\n"
                        "close/exit - close the bot")
                case _:
                    print("Invalid command. Please try again")
                    print("Commands:\n"
                        "hello - greet the bot\n"
                        "add [name] [phone] - add a contact\n"
                        "change [name] [phone] - change the phone number of a contact\n"
                        "phone [name] - show the phone number of a contact\n"
                        "all - show all contacts\n"
                        "add-birthday [name] [birthday] - add a birthday to a contact\n"
                        "show-birthday [name] - show the birthday of a contact\n"
                        "birthdays - show all upcoming birthdays\n"
                        "close/exit - close the bot")
                    continue
    except KeyboardInterrupt:
        save_data(book)
        print("\nGoodbye!")

if __name__ == "__main__":
    main()