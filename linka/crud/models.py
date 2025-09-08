from django.db import models

# Create your models here.
from neomodel import StringProperty, DateProperty
from neomodel.contrib import SemiStructuredNode

class Role(SemiStructuredNode):
    title = StringProperty(unique_index=True)

# class Person(SemiStructuredNode):
#     pass

class Base(SemiStructuredNode):
    title = StringProperty(unique_index=True)

def get_node(label):
    return type(label, (SemiStructuredNode,), {'__label__': label})