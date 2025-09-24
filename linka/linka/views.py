import json
# 
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib import messages
from django.db import transaction
from django.db.models import ManyToManyField
from django.shortcuts import render,redirect
from neomodel import db
# 
from . import models
# Create your views here.

@login_required(login_url='/admin/login')
def home_page(request):
    context = {
        'title':'Home-Page',
        'head_name':'Dashboard'
    }
    return render(request,'home_page.html',context=context)
@user_passes_test(lambda u: u.is_superuser,login_url='admin:index')
def merge_people_page(request):
    records = models.PersonModel.objects.all()
    context = {
        'title':'Merge-Page',
        'head_name':'Merge Records',
        'records':records
    }
    return render(request,'merge_page.html',context=context)
@user_passes_test(lambda u: u.is_superuser,login_url='admin:index')
def merge_two_records(request):

    if request.method == "POST":
        remain_record_id = request.POST.get('record_keep')
        remove_record_id = request.POST.get('record_merge')

        if remain_record_id == remove_record_id:
            messages.error(request, "Objects can't be the same.")
            return redirect('linka:merge_page')
        
        try:
            remain_record = models.PersonModel.objects.get(id=remain_record_id)
            remove_record = models.PersonModel.objects.get(id=remove_record_id)
        except models.PersonModel.DoesNotExist:
            messages.warning(request, "Object is missing.")
            return redirect('linka:merge_page')
        
        if remain_record.__class__ != remove_record.__class__:
            messages.error(request, "Objects must be from the same model.")
            return redirect('linka:merge_page')

        with transaction.atomic():
            # -----------------------------
            # 1. Handle reverse relations
            # -----------------------------
            for related in remain_record._meta.related_objects:
                rel_manager = getattr(remove_record, related.get_accessor_name())
                # OneToOneField
                if related.one_to_one:
                    try:
                        obj = rel_manager.get()
                        setattr(obj, related.field.name, remain_record)
                        obj.save()
                    except related.related_model.DoesNotExist:
                        pass

                # ManyToManyField
                elif isinstance(related.field, ManyToManyField):
                    for obj in rel_manager.all():
                        getattr(obj, related.field.name).add(remain_record)
                    rel_manager.clear()

                # ForeignKey (one-to-many)
                else:
                    rel_manager.update(**{related.field.name: remain_record})
            # -----------------------------
            # 2. Handle direct ManyToMany fields on the model
            # -----------------------------
            for m2m_field in remove_record._meta.many_to_many:
                old_m2m_manager = getattr(remove_record, m2m_field.name)
                new_m2m_manager = getattr(remain_record, m2m_field.name)
                
                # Transfer all related objects
                new_m2m_manager.add(*old_m2m_manager.all())
                
                # Clear old object
                old_m2m_manager.clear()
            # Delete duplicate
            remove_record.delete()

        messages.success(request, "Records merged successfully.")

    return redirect('linka:merge_page')

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