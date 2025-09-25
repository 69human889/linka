import io, json
# 
from django.apps import apps
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib import messages
from django.core import serializers
from django.core.serializers.base import DeserializationError
from django.db import transaction
from django.db.models import ManyToManyField
from django.http import HttpResponse

from django.shortcuts import render,redirect
from neomodel import db
# 
from . import models
from .forms import ImportDataForm
# Create your views here.

@login_required(login_url='/admin/login')
def home_page(request):
    context = {
        'title': 'Home-Page',
        'head_name': 'Dashboard'
    }

    if request.method == "POST":
        form = ImportDataForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data["file"]
            try:
                data = json.load(file)

                # Mapping: { "app_label.model_name": {old_pk: new_instance} }
                pk_map = {}

                with transaction.atomic():
                    # Step 1: create or reuse objects without PKs
                    for item in data:
                        model_label = item["model"]
                        Model = apps.get_model(*model_label.split("."))
                        old_pk = item["pk"]
                        fields = item["fields"]

                        # Check unique fields to avoid UNIQUE constraint errors
                        unique_fields = [
                            f.name for f in Model._meta.fields
                            if f.unique and f.name in fields
                        ]
                        filter_kwargs = {f: fields[f] for f in unique_fields} if unique_fields else {}
                        obj = Model.objects.filter(**filter_kwargs).first()
                        if not obj:
                            obj = Model.objects.create(**fields)

                        if model_label not in pk_map:
                            pk_map[model_label] = {}
                        pk_map[model_label][old_pk] = obj

                    # Step 2: fix foreign keys and ManyToMany
                    for item in data:
                        model_label = item["model"]
                        Model = apps.get_model(*model_label.split("."))
                        obj = pk_map[model_label][item["pk"]]
                        updated = False

                        for field in Model._meta.get_fields():
                            if field.is_relation and not field.auto_created:
                                if field.many_to_many:
                                    # ManyToMany
                                    old_values = item["fields"].get(field.name, [])
                                    if old_values:
                                        related_model_label = f"{field.remote_field.model._meta.app_label}.{field.remote_field.model.__name__}"
                                        new_related = [pk_map[related_model_label][pk] for pk in old_values]
                                        getattr(obj, field.name).set(new_related)
                                        updated = True
                                elif field.many_to_one:
                                    # ForeignKey
                                    old_value = item["fields"].get(field.name)
                                    if old_value:
                                        related_model_label = f"{field.remote_field.model._meta.app_label}.{field.remote_field.model.__name__}"
                                        setattr(obj, field.name, pk_map[related_model_label][old_value])
                                        updated = True

                        if updated:
                            obj.save()

                messages.success(request, "Data imported successfully with new IDs (unique constraints handled)!")
                return redirect("linka:home")

            except Exception as e:
                messages.error(request, f"Import failed: {e}")
    else:
        form = ImportDataForm()

    context["form"] = form
    return render(request, 'home_page.html', context=context)

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
    if request.method != "POST":
        return redirect('linka:merge_page')

    remain_record_id = request.POST.get('record_keep')
    remove_record_id = request.POST.get('record_merge')

    if remain_record_id == remove_record_id:
        messages.error(request, "Objects can't be the same.")
        return redirect('linka:merge_page')

    try:
        remain_record = models.PersonModel.objects.get(id=remain_record_id)
        remove_record = models.PersonModel.objects.get(id=remove_record_id)
    except models.PersonModel.DoesNotExist:
        messages.warning(request, "One or both objects are missing.")
        return redirect('linka:merge_page')

    if remain_record.__class__ != remove_record.__class__:
        messages.error(request, "Objects must be from the same model.")
        return redirect('linka:merge_page')

    # Use the improved merge function
    try:
        merge_records(remain_record, remove_record, delete_after_merge=True, verbose=False)
        messages.success(request, "Records merged successfully.")
    except Exception as e:
        messages.error(request, f"An error occurred while merging: {str(e)}")

    return redirect('linka:merge_page')


# The merge_records function from earlier
def merge_records(remain_record, remove_record, delete_after_merge=True, verbose=False):
    from django.db.models import ManyToManyField
    from django.db import transaction

    if remain_record._meta.model != remove_record._meta.model:
        raise ValueError("Both records must be instances of the same model")

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
                    current_related = getattr(remain_record, related.get_accessor_name(), None)
                    if current_related:
                        if verbose:
                            print(f"Conflict in {related.get_accessor_name()}: keeping existing relation.")
                        continue
                    setattr(obj, related.field.name, remain_record)
                    obj.save()
                    if verbose:
                        print(f"OneToOne {related.name}: reassigned {obj}")
                except related.related_model.DoesNotExist:
                    pass

            # ManyToManyField (reverse)
            elif isinstance(related.field, ManyToManyField):
                objs = list(rel_manager.all())
                for obj in objs:
                    getattr(obj, related.field.name).add(remain_record)
                rel_manager.clear()
                if verbose and objs:
                    print(f"Reverse M2M {related.name}: transferred {len(objs)} objects")

            # ForeignKey (one-to-many)
            else:
                count = rel_manager.update(**{related.field.name: remain_record})
                if verbose and count:
                    print(f"FK {related.name}: reassigned {count} objects")

        # -----------------------------
        # 2. Handle direct ManyToMany fields
        # -----------------------------
        for m2m_field in remove_record._meta.many_to_many:
            old_m2m_manager = getattr(remove_record, m2m_field.name)
            new_m2m_manager = getattr(remain_record, m2m_field.name)

            objs = list(old_m2m_manager.all())
            if objs:
                new_m2m_manager.add(*objs)
                old_m2m_manager.clear()
                if verbose:
                    print(f"Direct M2M {m2m_field.name}: transferred {len(objs)} objects")

        # -----------------------------
        # 3. Optional deletion of remove_record
        # -----------------------------
        if delete_after_merge:
            remove_record.delete()
            if verbose:
                print(f"Deleted merged record: {remove_record}")


def export_linka_data(request):
    app_models = apps.get_app_config("linka").get_models()
    export_data = []

    for model in app_models:
        model_label = f"{model._meta.app_label}.{model.__name__}"
        for obj in model.objects.all():
            export_data.append({
                "model": model_label,
                "pk": obj.pk,
                "fields": {
                    field.name: getattr(obj, field.name)
                    for field in model._meta.fields
                    if field.name != "id"
                }
            })

    response = HttpResponse(
        json.dumps(export_data, indent=2, default=str),
        content_type="application/json"
    )
    response["Content-Disposition"] = 'attachment; filename="linka_export.json"'
    return response

def import_linka_data(request):
    if request.method == "POST":
        form = ImportDataForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data["file"]
            try:
                objects = serializers.deserialize("json", file.read().decode("utf-8"))
                for obj in objects:
                    obj.save()
                messages.success(request, "Data imported successfully!")
                return redirect("linka:import_page")
            except Exception as e:
                messages.error(request, f"Import failed: {e}")
    else:
        form = ImportDataForm()

    return render(request, "linka/import_page.html", {"form": form})
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