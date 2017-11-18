from models.base_model import *
from peewee import CharField, DateTimeField

class Country(BaseModel):
    name = CharField(50)
    slug = CharField(50)
    date_created = DateTimeField()
