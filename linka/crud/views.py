from django.shortcuts import render
from django.http import JsonResponse
from neomodel.contrib import SemiStructuredNode
# Create your views here.
from .models import get_node
def test(request):
    Node = get_node('Role')
    # node = Node(title='ali2')
    # node.save()
    
    d = {}
    for p in Node.nodes.all():
        p :SemiStructuredNode= p
        d[p.element_id]= p.labels()
        
    return JsonResponse(d)