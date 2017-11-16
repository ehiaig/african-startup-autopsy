from models.base_model import *
from peewee import CharField, DateTimeField
from datetime import datetime

class UserModel(BaseModel):
    username = CharField(50)
    email = CharField(50)
    password = CharField(64)
    date_created = DateTimeField(default=datetime.now)
