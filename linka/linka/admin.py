from django.contrib import admin

from .models import (
    PersonModel,
    BaseModel,
    FileModel,
    RoleModel,
    EmailModel,
    ImageModel,
    AcountIdModel,
    PhoneNumberModel,
    PeopleRelationshipModel,
    PeopleRoleModel
)


def get_all_fields(model):
    fields = [field.name for field in model._meta.get_fields() if field.many_to_many != True and field.one_to_many != True]
    return fields
    # return ['__str__']+fields



# Register your models here.
@admin.register(PersonModel)
class PersonAdmin(admin.ModelAdmin):
    list_display = get_all_fields(PersonModel)
    list_display_links = list_display
    search_fields = ['id','first_name','last_name']
    autocomplete_fields = ['phone_numbers']

@admin.register(RoleModel)
class RoleAdmin(admin.ModelAdmin):
    list_display = get_all_fields(RoleModel)
    list_display_links = list_display
    search_fields = ['role_name']
    autocomplete_fields = ['role_person']

@admin.register(BaseModel)
class BaseAdmin(admin.ModelAdmin):
    list_display = get_all_fields(BaseModel)
    list_display_links = list_display
    search_fields = []
    autocomplete_fields = ['people']
    
@admin.register(FileModel)
class FileAdmin(admin.ModelAdmin):
    list_display = get_all_fields(FileModel)
    list_display_links = list_display
    search_fields = []
    autocomplete_fields = ['person']

@admin.register(EmailModel)
class EmailAdmin(admin.ModelAdmin):
    list_display = get_all_fields(EmailModel)
    list_display_links = list_display
    search_fields = []
    autocomplete_fields = ['person']

@admin.register(ImageModel)
class ImageAdmin(admin.ModelAdmin):
    list_display = get_all_fields(ImageModel)
    list_display_links = list_display
    search_fields = []
    autocomplete_fields = ['person']

@admin.register(AcountIdModel)
class AccountAdmin(admin.ModelAdmin):
    list_display = get_all_fields(AcountIdModel)
    list_display_links = list_display
    search_fields = []
    autocomplete_fields = ['person']


@admin.register(PhoneNumberModel)
class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = get_all_fields(PhoneNumberModel)
    list_display_links = list_display
    search_fields = ['number']
    autocomplete_fields = []



@admin.register(PeopleRelationshipModel)
class PeopleRelationshipAdmin(admin.ModelAdmin):
    list_display = get_all_fields(PeopleRelationshipModel)
    list_display_links = list_display
    search_fields = []
    autocomplete_fields = ['person_A','person_B']

@admin.register(PeopleRoleModel)
class PeopleRoleAdmin(admin.ModelAdmin):
    list_display = get_all_fields(PeopleRoleModel)
    list_display_links = list_display
    search_fields = []
    autocomplete_fields = ['person','role']