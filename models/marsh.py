from marshmallow import fields
from marshmallow_sqlalchemy import ModelSchema

from .model import (
    Film,
    Company,
    Category,
    Sales,
    Dates,
    Users,
    Salts,
    Perm,
    RegDates,
)

# Serialize data from table to dict


# For film model
class FilmMarsh(ModelSchema):
    class Meta:
        model = Film
        load_instance = True

    id = fields.Integer()
    name = fields.String()
    description = fields.String()
    company_id = fields.Integer()
    category_id = fields.Integer()
    release_date = fields.DateTime()
    active = fields.Boolean()


# For company model
class CompanyMarsh(ModelSchema):
    class Meta:
        model = Company
        load_instance = True

    id = fields.Integer()
    name = fields.String()


# For category model
class CategoryMarsh(ModelSchema):
    class Meta:
        model = Category
        load_instance = True

    id = fields.Integer()
    name = fields.String()


# For sales model
class SalesMarsh(ModelSchema):
    class Meta:
        model = Sales
        load_instance = True

    id = fields.Integer()
    film_id = fields.Integer()
    peoples = fields.Integer()
    ticket_price = fields.Float()


# For dates model
class DatesMarsh(ModelSchema):
    class Meta:
        model = Dates
        load_instance = True

    id = fields.Integer()
    film_id = fields.Integer()
    start_date = fields.Date()
    end_date = fields.Date()


# For users model
class UsersMarsh(ModelSchema):
    class Meta:
        model = Users
        load_instance = True

    id = fields.Integer()
    username = fields.String()
    full_name = fields.String()
    email = fields.String()
    hashed_password = fields.String()


# For salts model
class SaltsMarsh(ModelSchema):
    class Meta:
        model = Salts
        load_instance = True

    id = fields.Integer()
    user_id = fields.Integer()
    salt = fields.String()


# For perm model
class PermMarsh(ModelSchema):
    class Meta:
        model = Perm
        load_instance = True

    id = fields.Integer()
    user_id = fields.Integer()
    admin = fields.Boolean()


# For regdates model
class RegDatesMarsh(ModelSchema):
    class Meta:
        model = RegDates
        load_instance = True

    id = fields.Integer()
    user_id = fields.Integer()
    reg_date = fields.Date()
    last_activity = fields.Date()
