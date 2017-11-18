from models.base_model import *
from peewee import CharField, DateTimeField

class Subscription(BaseModel):
    email = CharField(50)
    subscription_date = DateTimeField()
