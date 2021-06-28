from sys import path
from time import sleep
from hashlib import sha256
from uuid import uuid4
from datetime import date

from sqlalchemy import select, and_
from rich.progress import track
from rich import print as pprint
from rich.table import Table

from richer.console import Bcolors, clear_console
from models.model import session
from models.marsh import (
    FilmMarsh,
    SalesMarsh,
)
from models.model import (
    Users,
    Salts,
    Perm,
    RegDates,
    Dates,
    Film,
    Sales,
)
from richer.gui import (
    FilmView,
    CompanyView,
    UsersView,
    CategoryView,
    SalesView,
    FilmDateView,
    SaltsView,
    PermView,
    RegDateView,
)

path.append("..")
ADMIN = False


def menu():
    global ADMIN
    func = [login, register]
    clear_console()
    m = f"{Bcolors.HEADER}Меню:{Bcolors.ENDC}\n{Bcolors.BOLD}[1] - Логін\n[2] - Реєстрація{Bcolors.ENDC}\n -> "
    while True:
        method = input(m)
        if method.isnumeric():
            if int(method) in [1, 2]:
                access = func[int(method)-1]()
                if access:
                    break
    for _ in track(range(40), description="Загрузка..."):
        sleep(0.05)
    clear_console()
    if ADMIN:
        admin_menu()
    else:
        common_menu()


def login():
    global ADMIN
    while True:
        username = input("Введіть логін -> ")
        check_user = session.execute(select(Users).where(Users.username == username)).scalars().all()
        if len(check_user) == 0:
            print(f"{Bcolors.FAIL}Такого користувача не існує{Bcolors.ENDC}")
        else:
            break
    while True:
        password = input("Введіть пароль -> ")
        get_salt = session.execute(select(Salts).where(Salts.user_id == check_user[0].id)).scalars().all()[0].salt
        new_password = sha256(get_salt.encode() + password.encode()).hexdigest()
        if new_password == check_user[0].hashed_password:
            break
        else:
            print(f"{Bcolors.FAIL}Пароль не вірний{Bcolors.ENDC}")
    perm_user = session.query(Perm).where(Perm.user_id == check_user[0].id).first()
    ADMIN = perm_user.admin
    dates_user = session.query(RegDates).where(RegDates.user_id == check_user[0].id).first()
    dates_user.last_activity = date.today()
    session.add(dates_user)
    session.commit()
    clear_console()
    print(f"{Bcolors.OKGREEN}Ви успішно увійшли{Bcolors.ENDC}")

    return True


def register():
    while True:
        username = input("Введіть логін -> ")
        if len(username) >= 3:
            break
        else:
            print(f"{Bcolors.FAIL}Довжина пароля повина бути >= 3{Bcolors.ENDC}")
    while True:
        password_first = input("Введіть пароль -> ")
        password_second = input("Введіть пароль ще раз -> ")
        if password_first == password_second:
            if len(password_first) >= 5:
                break
            else:
                print(f"{Bcolors.FAIL}Довжина пароля має бути >= 5{Bcolors.ENDC}")
        else:
            print(f"{Bcolors.FAIL}Паролі не одинакові{Bcolors.ENDC}")
    while True:
        full_name = input("Ваше повне ім'я -> ")
        if len(full_name) >= 5:
            break
        else:
            print(f"{Bcolors.FAIL}Введіть дані вірно{Bcolors.ENDC}")
    while True:
        email = input("Ваша пошта -> ")
        if len(email) >= 6:
            break
        else:
            print(f"{Bcolors.FAIL}Введіть дані вірно{Bcolors.ENDC}")
    salt = uuid4().hex
    hash_password = sha256(salt.encode() + password_first.encode()).hexdigest()
    user = Users(username=username, full_name=full_name, email=email, hashed_password=hash_password)
    session.add(user)
    session.commit()
    salt_user = Salts(user_id=user.id, salt=salt)
    perm_user = Perm(user_id=user.id)
    dates_user = RegDates(user_id=user.id)
    session.add(salt_user)
    session.add(perm_user)
    session.add(dates_user)
    session.commit()
    clear_console()
    print(f"{Bcolors.OKGREEN}Успішна реєстрація{Bcolors.ENDC}")
    return True


# Menu for superusers
def admin_menu():
    m = f"{Bcolors.HEADER}Адмін Меню:{Bcolors.ENDC}\n{Bcolors.BOLD}[1] - Перегляд таблиць\n[2] - Редагування таблиць\n"\
        f"[3] - Виведення звітів{Bcolors.ENDC}\n -> "
    admin_funcs = {1: all_table, 2: edit_table}
    while True:
        clear_console()
        method = input(m)
        if method.isnumeric():
            if int(method) in list(range(1, 4)):
                clear_console()
                admin_funcs[int(method)]()


# Menu for common users
def common_menu():
    m = f"{Bcolors.HEADER}Меню:{Bcolors.ENDC}\n{Bcolors.BOLD}[1] - Розклад фільмів\n" \
        f"[2] - Купівля квитка{Bcolors.ENDC}\n -> "
    funcs = {1: view_films_today, 2: buy_ticket}
    while True:
        method = input(m)
        if method.isnumeric():
            if int(method) in list(range(1, 3)):
                clear_console()
                funcs[int(method)]()
            else:
                clear_console()
                print(f"{Bcolors.FAIL}Введіть номер функції вірно{Bcolors.ENDC}")
        else:
            clear_console()
            print(f"{Bcolors.FAIL}Введіть номер функції вірно{Bcolors.ENDC}")


# Common Menu function to buy tickets
def buy_ticket():
    date_today = date.today()
    table = Table(title=f"Films today ({date_today})")
    table.add_column("Id", justify="center")
    table.add_column("Film", justify="center")
    table.add_column("Description", justify="center")
    table.add_column("Ticket Price", justify="center")
    all_films_id = session.execute(select(Dates).where(and_(Dates.start_date <= date_today,
                                                            Dates.end_date >= date_today))).scalars()
    f_marsh = FilmMarsh()
    s_marsh = SalesMarsh()
    for elem in all_films_id:
        film = f_marsh.dump(session.query(Film).where(Film.id == elem.film_id).first())
        sales = s_marsh.dump(session.query(Sales).where(Sales.film_id == elem.film_id).first())
        table.add_row(str(film["id"]), film["name"], film["description"], str(sales["ticket_price"]))
    while True:
        pprint(table)
        m = f"{Bcolors.HEADER}Дії{Bcolors.ENDC}\n{Bcolors.BOLD}[1] - Купити\n[2] - Повернутись{Bcolors.ENDC}"
        print(m)
        f = input(f"{Bcolors.BOLD} -> {Bcolors.ENDC}")
        if f.isnumeric():
            if int(f) == 1:
                access = False
                while True:
                    idx = input(f"{Bcolors.BOLD}Введіть індекс -> {Bcolors.ENDC}")
                    if idx.isnumeric():
                        q = session.execute(select(Dates).where(and_(Dates.start_date <= date_today,
                                                                     Dates.end_date >= date_today))).scalars()
                        for elem in q:
                            if elem.film_id == int(idx):
                                while True:
                                    count = input(f"{Bcolors.BOLD}Кількість квитків -> {Bcolors.ENDC}")
                                    if count.isnumeric():
                                        sales = session.query(Sales).where(Sales.film_id == int(idx)).first()
                                        sales.peoples += int(count)
                                        session.add(sales)
                                        session.commit()
                                        access = True
                                        break
                        if access:
                            clear_console()
                            print(f"{Bcolors.OKGREEN}Квитки куплені{Bcolors.ENDC}")
                            access = False
                            break
                        print(f"{Bcolors.FAIL}Дія введена не вірно{Bcolors.ENDC}")
            elif int(f) == 2:
                clear_console()
                return
            else:
                print(f"{Bcolors.FAIL}Дія введена не вірно{Bcolors.ENDC}")
        else:
            clear_console()
            print(f"{Bcolors.FAIL}Дія введена не вірно{Bcolors.ENDC}")


# Common Menu function for see all films today
def view_films_today():
    date_today = date.today()
    table = Table(title=f"Films today ({date_today})")
    table.add_column("Film", justify="center")
    table.add_column("Description", justify="center")
    table.add_column("Ticket Price", justify="center")
    all_films_id = session.execute(select(Dates).where(and_(Dates.start_date <= date_today,
                                                            Dates.end_date >= date_today))).scalars()
    f_marsh = FilmMarsh()
    s_marsh = SalesMarsh()
    for elem in all_films_id:
        film = f_marsh.dump(session.query(Film).where(Film.id == elem.film_id).first())
        sales = s_marsh.dump(session.query(Sales).where(Sales.film_id == elem.film_id).first())
        table.add_row(film["name"], film["description"], str(sales["ticket_price"]))
    while True:
        pprint(table)
        print(f"{Bcolors.HEADER}Дії{Bcolors.ENDC}\n{Bcolors.BOLD}[1] - Повернутись{Bcolors.ENDC}")
        f = input(f"{Bcolors.BOLD} -> {Bcolors.ENDC}")
        if f.isnumeric():
            if int(f) == 1:
                clear_console()
                break
            else:
                clear_console()
                print(f"{Bcolors.FAIL}Дія введена не вірно{Bcolors.ENDC}")
        else:
            clear_console()
            print(f"{Bcolors.FAIL}Дія введена не вірно{Bcolors.ENDC}")


# Func for print all tables names
def all_table():
    tables_names = ["Фільми", "Компанії", "Категорії", "Продажі", "Дати фільмів", "Користувачі", "Хешування",
                    "Права", "Активність", "Назад"]
    tables = {1: FilmView, 2: CompanyView, 3: CategoryView, 4: SalesView, 5: FilmDateView, 6: UsersView,
              7: SaltsView, 8: PermView, 9: RegDateView}
    m = f"{Bcolors.HEADER}Таблиці:{Bcolors.ENDC}{Bcolors.BOLD}\n"
    for idx, elem in enumerate(tables_names):
        m += f"[{idx + 1}] - {elem}\n"
    m += f"{Bcolors.ENDC} -> "
    while True:
        func = input(m)
        if func.isnumeric():
            if int(func) in list(range(1, 11)):
                if int(func) == 10:
                    break
                else:
                    clear_console()
                    tables[int(func)]().menu()
                    clear_console()


# Func for edit all tables
def edit_table():
    tables_names = ["Фільми", "Компанії", "Категорії", "Продажі", "Дати фільмів", "Користувачі", "Хешування",
                    "Права", "Активність", "Назад"]
    tables = {1: FilmView, 2: CompanyView, 3: CategoryView, 4: SalesView, 5: FilmDateView, 6: UsersView,
              7: SaltsView, 8: PermView, 9: RegDateView}
    m = f"{Bcolors.HEADER}Таблиці (Редагування):{Bcolors.ENDC}{Bcolors.BOLD}\n"
    for idx, elem in enumerate(tables_names):
        m += f"[{idx + 1}] - {elem}\n"
    m += f"{Bcolors.ENDC} -> "
    while True:
        func = input(m)
        if func.isnumeric():
            if int(func) in list(range(1, 11)):
                if int(func) == 10:
                    break
                else:
                    clear_console()
                    tables[int(func)]().menu_edit()
                    clear_console()


if __name__ == "__main__":
    menu()
