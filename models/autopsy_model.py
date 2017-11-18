from models.base_model import *
from peewee import CharField, TextField, DateTimeField, ForeignKeyField
from models.category_model import Category
from models.country_model import Country

class Autopsy(BaseModel):
    company_name = CharField(50)
    company_logo = CharField()
    description = TextField(200)
    industry = ForeignKeyField(rel_model=Category)
    year_range = CharField(20)
    country=ForeignKeyField(rel_model=Country)
    amount_raised=CharField(50)
    founder_name=CharField(50)
    why_they_failed=TextField(1000)
    date_created = DateTimeField()
