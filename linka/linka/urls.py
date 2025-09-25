from django.urls import path
from . import views

app_name = 'linka'
urlpatterns = [
    path('',views.home_page, name='home'),
    path('merge',views.merge_people_page,name='merge_page'),
    path('merge-records',views.merge_two_records,name='merge_records'),
    path('export',views.export_linka_data,name='export'),
    # path('import',views.export_linka_data,name='import'),
    path('to_neo4j',views.to_neo4j, name='to_neo4j')
]