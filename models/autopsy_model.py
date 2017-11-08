from models.base_model import *
from peewee import CharField, TextField, DateTimeField

from datetime import datetime

class AutopsyModel(BaseModel):
    company_name = CharField(50)
    company_logo = CharField()
    description = TextField(200)
    industry = CharField(20)
    year_range = CharField(20)
    country=CharField(50)
    amount_raised=CharField(50)
    founder_name=CharField(50)
    why_they_failed=TextField(1000)
    amount_raised=CharField(50)
    timestamp = DateTimeField(default=datetime.now)
