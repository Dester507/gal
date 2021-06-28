import datetime as dt
from hashlib import sha256
from uuid import uuid4

from rich import print as rich_print
from rich.table import Table
from sqlalchemy import select

from .console import Bcolors, clear_console
from models.model import session
from models.model import (
    Film,
    Company,
    Users,
    Category,
    Sales,
    Dates,
    Salts,
    Perm,
    RegDates,
)
from models.marsh import (
    FilmMarsh,
    CompanyMarsh,
    UsersMarsh,
    CategoryMarsh,
    SalesMarsh,
    DatesMarsh,
    SaltsMarsh,
    PermMarsh,
    RegDatesMarsh,
)


class FilmView:
    def __init__(self):
        self.base = Film
        self.columns = self.base.__table__.columns
        self.marsh = FilmMarsh()
        self.page = 1
        self.find = False
        self.funcs_edit_main = ["Змінити назву", "Змінити опис", "Видалити", "Новий фільм", "Вперед", "Назад", "Вихід"]
        self.funcs_edit_call_main = {1: self.edit_by_name, 2: self.edit_by_desc, 3: self.delete, 4: self.new_film,
                                     5: self.next, 6: self.back}
        self.funcs_view_main = ["Пошук по імені", "Пошук по категорії", "Пошук по компанії", "Вперед", "Назад", "Вихід"]
        self.funcs_view_call_main = {1: self.find_by_name, 2: self.find_by_category, 3: self.find_by_company,
                                     4: self.next, 5: self.back}

    def table(self):
        t = Table(title=f"{self.base.__tablename__}\n Page: {self.page}")
        for column in self.columns:
            t.add_column(column.name, justify="center")
        return t

    def print_table(self, rows):
        table = self.table()
        for row in rows:
            table.add_row(str(row["id"]), row["name"], row["description"],
                          str(row["company_id"]), str(row["category_id"]),
                          f"{row['release_date']}", f"{row['active']}")
        clear_console()
        rich_print(table)

    def next(self):
        if len(self.all_rows(self.page+1)) > 0:
            self.page += 1
            self.print_table(self.all_rows(self.page))
        else:
            self.print_table(self.all_rows(self.page))

    def back(self):
        if self.page != 1:
            self.page -= 1
        self.print_table(self.all_rows(self.page))

    def all_rows(self, page):
        return self.marsh.dump(session.execute(select(self.base)
                                               .limit(5).offset(5*(page-1))).scalars(), many=True)

    def find_by_name(self):
        name = input(f"{Bcolors.BOLD}Введіть ім'я -> {Bcolors.ENDC}")
        q = session.execute(select(self.base).where(self.base.name == name)).scalars()
        self.print_table(self.marsh.dump(q, many=True))
        self.find = True

    def find_by_category(self):
        clear_console()
        all_category = session.execute(select(Category)).scalars().all()
        m = "Категорії -"
        for elem in all_category:
            m += f" {elem.name}"
        print(f"{Bcolors.HEADER}{m} {Bcolors.ENDC}")
        name = input(f"{Bcolors.BOLD}Введіть назву -> {Bcolors.ENDC}")
        ans = -1
        for elem in all_category:
            if elem.name == name:
                ans = elem.id
        q = session.execute(select(self.base).where(self.base.category_id == ans)).scalars()
        self.print_table(self.marsh.dump(q, many=True))
        self.find = True

    def find_by_company(self):
        clear_console()
        all_company = session.execute(select(Company)).scalars().all()
        m = "Компанії -"
        for elem in all_company:
            m += f" {elem.name}"
        print(f"{Bcolors.HEADER}{m}{Bcolors.ENDC}")
        name = input(f"{Bcolors.BOLD}Введіть назву -> {Bcolors.ENDC}")
        ans = -1
        for elem in all_company:
            if elem.name == name:
                ans = elem.id
        q = session.execute(select(self.base).where(self.base.company_id == ans)).scalars()
        self.print_table(self.marsh.dump(q, many=True))
        self.find = True

    def edit_by_name(self):
        all_films = session.execute(select(self.base)).scalars().all()
        while True:
            idx = input(f"{Bcolors.BOLD}Введіть id -> {Bcolors.ENDC}")
            if idx.isnumeric():
                for elem in all_films:
                    if elem.id == int(idx):
                        while True:
                            new_name = input(f"{Bcolors.BOLD}Нова назва -> {Bcolors.ENDC}")
                            if len(new_name) > 0:
                                film = session.query(self.base).where(self.base.id == idx).first()
                                film.name = new_name
                                session.add(film)
                                session.commit()
                                break
                            else:
                                print(f"{Bcolors.FAIL}Введіть правельну назву{Bcolors.ENDC}")
                        self.print_table(self.all_rows(1))
                        return
                    elif all_films[-1] == elem:
                        print(f"{Bcolors.FAIL}Такого фільма не існує{Bcolors.ENDC}")
            else:
                print(f"{Bcolors.FAIL}Не правильний id{Bcolors.ENDC}")

    def edit_by_desc(self):
        all_films = session.execute(select(self.base)).scalars().all()
        while True:
            idx = input(f"{Bcolors.BOLD}Введіть id -> {Bcolors.ENDC}")
            if idx.isnumeric():
                for elem in all_films:
                    if elem.id == int(idx):
                        while True:
                            new_desc = input(f"{Bcolors.BOLD}Новий опис -> {Bcolors.ENDC}")
                            if len(new_desc) > 0:
                                film = session.query(self.base).where(self.base.id == idx).first()
                                film.description = new_desc
                                session.add(film)
                                session.commit()
                                break
                            else:
                                print(f"{Bcolors.FAIL}Введіть правельну назву{Bcolors.ENDC}")
                        self.print_table(self.all_rows(1))
                        return
                    elif all_films[-1] == elem:
                        print(f"{Bcolors.FAIL}Такого фільма не існує{Bcolors.ENDC}")
            else:
                print(f"{Bcolors.FAIL}Не правильний id{Bcolors.ENDC}")

    def delete(self):
        all_films = session.execute(select(self.base)).scalars().all()
        while True:
            idx = input(f"{Bcolors.BOLD}Введіть id -> {Bcolors.ENDC}")
            if idx.isnumeric():
                for elem in all_films:
                    if elem.id == int(idx):
                        session.delete(session.query(Dates).where(Dates.film_id == elem.id).first())
                        session.delete(session.query(Sales).where(Sales.film_id == elem.id).first())
                        session.delete(elem)
                        session.commit()
                        self.print_table(self.all_rows(1))
                        return
                    elif all_films[-1] == elem:
                        print(f"{Bcolors.FAIL}Такого фільма не існує{Bcolors.ENDC}")
            else:
                print(f"{Bcolors.FAIL}Не правильний id{Bcolors.ENDC}")

    def new_film(self):
        while True:
            name = input(f"{Bcolors.BOLD}Назва -> {Bcolors.ENDC}")
            if len(name) > 0:
                break
            else:
                print(f"{Bcolors.FAIL}Введіть правельну назву{Bcolors.ENDC}")
        while True:
            desc = input(f"{Bcolors.BOLD}Опис -> {Bcolors.ENDC}")
            if len(desc) > 0:
                break
            else:
                print(f"{Bcolors.FAIL}Введіть правельний опис{Bcolors.ENDC}")
        while True:
            all_category = session.execute(select(Category)).scalars().all()
            m = "Категорії -"
            for elem in all_category:
                m += f" {elem.name}"
            print(f"{Bcolors.HEADER}{m} {Bcolors.ENDC}")
            cat = input(f"{Bcolors.BOLD}Введіть назву -> {Bcolors.ENDC}")
            ans = -1
            for elem in all_category:
                if elem.name == cat:
                    ans = elem.id
            if ans != -1:
                cat = ans
                break
            else:
                print(f"{Bcolors.FAIL}Такої категорії не існує{Bcolors.ENDC}")
        while True:
            all_company = session.execute(select(Company)).scalars().all()
            m = "Компанії -"
            for elem in all_company:
                m += f" {elem.name}"
            print(f"{Bcolors.HEADER}{m} {Bcolors.ENDC}")
            comp = input(f"{Bcolors.BOLD}Введіть назву -> {Bcolors.ENDC}")
            ans = -1
            for elem in all_company:
                if elem.name == comp:
                    ans = elem.id
            if ans != -1:
                comp = ans
                break
            else:
                print(f"{Bcolors.FAIL}Такої компанії не існує{Bcolors.ENDC}")
        while True:
            act = input(f"{Bcolors.BOLD}Активний (1-так, 2-ні) -> {Bcolors.ENDC}")
            if act.isnumeric():
                if int(act) in list(range(1, 3)):
                    act = int(act)
                    break
        while True:
            print(f"{Bcolors.HEADER}Дата початку показу{Bcolors.ENDC}")
            year = input(f"{Bcolors.BOLD}Рік -> {Bcolors.ENDC}")
            if year.isnumeric():
                year = int(year)
                month = input(f"{Bcolors.BOLD}Місяць -> {Bcolors.ENDC}")
                if month.isnumeric():
                    month = int(month)
                    if month in list(range(1, 13)):
                        day = input(f"{Bcolors.BOLD}День -> {Bcolors.ENDC}")
                        if day.isnumeric():
                            day = int(day)
                            if day in list(range(1, 32)):
                                st_date = dt.date(year, month, day)
                                break
                            else:
                                print(f"{Bcolors.FAIL}Не правильний день{Bcolors.ENDC}")
                        else:
                            print(f"{Bcolors.FAIL}Не правильний день{Bcolors.ENDC}")
                    else:
                        print(f"{Bcolors.FAIL}Не правильний місяць{Bcolors.ENDC}")
                else:
                    print(f"{Bcolors.FAIL}Не правильний місяць{Bcolors.ENDC}")
            else:
                print(f"{Bcolors.FAIL}Не правильний рік{Bcolors.ENDC}")
        while True:
            print(f"{Bcolors.HEADER}Дата кінця показу{Bcolors.ENDC}")
            year = input(f"{Bcolors.BOLD}Рік -> {Bcolors.ENDC}")
            if year.isnumeric():
                year = int(year)
                month = input(f"{Bcolors.BOLD}Місяць -> {Bcolors.ENDC}")
                if month.isnumeric():
                    month = int(month)
                    if month in list(range(1, 13)):
                        day = input(f"{Bcolors.BOLD}День -> {Bcolors.ENDC}")
                        if day.isnumeric():
                            day = int(day)
                            if day in list(range(1, 32)):
                                end_date = dt.date(year, month, day)
                                break
                            else:
                                print(f"{Bcolors.FAIL}Не правильний день{Bcolors.ENDC}")
                        else:
                            print(f"{Bcolors.FAIL}Не правильний день{Bcolors.ENDC}")
                    else:
                        print(f"{Bcolors.FAIL}Не правильний місяць{Bcolors.ENDC}")
                else:
                    print(f"{Bcolors.FAIL}Не правильний місяць{Bcolors.ENDC}")
            else:
                print(f"{Bcolors.FAIL}Не правильний рік{Bcolors.ENDC}")
        while True:
            price = input(f"{Bcolors.BOLD}Ціна квитка -> {Bcolors.ENDC}")
            if price.isnumeric():
                price = int(price)
                break
            else:
                print(f"{Bcolors.FAIL}Введіть вірну ціну{Bcolors.ENDC}")
        film = self.base(name=name, description=desc, company_id=comp, category_id=cat, active=act)
        session.add(film)
        session.commit()
        film_sales = Sales(film_id=film.id, peoples=0, ticket_price=price)
        film_dates = Dates(film_id=film.id, start_date=st_date, end_date=end_date)
        session.add_all([film_dates, film_sales])
        session.commit()
        self.print_table(self.all_rows(1))

    def menu(self):
        self.print_table(self.all_rows(self.page))
        while True:
            if not self.find:
                print(f"{Bcolors.HEADER} Дії {Bcolors.ENDC}")
                for idx, elem in enumerate(self.funcs_view_main):
                    print(f"{Bcolors.BOLD}[{idx+1}] - {elem}{Bcolors.ENDC}")
                func = input(" -> ")
                if func.isnumeric():
                    if int(func) in list(range(1, len(self.funcs_view_main)+1)):
                        if int(func) == len(self.funcs_view_main):
                            break
                        else:
                            self.funcs_view_call_main[int(func)]()
                    else:
                        self.print_table(self.all_rows(self.page))
                else:
                    self.print_table(self.all_rows(self.page))
            else:
                while True:
                    print(f"{Bcolors.HEADER} Дії {Bcolors.ENDC}\n{Bcolors.BOLD}[1] - Повернутись{Bcolors.ENDC}")
                    func = input(" -> ")
                    if func.isnumeric():
                        if int(func) == 1:
                            self.find = False
                            break
                self.page = 1
                clear_console()
                self.print_table(self.all_rows(self.page))
        return

    def menu_edit(self):
        self.print_table(self.all_rows(self.page))
        while True:
            print(f"{Bcolors.HEADER} Дії {Bcolors.ENDC}")
            for idx, elem in enumerate(self.funcs_edit_main):
                print(f"{Bcolors.BOLD}[{idx+1}] - {elem}{Bcolors.ENDC}")
            func = input(" -> ")
            if func.isnumeric():
                if int(func) in list(range(1, len(self.funcs_edit_main)+1)):
                    if int(func) == len(self.funcs_edit_main):
                        break
                    else:
                        self.funcs_edit_call_main[int(func)]()
                else:
                    self.print_table(self.all_rows(self.page))
            else:
                self.print_table(self.all_rows(self.page))
        return


class CompanyView:
    def __init__(self):
        self.base = Company
        self.columns = self.base.__table__.columns
        self.marsh = CompanyMarsh()
        self.page = 1
        self.find = False
        self.funcs_edit_main = ["Зміна назви", "Видалити", "Створити", "Вперед", "Назад", "Вихід"]
        self.funcs_edit_call_main = {1: self.edit_by_name, 2: self.delete, 3: self.new_company,
                                     4: self.next, 5: self.back}
        self.funcs_view_main = ["Пошук по імені", "Вперед", "Назад", "Вихід"]
        self.funcs_view_call_main = {1: self.find_by_name, 2: self.next, 3: self.back}

    def table(self):
        t = Table(title=f"{self.base.__tablename__}\n Page: {self.page}")
        for column in self.columns:
            t.add_column(column.name, justify="center")
        return t

    def print_table(self, rows):
        table = self.table()
        for row in rows:
            table.add_row(str(row["id"]), row["name"])
        clear_console()
        rich_print(table)

    def edit_by_name(self):
        all_company = session.execute(select(self.base)).scalars().all()
        while True:
            idx = input(f"{Bcolors.BOLD}Введіть id -> {Bcolors.ENDC}")
            if idx.isnumeric():
                for elem in all_company:
                    if elem.id == int(idx):
                        while True:
                            new_name = input(f"{Bcolors.BOLD}Нова назва -> {Bcolors.ENDC}")
                            if len(new_name) > 0:
                                company = session.query(self.base).where(self.base.id == idx).first()
                                company.name = new_name
                                session.add(company)
                                session.commit()
                                break
                            else:
                                print(f"{Bcolors.FAIL}Введіть правельну назву{Bcolors.ENDC}")
                        self.print_table(self.all_rows(1))
                        return
                    elif all_company[-1] == elem:
                        print(f"{Bcolors.FAIL}Такої компанії не існує{Bcolors.ENDC}")
            else:
                print(f"{Bcolors.FAIL}Не правильний id{Bcolors.ENDC}")

    def delete(self):
        all_company = session.execute(select(self.base)).scalars().all()
        while True:
            idx = input(f"{Bcolors.BOLD}Введіть id -> {Bcolors.ENDC}")
            if idx.isnumeric():
                for elem in all_company:
                    if elem.id == int(idx):
                        all_films = session.execute(select(Film).where(Film.comany_id == elem.id)).scalars()
                        for film in all_films:
                            session.delete(session.query(Dates).where(Dates.film_id == film.id).first())
                            session.delete(session.query(Sales).where(Sales.film_id == film.id).first())
                            session.delete(film)
                        session.delete(elem)
                        session.commit()
                        self.print_table(self.all_rows(1))
                        return
                    elif all_company[-1] == elem:
                        print(f"{Bcolors.FAIL}Такої компанії не існує{Bcolors.ENDC}")
            else:
                print(f"{Bcolors.FAIL}Не правильний id{Bcolors.ENDC}")

    def new_company(self):
        while True:
            name = input(f"{Bcolors.BOLD}Назва -> {Bcolors.ENDC}")
            if len(name) > 0:
                break
            else:
                print(f"{Bcolors.FAIL}Введіть правельну назву{Bcolors.ENDC}")
        company = self.base(name=name)
        session.add(company)
        session.commit()
        self.print_table(self.all_rows(1))

    def next(self):
        if len(self.all_rows(self.page+1)) > 0:
            self.page += 1
            self.print_table(self.all_rows(self.page))
        else:
            self.print_table(self.all_rows(self.page))

    def back(self):
        if self.page != 1:
            self.page -= 1
        self.print_table(self.all_rows(self.page))

    def all_rows(self, page):
        return self.marsh.dump(session.execute(select(self.base)
                                               .limit(5).offset(5*(page-1))).scalars(), many=True)

    def find_by_name(self):
        name = input(f"{Bcolors.BOLD}Введіть ім'я -> {Bcolors.ENDC}")
        q = session.execute(select(self.base).where(self.base.name == name)).scalars()
        self.print_table(self.marsh.dump(q, many=True))
        self.find = True

    def menu(self):
        self.print_table(self.all_rows(self.page))
        while True:
            if not self.find:
                print(f"{Bcolors.HEADER} Дії {Bcolors.ENDC}")
                for idx, elem in enumerate(self.funcs_view_main):
                    print(f"{Bcolors.BOLD}[{idx+1}] - {elem}{Bcolors.ENDC}")
                func = input(" -> ")
                if func.isnumeric():
                    if int(func) in list(range(1, len(self.funcs_view_main)+1)):
                        if int(func) == len(self.funcs_view_main):
                            break
                        else:
                            self.funcs_view_call_main[int(func)]()
                    else:
                        self.print_table(self.all_rows(self.page))
                else:
                    self.print_table(self.all_rows(self.page))
            else:
                while True:
                    print(f"{Bcolors.HEADER} Дії {Bcolors.ENDC}\n{Bcolors.BOLD}[1] - Повернутись{Bcolors.ENDC}")
                    func = input(" -> ")
                    if func.isnumeric():
                        if int(func) == 1:
                            self.find = False
                            break
                self.page = 1
                clear_console()
                self.print_table(self.all_rows(self.page))
        return

    def menu_edit(self):
        self.print_table(self.all_rows(self.page))
        while True:
            print(f"{Bcolors.HEADER} Дії {Bcolors.ENDC}")
            for idx, elem in enumerate(self.funcs_edit_main):
                print(f"{Bcolors.BOLD}[{idx+1}] - {elem}{Bcolors.ENDC}")
            func = input(" -> ")
            if func.isnumeric():
                if int(func) in list(range(1, len(self.funcs_edit_main)+1)):
                    if int(func) == len(self.funcs_edit_main):
                        break
                    else:
                        self.funcs_edit_call_main[int(func)]()
                else:
                    self.print_table(self.all_rows(self.page))
            else:
                self.print_table(self.all_rows(self.page))
        return


class UsersView:
    def __init__(self):
        self.base = Users
        self.columns = self.base.__table__.columns
        self.marsh = UsersMarsh()
        self.page = 1
        self.find = False
        self.funcs_edit_main = ["Змінити нік", "Змінити ПІБ", "Змінити пошту", "Створити", "Видалити",
                                "Вперед", "Назад", "Вихід"]
        self.funcs_edit_call_main = {1: self.edit_by_username, 2: self.edit_by_name, 3: self.edit_by_email,
                                     4: self.new_user, 5: self.delete, 6: self.next, 7: self.back}
        self.funcs_view_main = ["Пошук по ніку", "Пошук по іменю и прізвищу", "Пошук по пошті", "Вперед", "Назад",
                                "Вихід"]
        self.funcs_view_call_main = {1: self.find_by_username, 2: self.find_by_fullname, 3: self.find_by_email,
                                     4: self.next, 5: self.back}

    def table(self):
        t = Table(title=f"{self.base.__tablename__}\n Page: {self.page}")
        for column in self.columns:
            t.add_column(column.name, justify="center")
        return t

    def print_table(self, rows):
        table = self.table()
        for row in rows:
            table.add_row(str(row["id"]), row["username"], row["full_name"],
                          row["email"], row["hashed_password"])
        clear_console()
        rich_print(table)

    def next(self):
        if len(self.all_rows(self.page+1)) > 0:
            self.page += 1
            self.print_table(self.all_rows(self.page))
        else:
            self.print_table(self.all_rows(self.page))

    def back(self):
        if self.page != 1:
            self.page -= 1
        self.print_table(self.all_rows(self.page))

    def all_rows(self, page):
        return self.marsh.dump(session.execute(select(self.base)
                                               .limit(5).offset(5*(page-1))).scalars(), many=True)

    def edit_by_username(self):
        all_users = session.execute(select(self.base)).scalars().all()
        while True:
            idx = input(f"{Bcolors.BOLD}Введіть id -> {Bcolors.ENDC}")
            if idx.isnumeric():
                for elem in all_users:
                    if elem.id == int(idx):
                        while True:
                            new_name = input(f"{Bcolors.BOLD}Новий нік -> {Bcolors.ENDC}")
                            if len(new_name) > 0:
                                check_name = session.execute(select(self.base)
                                                             .where(self.base.username == new_name)).scalars().all()
                                if len(check_name) == 0:
                                    user = session.query(self.base).where(self.base.id == idx).first()
                                    user.username = new_name
                                    session.add(user)
                                    session.commit()
                                    break
                                else:
                                    print(f"{Bcolors.FAIL}Такий нік вже існує{Bcolors.ENDC}")
                            else:
                                print(f"{Bcolors.FAIL}Введіть правильний нік{Bcolors.ENDC}")
                        self.print_table(self.all_rows(1))
                        return
                    elif all_users[-1] == elem:
                        print(f"{Bcolors.FAIL}Такого користувача не існує{Bcolors.ENDC}")
            else:
                print(f"{Bcolors.FAIL}Не правильний id{Bcolors.ENDC}")

    def edit_by_name(self):
        all_users = session.execute(select(self.base)).scalars().all()
        while True:
            idx = input(f"{Bcolors.BOLD}Введіть id -> {Bcolors.ENDC}")
            if idx.isnumeric():
                for elem in all_users:
                    if elem.id == int(idx):
                        while True:
                            new_name = input(f"{Bcolors.BOLD}Новий ПІБ -> {Bcolors.ENDC}")
                            if len(new_name) > 0:
                                user = session.query(self.base).where(self.base.id == idx).first()
                                user.full_name = new_name
                                session.add(user)
                                session.commit()
                                break
                            else:
                                print(f"{Bcolors.FAIL}Введіть правильний ПІБ{Bcolors.ENDC}")
                        self.print_table(self.all_rows(1))
                        return
                    elif all_users[-1] == elem:
                        print(f"{Bcolors.FAIL}Такого користувача не існує{Bcolors.ENDC}")
            else:
                print(f"{Bcolors.FAIL}Не правильний id{Bcolors.ENDC}")

    def edit_by_email(self):
        all_users = session.execute(select(self.base)).scalars().all()
        while True:
            idx = input(f"{Bcolors.BOLD}Введіть id -> {Bcolors.ENDC}")
            if idx.isnumeric():
                for elem in all_users:
                    if elem.id == int(idx):
                        while True:
                            new_name = input(f"{Bcolors.BOLD}Нова пошта -> {Bcolors.ENDC}")
                            if len(new_name) > 0:
                                check_name = session.execute(select(self.base)
                                                             .where(self.base.email == new_name)).scalars().all()
                                if len(check_name) == 0:
                                    user = session.query(self.base).where(self.base.id == idx).first()
                                    user.email = new_name
                                    session.add(user)
                                    session.commit()
                                    break
                                else:
                                    print(f"{Bcolors.FAIL}Така пошта вже існує{Bcolors.ENDC}")
                            else:
                                print(f"{Bcolors.FAIL}Введіть правильну пошту{Bcolors.ENDC}")
                        self.print_table(self.all_rows(1))
                        return
                    elif all_users[-1] == elem:
                        print(f"{Bcolors.FAIL}Такого користувача не існує{Bcolors.ENDC}")
            else:
                print(f"{Bcolors.FAIL}Не правильний id{Bcolors.ENDC}")

    def new_user(self):
        while True:
            username = input(f"{Bcolors.BOLD}Нік -> {Bcolors.ENDC}")
            if len(username) > 0:
                check_username = session.execute(select(self.base)
                                                 .where(self.base.username == username)).scalars().all()
                if len(check_username) == 0:
                    break
                else:
                    print(f"{Bcolors.FAIL}Користувач з таким ніком вже існує{Bcolors.ENDC}")
            else:
                print(f"{Bcolors.FAIL}Введіть правельний нік{Bcolors.ENDC}")
        while True:
            fullname = input(f"{Bcolors.BOLD}ПІБ -> {Bcolors.ENDC}")
            if len(username) > 0:
                break
            else:
                print(f"{Bcolors.FAIL}Введіть правельний ПІБ{Bcolors.ENDC}")
        while True:
            email = input(f"{Bcolors.BOLD}Пошта -> {Bcolors.ENDC}")
            if len(username) > 0:
                check_email = session.execute(select(self.base)
                                              .where(self.base.email == email)).scalars().all()
                if len(check_email) == 0:
                    break
                else:
                    print(f"{Bcolors.FAIL}Користувач з такою поштою вже існує{Bcolors.ENDC}")
            else:
                print(f"{Bcolors.FAIL}Введіть правельну пошту{Bcolors.ENDC}")
        while True:
            password_first = input(f"{Bcolors.BOLD}Введіть пароль -> {Bcolors.ENDC}")
            password_second = input(f"{Bcolors.BOLD}Введіть пароль ще раз -> {Bcolors.ENDC}")
            if password_first == password_second:
                if len(password_first) >= 5:
                    break
                else:
                    print(f"{Bcolors.FAIL}Довжина пароля має бути >= 5{Bcolors.ENDC}")
            else:
                print(f"{Bcolors.FAIL}Паролі не одинакові{Bcolors.ENDC}")
        while True:
            perm = input(f"{Bcolors.BOLD}Адмін (1-так, 0-ні) -> {Bcolors.ENDC}")
            if perm.isnumeric():
                if int(perm) in list(range(0, 2)):
                    perm = bool(perm)
                    break
        salt = uuid4().hex
        hash_password = sha256(salt.encode() + password_first.encode()).hexdigest()
        user = self.base(username=username, full_name=fullname, email=email, hashed_password=hash_password)
        session.add(user)
        session.commit()
        dates = RegDates(user_id=user.id)
        perms = Perm(user_id=user.id, admin=perm)
        salts = Salts(user_id=user.id, salt=salt)
        session.add_all([dates, perms, salts])
        session.commit()
        self.print_table(self.all_rows(1))

    def delete(self):
        all_users = session.execute(select(self.base)).scalars().all()
        while True:
            idx = input(f"{Bcolors.BOLD}Введіть id -> {Bcolors.ENDC}")
            if idx.isnumeric():
                for elem in all_users:
                    if elem.id == int(idx):
                        session.delete(session.query(Perm).where(Perm.user_id == elem.id).first())
                        session.delete(session.query(RegDates).where(RegDates.user_id == elem.id).first())
                        session.delete(session.query(Salts).where(Salts.user_id == elem.id).first())
                        session.delete(elem)
                        session.commit()
                        self.print_table(self.all_rows(1))
                        return
                    elif all_users[-1] == elem:
                        print(f"{Bcolors.FAIL}Такого користувача не існує{Bcolors.ENDC}")
            else:
                print(f"{Bcolors.FAIL}Не правильний id{Bcolors.ENDC}")

    def find_by_username(self):
        username = input(f"{Bcolors.BOLD}Введіть нік -> {Bcolors.ENDC}")
        q = session.execute(select(self.base).where(self.base.username == username)).scalars()
        self.print_table(self.marsh.dump(q, many=True))
        self.find = True

    def find_by_fullname(self):
        fullname = input(f"{Bcolors.BOLD}Введіть ім'я і прізвище -> {Bcolors.ENDC}")
        q = session.execute(select(self.base).where(self.base.full_name == fullname)).scalars()
        self.print_table(self.marsh.dump(q, many=True))
        self.find = True

    def find_by_email(self):
        email = input(f"{Bcolors.BOLD}Введіть пошту -> {Bcolors.ENDC}")
        q = session.execute(select(self.base).where(self.base.email == email)).scalars()
        self.print_table(self.marsh.dump(q, many=True))
        self.find = True

    def menu(self):
        self.print_table(self.all_rows(self.page))
        while True:
            if not self.find:
                print(f"{Bcolors.HEADER} Дії {Bcolors.ENDC}")
                for idx, elem in enumerate(self.funcs_view_main):
                    print(f"{Bcolors.BOLD}[{idx+1}] - {elem}{Bcolors.ENDC}")
                func = input(" -> ")
                if func.isnumeric():
                    if int(func) in list(range(1, len(self.funcs_view_main)+1)):
                        if int(func) == len(self.funcs_view_main):
                            break
                        else:
                            self.funcs_view_call_main[int(func)]()
                    else:
                        self.print_table(self.all_rows(self.page))
                else:
                    self.print_table(self.all_rows(self.page))
            else:
                while True:
                    print(f"{Bcolors.HEADER} Дії {Bcolors.ENDC}\n{Bcolors.BOLD}[1] - Повернутись{Bcolors.ENDC}")
                    func = input(" -> ")
                    if func.isnumeric():
                        if int(func) == 1:
                            self.find = False
                            break
                self.page = 1
                clear_console()
                self.print_table(self.all_rows(self.page))
        return

    def menu_edit(self):
        self.print_table(self.all_rows(self.page))
        while True:
            print(f"{Bcolors.HEADER} Дії {Bcolors.ENDC}")
            for idx, elem in enumerate(self.funcs_edit_main):
                print(f"{Bcolors.BOLD}[{idx+1}] - {elem}{Bcolors.ENDC}")
            func = input(" -> ")
            if func.isnumeric():
                if int(func) in list(range(1, len(self.funcs_edit_main)+1)):
                    if int(func) == len(self.funcs_edit_main):
                        break
                    else:
                        self.funcs_edit_call_main[int(func)]()
                else:
                    self.print_table(self.all_rows(self.page))
            else:
                self.print_table(self.all_rows(self.page))
        return


class CategoryView:
    def __init__(self):
        self.base = Category
        self.columns = self.base.__table__.columns
        self.marsh = CategoryMarsh()
        self.page = 1
        self.find = False
        self.funcs_edit_main = ["Зміна назви", "Видалити", "Створити", "Вперед", "Назад", "Вихід"]
        self.funcs_edit_call_main = {1: self.edit_by_name, 2: self.delete, 3: self.new_category,
                                     4: self.next, 5: self.back}
        self.funcs_view_main = ["Пошук по імені", "Вперед", "Назад", "Вихід"]
        self.funcs_view_call_main = {1: self.find_by_name, 2: self.next, 3: self.back}

    def table(self):
        t = Table(title=f"{self.base.__tablename__}\n Page: {self.page}")
        for column in self.columns:
            t.add_column(column.name, justify="center")
        return t

    def print_table(self, rows):
        table = self.table()
        for row in rows:
            table.add_row(str(row["id"]), row["name"])
        clear_console()
        rich_print(table)

    def next(self):
        if len(self.all_rows(self.page+1)) > 0:
            self.page += 1
            self.print_table(self.all_rows(self.page))
        else:
            self.print_table(self.all_rows(self.page))

    def back(self):
        if self.page != 1:
            self.page -= 1
        self.print_table(self.all_rows(self.page))

    def all_rows(self, page):
        return self.marsh.dump(session.execute(select(self.base)
                                               .limit(5).offset(5*(page-1))).scalars(), many=True)

    def edit_by_name(self):
        all_category = session.execute(select(self.base)).scalars().all()
        while True:
            idx = input(f"{Bcolors.BOLD}Введіть id -> {Bcolors.ENDC}")
            if idx.isnumeric():
                for elem in all_category:
                    if elem.id == int(idx):
                        while True:
                            new_name = input(f"{Bcolors.BOLD}Нова назва -> {Bcolors.ENDC}")
                            if len(new_name) > 0:
                                category = session.query(self.base).where(self.base.id == idx).first()
                                category.name = new_name
                                session.add(category)
                                session.commit()
                                break
                            else:
                                print(f"{Bcolors.FAIL}Введіть правельну назву{Bcolors.ENDC}")
                        self.print_table(self.all_rows(1))
                        return
                    elif all_category[-1] == elem:
                        print(f"{Bcolors.FAIL}Такої категорії не існує{Bcolors.ENDC}")
            else:
                print(f"{Bcolors.FAIL}Не правильний id{Bcolors.ENDC}")

    def delete(self):
        all_category = session.execute(select(self.base)).scalars().all()
        while True:
            idx = input(f"{Bcolors.BOLD}Введіть id -> {Bcolors.ENDC}")
            if idx.isnumeric():
                for elem in all_category:
                    if elem.id == int(idx):
                        all_films = session.execute(select(Film).where(Film.category_id == elem.id)).scalars()
                        for film in all_films:
                            session.delete(session.query(Dates).where(Dates.film_id == film.id).first())
                            session.delete(session.query(Sales).where(Sales.film_id == film.id).first())
                            session.delete(film)
                        session.delete(elem)
                        session.commit()
                        self.print_table(self.all_rows(1))
                        return
                    elif all_category[-1] == elem:
                        print(f"{Bcolors.FAIL}Такої категорії не існує{Bcolors.ENDC}")
            else:
                print(f"{Bcolors.FAIL}Не правильний id{Bcolors.ENDC}")

    def new_category(self):
        while True:
            name = input(f"{Bcolors.BOLD}Назва -> {Bcolors.ENDC}")
            if len(name) > 0:
                break
            else:
                print(f"{Bcolors.FAIL}Введіть правельну назву{Bcolors.ENDC}")
        category = self.base(name=name)
        session.add(category)
        session.commit()
        self.print_table(self.all_rows(1))

    def find_by_name(self):
        name = input(f"{Bcolors.BOLD}Введіть ім'я -> {Bcolors.ENDC}")
        q = session.execute(select(self.base).where(self.base.name == name)).scalars()
        self.print_table(self.marsh.dump(q, many=True))
        self.find = True

    def menu(self):
        self.print_table(self.all_rows(self.page))
        while True:
            if not self.find:
                print(f"{Bcolors.HEADER} Дії {Bcolors.ENDC}")
                for idx, elem in enumerate(self.funcs_view_main):
                    print(f"{Bcolors.BOLD}[{idx+1}] - {elem}{Bcolors.ENDC}")
                func = input(" -> ")
                if func.isnumeric():
                    if int(func) in list(range(1, len(self.funcs_view_main)+1)):
                        if int(func) == len(self.funcs_view_main):
                            break
                        else:
                            self.funcs_view_call_main[int(func)]()
                    else:
                        self.print_table(self.all_rows(self.page))
                else:
                    self.print_table(self.all_rows(self.page))
            else:
                while True:
                    print(f"{Bcolors.HEADER} Дії {Bcolors.ENDC}\n{Bcolors.BOLD}[1] - Повернутись{Bcolors.ENDC}")
                    func = input(" -> ")
                    if func.isnumeric():
                        if int(func) == 1:
                            self.find = False
                            break
                self.page = 1
                clear_console()
                self.print_table(self.all_rows(self.page))
        return

    def menu_edit(self):
        self.print_table(self.all_rows(self.page))
        while True:
            print(f"{Bcolors.HEADER} Дії {Bcolors.ENDC}")
            for idx, elem in enumerate(self.funcs_edit_main):
                print(f"{Bcolors.BOLD}[{idx+1}] - {elem}{Bcolors.ENDC}")
            func = input(" -> ")
            if func.isnumeric():
                if int(func) in list(range(1, len(self.funcs_edit_main)+1)):
                    if int(func) == len(self.funcs_edit_main):
                        break
                    else:
                        self.funcs_edit_call_main[int(func)]()
                else:
                    self.print_table(self.all_rows(self.page))
            else:
                self.print_table(self.all_rows(self.page))
        return


class SalesView:
    def __init__(self):
        self.base = Sales
        self.columns = self.base.__table__.columns
        self.marsh = SalesMarsh()
        self.page = 1
        self.find = False
        self.funcs_edit_main = ["Змінити ціну", "Змінити кількість людей", "Видалити", "Вперед", "Назад", "Вихід"]
        self.funcs_edit_call_main = {1: self.edit_by_price, 2: self.edit_by_peoples, 3: self.delete,
                                     4: self.next, 5: self.back}
        self.funcs_view_main = ["Пошук по фільму", "Пошук по кількості людей", "Вперед", "Назад", "Вихід"]
        self.funcs_view_call_main = {1: self.find_by_film, 2: self.find_by_peoples, 3: self.next, 4: self.back}

    def table(self):
        t = Table(title=f"{self.base.__tablename__}\n Page: {self.page}")
        for column in self.columns:
            t.add_column(column.name, justify="center")
        return t

    def print_table(self, rows):
        table = self.table()
        for row in rows:
            table.add_row(str(row["id"]), str(row["film_id"]), str(row["peoples"]), str(row["ticket_price"]))
        clear_console()
        rich_print(table)

    def next(self):
        if len(self.all_rows(self.page+1)) > 0:
            self.page += 1
            self.print_table(self.all_rows(self.page))
        else:
            self.print_table(self.all_rows(self.page))

    def back(self):
        if self.page != 1:
            self.page -= 1
        self.print_table(self.all_rows(self.page))

    def all_rows(self, page):
        return self.marsh.dump(session.execute(select(self.base)
                                               .limit(5).offset(5*(page-1))).scalars(), many=True)

    def edit_by_price(self):
        all_sales = session.execute(select(self.base)).scalars().all()
        while True:
            idx = input(f"{Bcolors.BOLD}Введіть id -> {Bcolors.ENDC}")
            if idx.isnumeric():
                for elem in all_sales:
                    if elem.id == int(idx):
                        while True:
                            new_price = input(f"{Bcolors.BOLD}Нова ціна -> {Bcolors.ENDC}")
                            if new_price.isnumeric():
                                sales = session.query(self.base).where(self.base.id == idx).first()
                                sales.ticket_price = int(new_price)
                                session.add(sales)
                                session.commit()
                                break
                            else:
                                print(f"{Bcolors.FAIL}Введіть правельну ціну{Bcolors.ENDC}")
                        self.print_table(self.all_rows(1))
                        return
                    elif all_sales[-1] == elem:
                        print(f"{Bcolors.FAIL}Таких продажів не існує{Bcolors.ENDC}")
            else:
                print(f"{Bcolors.FAIL}Не правильний id{Bcolors.ENDC}")

    def edit_by_peoples(self):
        all_sales = session.execute(select(self.base)).scalars().all()
        while True:
            idx = input(f"{Bcolors.BOLD}Введіть id -> {Bcolors.ENDC}")
            if idx.isnumeric():
                for elem in all_sales:
                    if elem.id == int(idx):
                        while True:
                            new_peoples = input(f"{Bcolors.BOLD}Нова кількість людей -> {Bcolors.ENDC}")
                            if new_peoples.isnumeric():
                                sales = session.query(self.base).where(self.base.id == idx).first()
                                sales.peoples = int(new_peoples)
                                session.add(sales)
                                session.commit()
                                break
                            else:
                                print(f"{Bcolors.FAIL}Введіть правельну кількість людей{Bcolors.ENDC}")
                        self.print_table(self.all_rows(1))
                        return
                    elif all_sales[-1] == elem:
                        print(f"{Bcolors.FAIL}Таких продажів не існує{Bcolors.ENDC}")
            else:
                print(f"{Bcolors.FAIL}Не правильний id{Bcolors.ENDC}")

    def delete(self):
        all_sales = session.execute(select(self.base)).scalars().all()
        while True:
            idx = input(f"{Bcolors.BOLD}Введіть id -> {Bcolors.ENDC}")
            if idx.isnumeric():
                for elem in all_sales:
                    if elem.id == int(idx):
                        film = session.query(Film).where(Film.id == elem.film_id).first()
                        session.delete(session.query(Dates).where(Dates.film_id == film.id).first())
                        session.delete(elem)
                        session.delete(film)
                        session.commit()
                        self.print_table(self.all_rows(1))
                        return
                    elif all_sales[-1] == elem:
                        print(f"{Bcolors.FAIL}Такої продажі не існує{Bcolors.ENDC}")
            else:
                print(f"{Bcolors.FAIL}Не правильний id{Bcolors.ENDC}")

    def find_by_film(self):
        all_films = session.execute(select(Film)).scalars().all()
        count = 0
        m = f"{Bcolors.HEADER}Фільми:\n{Bcolors.ENDC}"
        for elem in all_films:
            count += 1
            m += f"{Bcolors.BOLD}{elem.name}{Bcolors.ENDC} "
            if count == 5:
                m += "\n"
        clear_console()
        print(m)
        film = input(f"{Bcolors.BOLD}Введіть фільм -> {Bcolors.ENDC}")
        ans = -1
        for elem in all_films:
            if elem.name == film:
                ans = elem.id
        q = session.execute(select(self.base).where(self.base.film_id == ans)).scalars()
        self.print_table(self.marsh.dump(q, many=True))
        self.find = True

    def find_by_peoples(self):
        min_num = input(f"{Bcolors.BOLD}Введіть меньше число -> {Bcolors.ENDC}")
        max_num = input(f"{Bcolors.BOLD}Введіть більше число -> {Bcolors.ENDC}")
        q = session.execute(select(self.base).where(self.base.peoples.between(min_num, max_num))).scalars()
        self.print_table(self.marsh.dump(q, many=True))
        self.find = True

    def menu(self):
        self.print_table(self.all_rows(self.page))
        while True:
            if not self.find:
                print(f"{Bcolors.HEADER} Дії {Bcolors.ENDC}")
                for idx, elem in enumerate(self.funcs_view_main):
                    print(f"{Bcolors.BOLD}[{idx+1}] - {elem}{Bcolors.ENDC}")
                func = input(" -> ")
                if func.isnumeric():
                    if int(func) in list(range(1, len(self.funcs_view_main)+1)):
                        if int(func) == len(self.funcs_view_main):
                            break
                        else:
                            self.funcs_view_call_main[int(func)]()
                    else:
                        self.print_table(self.all_rows(self.page))
                else:
                    self.print_table(self.all_rows(self.page))
            else:
                while True:
                    print(f"{Bcolors.HEADER} Дії {Bcolors.ENDC}\n{Bcolors.BOLD}[1] - Повернутись{Bcolors.ENDC}")
                    func = input(" -> ")
                    if func.isnumeric():
                        if int(func) == 1:
                            self.find = False
                            break
                self.page = 1
                clear_console()
                self.print_table(self.all_rows(self.page))
        return

    def menu_edit(self):
        self.print_table(self.all_rows(self.page))
        while True:
            print(f"{Bcolors.HEADER} Дії {Bcolors.ENDC}")
            for idx, elem in enumerate(self.funcs_edit_main):
                print(f"{Bcolors.BOLD}[{idx+1}] - {elem}{Bcolors.ENDC}")
            func = input(" -> ")
            if func.isnumeric():
                if int(func) in list(range(1, len(self.funcs_edit_main)+1)):
                    if int(func) == len(self.funcs_edit_main):
                        break
                    else:
                        self.funcs_edit_call_main[int(func)]()
                else:
                    self.print_table(self.all_rows(self.page))
            else:
                self.print_table(self.all_rows(self.page))
        return


class FilmDateView:
    def __init__(self):
        self.base = Dates
        self.columns = self.base.__table__.columns
        self.marsh = DatesMarsh()
        self.page = 1
        self.find = False
        self.funcs_edit_main = ["Змінити початкову дату", "Змінити кінцеву дату", "Видалити",
                                "Вперед", "Назад", "Вихід"]
        self.funcs_edit_call_main = {1: self.edit_by_start, 2: self.edit_by_end, 3: self.delete,
                                     4: self.next, 5: self.back}
        self.funcs_view_main = ["Пошук по фільму", "Пошук по даті початку", "Пошук по даті кінця",
                                "Вперед", "Назад", "Вихід"]
        self.funcs_view_call_main = {1: self.find_by_film, 2: self.find_by_start, 3: self.find_by_end,
                                     4: self.next, 5: self.back}

    def table(self):
        t = Table(title=f"{self.base.__tablename__}\n Page: {self.page}")
        for column in self.columns:
            t.add_column(column.name, justify="center")
        return t

    def print_table(self, rows):
        table = self.table()
        for row in rows:
            table.add_row(str(row["id"]), str(row["film_id"]), f'{row["start_date"]}', f'{row["end_date"]}')
        clear_console()
        rich_print(table)

    def next(self):
        if len(self.all_rows(self.page+1)) > 0:
            self.page += 1
            self.print_table(self.all_rows(self.page))
        else:
            self.print_table(self.all_rows(self.page))

    def back(self):
        if self.page != 1:
            self.page -= 1
        self.print_table(self.all_rows(self.page))

    def all_rows(self, page):
        return self.marsh.dump(session.execute(select(self.base)
                                               .limit(5).offset(5*(page-1))).scalars(), many=True)

    def edit_by_start(self):
        all_dates = session.execute(select(self.base)).scalars().all()
        while True:
            idx = input(f"{Bcolors.BOLD}Введіть id -> {Bcolors.ENDC}")
            if idx.isnumeric():
                for elem in all_dates:
                    if elem.id == int(idx):
                        print(f"{Bcolors.HEADER}Дата початку показу{Bcolors.ENDC}")
                        year = input(f"{Bcolors.BOLD}Рік -> {Bcolors.ENDC}")
                        if year.isnumeric():
                            year = int(year)
                            month = input(f"{Bcolors.BOLD}Місяць -> {Bcolors.ENDC}")
                            if month.isnumeric():
                                month = int(month)
                                if month in list(range(1, 13)):
                                    day = input(f"{Bcolors.BOLD}День -> {Bcolors.ENDC}")
                                    if day.isnumeric():
                                        day = int(day)
                                        if day in list(range(1, 32)):
                                            st_date = dt.date(year, month, day)
                                            elem.start_date = st_date
                                            session.add(elem)
                                            session.commit()
                                            self.print_table(self.all_rows(1))
                                            return
                                        else:
                                            print(f"{Bcolors.FAIL}Не правильний день{Bcolors.ENDC}")
                                    else:
                                        print(f"{Bcolors.FAIL}Не правильний день{Bcolors.ENDC}")
                                else:
                                    print(f"{Bcolors.FAIL}Не правильний місяць{Bcolors.ENDC}")
                            else:
                                print(f"{Bcolors.FAIL}Не правильний місяць{Bcolors.ENDC}")
                        else:
                            print(f"{Bcolors.FAIL}Не правильний рік{Bcolors.ENDC}")
                    elif all_dates[-1] == elem:
                        print(f"{Bcolors.FAIL}Такої дати фільму не існує{Bcolors.ENDC}")
            else:
                print(f"{Bcolors.FAIL}Не правильний id{Bcolors.ENDC}")

    def edit_by_end(self):
        all_dates = session.execute(select(self.base)).scalars().all()
        while True:
            idx = input(f"{Bcolors.BOLD}Введіть id -> {Bcolors.ENDC}")
            if idx.isnumeric():
                for elem in all_dates:
                    if elem.id == int(idx):
                        print(f"{Bcolors.HEADER}Дата кінця показу{Bcolors.ENDC}")
                        year = input(f"{Bcolors.BOLD}Рік -> {Bcolors.ENDC}")
                        if year.isnumeric():
                            year = int(year)
                            month = input(f"{Bcolors.BOLD}Місяць -> {Bcolors.ENDC}")
                            if month.isnumeric():
                                month = int(month)
                                if month in list(range(1, 13)):
                                    day = input(f"{Bcolors.BOLD}День -> {Bcolors.ENDC}")
                                    if day.isnumeric():
                                        day = int(day)
                                        if day in list(range(1, 32)):
                                            end_date = dt.date(year, month, day)
                                            elem.end_date = end_date
                                            session.add(elem)
                                            session.commit()
                                            self.print_table(self.all_rows(1))
                                            return
                                        else:
                                            print(f"{Bcolors.FAIL}Не правильний день{Bcolors.ENDC}")
                                    else:
                                        print(f"{Bcolors.FAIL}Не правильний день{Bcolors.ENDC}")
                                else:
                                    print(f"{Bcolors.FAIL}Не правильний місяць{Bcolors.ENDC}")
                            else:
                                print(f"{Bcolors.FAIL}Не правильний місяць{Bcolors.ENDC}")
                        else:
                            print(f"{Bcolors.FAIL}Не правильний рік{Bcolors.ENDC}")
                    elif all_dates[-1] == elem:
                        print(f"{Bcolors.FAIL}Такої дати фільму не існує{Bcolors.ENDC}")
            else:
                print(f"{Bcolors.FAIL}Не правильний id{Bcolors.ENDC}")

    def delete(self):
        all_dates = session.execute(select(self.base)).scalars().all()
        while True:
            idx = input(f"{Bcolors.BOLD}Введіть id -> {Bcolors.ENDC}")
            if idx.isnumeric():
                for elem in all_dates:
                    if elem.id == int(idx):
                        film = session.query(Film).where(Film.id == elem.film_id).first()
                        session.delete(session.query(Sales).where(Dates.film_id == film.id).first())
                        session.delete(elem)
                        session.delete(film)
                        session.commit()
                        self.print_table(self.all_rows(1))
                        return
                    elif all_dates[-1] == elem:
                        print(f"{Bcolors.FAIL}Такої дати фільму не існує{Bcolors.ENDC}")
            else:
                print(f"{Bcolors.FAIL}Не правильний id{Bcolors.ENDC}")

    def find_by_film(self):
        all_films = session.execute(select(Film)).scalars().all()
        count = 0
        m = f"{Bcolors.HEADER}Фільми:\n{Bcolors.ENDC}"
        for elem in all_films:
            count += 1
            m += f"{Bcolors.BOLD}{elem.name}{Bcolors.ENDC} "
            if count == 5:
                m += "\n"
        clear_console()
        print(m)
        film = input(f"{Bcolors.BOLD}Введіть фільм -> {Bcolors.ENDC}")
        ans = -1
        for elem in all_films:
            if elem.name == film:
                ans = elem.id
        q = session.execute(select(self.base).where(self.base.film_id == ans)).scalars()
        self.print_table(self.marsh.dump(q, many=True))
        self.find = True

    def find_by_start(self):
        print(f"{Bcolors.FAIL}Вводити такого типу -> 2021-07-25{Bcolors.ENDC}")
        min_date = input(f"{Bcolors.BOLD}Введіть першу дату -> {Bcolors.ENDC}")
        max_date = input(f"{Bcolors.BOLD}Введіть другу дату -> {Bcolors.ENDC}")
        q = session.execute(select(self.base).where(self.base.start_date.between(min_date, max_date))).scalars()
        self.print_table(self.marsh.dump(q, many=True))
        self.find = True

    def find_by_end(self):
        print(f"{Bcolors.FAIL}Вводити такого типу -> 2021-07-25{Bcolors.ENDC}")
        min_date = input(f"{Bcolors.BOLD}Введіть першу дату -> {Bcolors.ENDC}")
        max_date = input(f"{Bcolors.BOLD}Введіть другу дату -> {Bcolors.ENDC}")
        q = session.execute(select(self.base).where(self.base.end_date.between(min_date, max_date))).scalars()
        self.print_table(self.marsh.dump(q, many=True))
        self.find = True

    def menu(self):
        self.print_table(self.all_rows(self.page))
        while True:
            if not self.find:
                print(f"{Bcolors.HEADER} Дії {Bcolors.ENDC}")
                for idx, elem in enumerate(self.funcs_view_main):
                    print(f"{Bcolors.BOLD}[{idx+1}] - {elem}{Bcolors.ENDC}")
                func = input(" -> ")
                if func.isnumeric():
                    if int(func) in list(range(1, len(self.funcs_view_main)+1)):
                        if int(func) == len(self.funcs_view_main):
                            break
                        else:
                            self.funcs_view_call_main[int(func)]()
                    else:
                        self.print_table(self.all_rows(self.page))
                else:
                    self.print_table(self.all_rows(self.page))
            else:
                while True:
                    print(f"{Bcolors.HEADER} Дії {Bcolors.ENDC}\n{Bcolors.BOLD}[1] - Повернутись{Bcolors.ENDC}")
                    func = input(" -> ")
                    if func.isnumeric():
                        if int(func) == 1:
                            self.find = False
                            break
                self.page = 1
                clear_console()
                self.print_table(self.all_rows(self.page))
        return

    def menu_edit(self):
        self.print_table(self.all_rows(self.page))
        while True:
            print(f"{Bcolors.HEADER} Дії {Bcolors.ENDC}")
            for idx, elem in enumerate(self.funcs_edit_main):
                print(f"{Bcolors.BOLD}[{idx+1}] - {elem}{Bcolors.ENDC}")
            func = input(" -> ")
            if func.isnumeric():
                if int(func) in list(range(1, len(self.funcs_edit_main)+1)):
                    if int(func) == len(self.funcs_edit_main):
                        break
                    else:
                        self.funcs_edit_call_main[int(func)]()
                else:
                    self.print_table(self.all_rows(self.page))
            else:
                self.print_table(self.all_rows(self.page))
        return


class SaltsView:
    def __init__(self):
        self.base = Salts
        self.columns = self.base.__table__.columns
        self.marsh = SaltsMarsh()
        self.page = 1
        self.find = False
        self.funcs_edit_main = ["Видалити", "Вперед", "Назад", "Вихід"]
        self.funcs_edit_call_main = {1: self.delete, 2: self.next, 3: self.back}
        self.funcs_view_main = ["Пошук по ніку", "Вперед", "Назад", "Вихід"]
        self.funcs_view_call_main = {1: self.find_by_username, 2: self.next, 3: self.back}

    def table(self):
        t = Table(title=f"{self.base.__tablename__}\n Page: {self.page}")
        for column in self.columns:
            t.add_column(column.name, justify="center")
        return t

    def print_table(self, rows):
        table = self.table()
        for row in rows:
            table.add_row(str(row["id"]), str(row["user_id"]), row["salt"])
        clear_console()
        rich_print(table)

    def next(self):
        if len(self.all_rows(self.page+1)) > 0:
            self.page += 1
            self.print_table(self.all_rows(self.page))
        else:
            self.print_table(self.all_rows(self.page))

    def back(self):
        if self.page != 1:
            self.page -= 1
        self.print_table(self.all_rows(self.page))

    def all_rows(self, page):
        return self.marsh.dump(session.execute(select(self.base)
                                               .limit(5).offset(5*(page-1))).scalars(), many=True)

    def delete(self):
        all_salts = session.execute(select(self.base)).scalars().all()
        while True:
            idx = input(f"{Bcolors.BOLD}Введіть id -> {Bcolors.ENDC}")
            if idx.isnumeric():
                for elem in all_salts:
                    if elem.id == int(idx):
                        session.delete(session.query(Perm).where(Perm.user_id == elem.user_id).first())
                        session.delete(session.query(RegDates).where(RegDates.user_id == elem.user_id).first())
                        session.delete(session.query(Users).where(Users.id == elem.user_id).first())
                        session.delete(elem)
                        session.commit()
                        self.print_table(self.all_rows(1))
                        return
                    elif all_salts[-1] == elem:
                        print(f"{Bcolors.FAIL}Такого користувача не існує{Bcolors.ENDC}")
            else:
                print(f"{Bcolors.FAIL}Не правильний id{Bcolors.ENDC}")

    def find_by_username(self):
        clear_console()
        all_users = session.execute(select(Users)).scalars().all()
        username = input(f"{Bcolors.BOLD}Введіть нік -> {Bcolors.ENDC}")
        ans = -1
        for elem in all_users:
            if elem.username == username:
                ans = elem.id
        q = session.execute(select(self.base).where(self.base.user_id == ans)).scalars()
        self.print_table(self.marsh.dump(q, many=True))
        self.find = True

    def menu(self):
        self.print_table(self.all_rows(self.page))
        while True:
            if not self.find:
                print(f"{Bcolors.HEADER} Дії {Bcolors.ENDC}")
                for idx, elem in enumerate(self.funcs_view_main):
                    print(f"{Bcolors.BOLD}[{idx+1}] - {elem}{Bcolors.ENDC}")
                func = input(" -> ")
                if func.isnumeric():
                    if int(func) in list(range(1, len(self.funcs_view_main)+1)):
                        if int(func) == len(self.funcs_view_main):
                            break
                        else:
                            self.funcs_view_call_main[int(func)]()
                    else:
                        self.print_table(self.all_rows(self.page))
                else:
                    self.print_table(self.all_rows(self.page))
            else:
                while True:
                    print(f"{Bcolors.HEADER} Дії {Bcolors.ENDC}\n{Bcolors.BOLD}[1] - Повернутись{Bcolors.ENDC}")
                    func = input(" -> ")
                    if func.isnumeric():
                        if int(func) == 1:
                            self.find = False
                            break
                self.page = 1
                clear_console()
                self.print_table(self.all_rows(self.page))
        return

    def menu_edit(self):
        self.print_table(self.all_rows(self.page))
        while True:
            print(f"{Bcolors.HEADER} Дії {Bcolors.ENDC}")
            for idx, elem in enumerate(self.funcs_edit_main):
                print(f"{Bcolors.BOLD}[{idx+1}] - {elem}{Bcolors.ENDC}")
            func = input(" -> ")
            if func.isnumeric():
                if int(func) in list(range(1, len(self.funcs_edit_main)+1)):
                    if int(func) == len(self.funcs_edit_main):
                        break
                    else:
                        self.funcs_edit_call_main[int(func)]()
                else:
                    self.print_table(self.all_rows(self.page))
            else:
                self.print_table(self.all_rows(self.page))
        return


class PermView:
    def __init__(self):
        self.base = Perm
        self.columns = self.base.__table__.columns
        self.marsh = PermMarsh()
        self.page = 1
        self.find = False
        self.funcs_edit_main = ["Змінити права", "Видалити", "Вперед", "Назад", "Вихід"]
        self.funcs_edit_call_main = {1: self.edit_by_admin, 2: self.delete, 3: self.next, 4: self.back}
        self.funcs_view_main = ["Пошук по ніку", "Адміни", "Користувачі", "Вперед", "Назад", "Вихід"]
        self.funcs_view_call_main = {1: self.find_by_username, 2: self.find_by_admin, 3: self.find_by_user,
                                     4: self.next, 5: self.back}

    def table(self):
        t = Table(title=f"{self.base.__tablename__}\n Page: {self.page}")
        for column in self.columns:
            t.add_column(column.name, justify="center")
        return t

    def print_table(self, rows):
        table = self.table()
        for row in rows:
            table.add_row(str(row["id"]), str(row["user_id"]), f"{row['admin']}")
        clear_console()
        rich_print(table)

    def next(self):
        if len(self.all_rows(self.page+1)) > 0:
            self.page += 1
            self.print_table(self.all_rows(self.page))
        else:
            self.print_table(self.all_rows(self.page))

    def back(self):
        if self.page != 1:
            self.page -= 1
        self.print_table(self.all_rows(self.page))

    def all_rows(self, page):
        return self.marsh.dump(session.execute(select(self.base)
                                               .limit(5).offset(5*(page-1))).scalars(), many=True)

    def delete(self):
        all_perms = session.execute(select(self.base)).scalars().all()
        while True:
            idx = input(f"{Bcolors.BOLD}Введіть id -> {Bcolors.ENDC}")
            if idx.isnumeric():
                for elem in all_perms:
                    if elem.id == int(idx):
                        session.delete(session.query(Salts).where(Salts.user_id == elem.user_id).first())
                        session.delete(session.query(RegDates).where(RegDates.user_id == elem.user_id).first())
                        session.delete(session.query(Users).where(Users.id == elem.user_id).first())
                        session.delete(elem)
                        session.commit()
                        self.print_table(self.all_rows(1))
                        return
                    elif all_perms[-1] == elem:
                        print(f"{Bcolors.FAIL}Таких ключів не існує{Bcolors.ENDC}")
            else:
                print(f"{Bcolors.FAIL}Не правильний id{Bcolors.ENDC}")

    def edit_by_admin(self):
        all_perms = session.execute(select(self.base)).scalars().all()
        while True:
            idx = input(f"{Bcolors.BOLD}Введіть id -> {Bcolors.ENDC}")
            if idx.isnumeric():
                for elem in all_perms:
                    if elem.id == int(idx):
                        while True:
                            new_perm = input(f"{Bcolors.BOLD}Нові права (1-адмін, 0-користувач) -> {Bcolors.ENDC}")
                            if new_perm.isnumeric():
                                if int(new_perm) in list(range(0, 2)):
                                    perm = session.query(self.base).where(self.base.id == idx).first()
                                    perm.admin = int(new_perm)
                                    session.add(perm)
                                    session.commit()
                                    self.print_table(self.all_rows(1))
                                    return
                                else:
                                    print(f"{Bcolors.FAIL}Введіть правельну цифру{Bcolors.ENDC}")
                            else:
                                print(f"{Bcolors.FAIL}Введіть правельну цифру{Bcolors.ENDC}")
                    elif all_perms[-1] == elem:
                        print(f"{Bcolors.FAIL}Таких ключів не існує{Bcolors.ENDC}")
            else:
                print(f"{Bcolors.FAIL}Не правильний id{Bcolors.ENDC}")

    def find_by_username(self):
        clear_console()
        all_users = session.execute(select(Users)).scalars().all()
        username = input(f"{Bcolors.BOLD}Введіть нік -> {Bcolors.ENDC}")
        ans = -1
        for elem in all_users:
            if elem.username == username:
                ans = elem.id
        q = session.execute(select(self.base).where(self.base.user_id == ans)).scalars()
        self.print_table(self.marsh.dump(q, many=True))
        self.find = True

    def find_by_admin(self):
        q = session.execute(select(self.base).where(self.base.admin == 1)).scalars()
        self.print_table(self.marsh.dump(q, many=True))
        self.find = True

    def find_by_user(self):
        q = session.execute(select(self.base).where(self.base.admin == 0)).scalars()
        self.print_table(self.marsh.dump(q, many=True))
        self.find = True

    def menu(self):
        self.print_table(self.all_rows(self.page))
        while True:
            if not self.find:
                print(f"{Bcolors.HEADER} Дії {Bcolors.ENDC}")
                for idx, elem in enumerate(self.funcs_view_main):
                    print(f"{Bcolors.BOLD}[{idx+1}] - {elem}{Bcolors.ENDC}")
                func = input(" -> ")
                if func.isnumeric():
                    if int(func) in list(range(1, len(self.funcs_view_main)+1)):
                        if int(func) == len(self.funcs_view_main):
                            break
                        else:
                            self.funcs_view_call_main[int(func)]()
                    else:
                        self.print_table(self.all_rows(self.page))
                else:
                    self.print_table(self.all_rows(self.page))
            else:
                while True:
                    print(f"{Bcolors.HEADER} Дії {Bcolors.ENDC}\n{Bcolors.BOLD}[1] - Повернутись{Bcolors.ENDC}")
                    func = input(" -> ")
                    if func.isnumeric():
                        if int(func) == 1:
                            self.find = False
                            break
                self.page = 1
                clear_console()
                self.print_table(self.all_rows(self.page))
        return

    def menu_edit(self):
        self.print_table(self.all_rows(self.page))
        while True:
            print(f"{Bcolors.HEADER} Дії {Bcolors.ENDC}")
            for idx, elem in enumerate(self.funcs_edit_main):
                print(f"{Bcolors.BOLD}[{idx+1}] - {elem}{Bcolors.ENDC}")
            func = input(" -> ")
            if func.isnumeric():
                if int(func) in list(range(1, len(self.funcs_edit_main)+1)):
                    if int(func) == len(self.funcs_edit_main):
                        break
                    else:
                        self.funcs_edit_call_main[int(func)]()
                else:
                    self.print_table(self.all_rows(self.page))
            else:
                self.print_table(self.all_rows(self.page))
        return


class RegDateView:
    def __init__(self):
        self.base = RegDates
        self.columns = self.base.__table__.columns
        self.marsh = RegDatesMarsh()
        self.page = 1
        self.find = False
        self.funcs_edit_main = ["Видалити", "Вперед", "Назад", "Вихід"]
        self.funcs_edit_call_main = {1: self.delete}
        self.funcs_view_main = ["Пошук по ніку", "Пошук по реєстрації", "Пошук по активності",
                                "Вперед", "Назад", "Вихід"]
        self.funcs_view_call_main = {1: self.find_by_username, 2: self.find_by_reg, 3: self.find_by_activity,
                                     4: self.next, 5: self.back}

    def table(self):
        t = Table(title=f"{self.base.__tablename__}\n Page: {self.page}")
        for column in self.columns:
            t.add_column(column.name, justify="center")
        return t

    def print_table(self, rows):
        table = self.table()
        for row in rows:
            table.add_row(str(row["id"]), str(row["user_id"]), f"{row['reg_date']}", f"{row['last_activity']}")
        clear_console()
        rich_print(table)

    def next(self):
        if len(self.all_rows(self.page+1)) > 0:
            self.page += 1
            self.print_table(self.all_rows(self.page))
        else:
            self.print_table(self.all_rows(self.page))

    def back(self):
        if self.page != 1:
            self.page -= 1
        self.print_table(self.all_rows(self.page))

    def all_rows(self, page):
        return self.marsh.dump(session.execute(select(self.base)
                                               .limit(5).offset(5*(page-1))).scalars(), many=True)

    def delete(self):
        all_dates = session.execute(select(self.base)).scalars().all()
        while True:
            idx = input(f"{Bcolors.BOLD}Введіть id -> {Bcolors.ENDC}")
            if idx.isnumeric():
                for elem in all_dates:
                    if elem.id == int(idx):
                        session.delete(session.query(Salts).where(Salts.user_id == elem.user_id).first())
                        session.delete(session.query(Perm).where(Perm.user_id == elem.user_id).first())
                        session.delete(session.query(Users).where(Users.id == elem.user_id).first())
                        session.delete(elem)
                        session.commit()
                        self.print_table(self.all_rows(1))
                        return
                    elif all_dates[-1] == elem:
                        print(f"{Bcolors.FAIL}Таких ключів не існує{Bcolors.ENDC}")
            else:
                print(f"{Bcolors.FAIL}Не правильний id{Bcolors.ENDC}")

    def find_by_username(self):
        clear_console()
        all_users = session.execute(select(Users)).scalars().all()
        username = input(f"{Bcolors.BOLD}Введіть нік -> {Bcolors.ENDC}")
        ans = -1
        for elem in all_users:
            if elem.username == username:
                ans = elem.id
        q = session.execute(select(self.base).where(self.base.user_id == ans)).scalars()
        self.print_table(self.marsh.dump(q, many=True))
        self.find = True

    def find_by_reg(self):
        print(f"{Bcolors.FAIL}Вводити такого типу -> 2021-07-25{Bcolors.ENDC}")
        min_date = input(f"{Bcolors.BOLD}Введіть першу дату -> {Bcolors.ENDC}")
        max_date = input(f"{Bcolors.BOLD}Введіть другу дату -> {Bcolors.ENDC}")
        q = session.execute(select(self.base).where(self.base.reg_date.between(min_date, max_date))).scalars()
        self.print_table(self.marsh.dump(q, many=True))
        self.find = True

    def find_by_activity(self):
        print(f"{Bcolors.FAIL}Вводити такого типу -> 2021-07-25{Bcolors.ENDC}")
        min_date = input(f"{Bcolors.BOLD}Введіть першу дату -> {Bcolors.ENDC}")
        max_date = input(f"{Bcolors.BOLD}Введіть другу дату -> {Bcolors.ENDC}")
        q = session.execute(select(self.base).where(self.base.last_activity.between(min_date, max_date))).scalars()
        self.print_table(self.marsh.dump(q, many=True))
        self.find = True

    def menu(self):
        self.print_table(self.all_rows(self.page))
        while True:
            if not self.find:
                print(f"{Bcolors.HEADER} Дії {Bcolors.ENDC}")
                for idx, elem in enumerate(self.funcs_view_main):
                    print(f"{Bcolors.BOLD}[{idx+1}] - {elem}{Bcolors.ENDC}")
                func = input(" -> ")
                if func.isnumeric():
                    if int(func) in list(range(1, len(self.funcs_view_main)+1)):
                        if int(func) == len(self.funcs_view_main):
                            break
                        else:
                            self.funcs_view_call_main[int(func)]()
                    else:
                        self.print_table(self.all_rows(self.page))
                else:
                    self.print_table(self.all_rows(self.page))
            else:
                while True:
                    print(f"{Bcolors.HEADER} Дії {Bcolors.ENDC}\n{Bcolors.BOLD}[1] - Повернутись{Bcolors.ENDC}")
                    func = input(" -> ")
                    if func.isnumeric():
                        if int(func) == 1:
                            self.find = False
                            break
                self.page = 1
                clear_console()
                self.print_table(self.all_rows(self.page))
        return

    def menu_edit(self):
        self.print_table(self.all_rows(self.page))
        while True:
            print(f"{Bcolors.HEADER} Дії {Bcolors.ENDC}")
            for idx, elem in enumerate(self.funcs_edit_main):
                print(f"{Bcolors.BOLD}[{idx+1}] - {elem}{Bcolors.ENDC}")
            func = input(" -> ")
            if func.isnumeric():
                if int(func) in list(range(1, len(self.funcs_edit_main)+1)):
                    if int(func) == len(self.funcs_edit_main):
                        break
                    else:
                        self.funcs_edit_call_main[int(func)]()
                else:
                    self.print_table(self.all_rows(self.page))
            else:
                self.print_table(self.all_rows(self.page))
        return
