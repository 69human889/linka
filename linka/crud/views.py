from django.shortcuts import render
from django.http import JsonResponse
from neomodel.contrib import SemiStructuredNode
from neomodel import NodeSet
# Create your views here.
from .models import Role
def test(request):
    
    # node = Role(title='ali')
    # node.save()
    nodes :NodeSet= Role.nodes
    node = nodes.get(uid='9e1213282343459c80986cdaf4a7cc4f')
    d = {}
    # for p in nodes:
    #     p :SemiStructuredNode= p
    #     d[p.uid]= p.element_id_property
    d[node.uid] = node.__properties__['title']
    return JsonResponse(d)