from django.db import models

# Create your models here.
from neomodel import StringProperty, DateProperty,UniqueIdProperty
from neomodel.contrib import SemiStructuredNode

class Role(SemiStructuredNode):
    uid = UniqueIdProperty()
    title = StringProperty(unique_index=True)

class Person(SemiStructuredNode):
    uid = UniqueIdProperty()

class Base(SemiStructuredNode):
    uid = UniqueIdProperty()
    title = StringProperty(unique_index=True)

class Account(SemiStructuredNode):
    platform = StringProperty()
    identifire = StringProperty()


# def get_node(label):
#     return type(label, (SemiStructuredNode,), {'__label__': label,'uid':UniqueIdProperty()})