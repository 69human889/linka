import json
# 
from django.shortcuts import render,redirect
from django.http import JsonResponse
from neomodel import db
# 
from . import models
# Create your views here.


def home_page(request):
    db.cypher_query('MATCH (n) DETACH DELETE n;')
    models.PhoneNumberModel.to_neo4j()
    models.PersonModel.to_neo4j()
    models.BaseModel.to_neo4j()
    models.RoleModel.to_neo4j()
    models.AcountIdModel.to_neo4j()
    models.EmailModel.to_neo4j()

    return JsonResponse({'message':'done.'})