import json
# 
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from neomodel import db
# 
from . import models
# Create your views here.

@login_required(login_url='/admin/login')
def home_page(request):
    # return JsonResponse({'message':'done.'})
    return render(request,'home_page.html',context={})

@login_required
def to_neo4j(request):
    if not request.user.is_staff:
        return redirect('/')
    db.cypher_query('MATCH (n) DETACH DELETE n;')
    models.PhoneNumberModel.to_neo4j()
    models.PersonModel.to_neo4j()
    models.BaseModel.to_neo4j()
    models.RoleModel.to_neo4j()
    models.AcountIdModel.to_neo4j()
    models.EmailModel.to_neo4j()
    return redirect('/')