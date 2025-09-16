from django.urls import path
from . import views

app_name = 'linka'
urlpatterns = [
    path('',views.home_page, name='home'),
    path('to_neo4j',views.to_neo4j, name='to_neo4j')
]