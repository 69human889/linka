from django.contrib import admin

from .models import (
    PersonModel,
    BaseModel,
    FileModel,
    RoleModel,
    EmailModel,
    ImageModel,
    AcountIdModel,
    PhoneNumberModel
)


def get_all_fields(model):

    fields = [field.name for field in model._meta.get_fields() if field.many_to_many != True and field.one_to_many != True and field.name != 'id']
    return ['__str__']+fields



# Register your models here.
@admin.register(PersonModel)
class PersonAdmin(admin.ModelAdmin):
    list_display = get_all_fields(PersonModel)
    search_fields = ['first_name','last_name']

@admin.register(RoleModel)
class RoleAdmin(admin.ModelAdmin):
    list_display = get_all_fields(RoleModel)
    list_display_links = list_display
    search_fields = ['role_name']
    autocomplete_fields = ['role_person']

@admin.register(BaseModel)
class BaseAdmin(admin.ModelAdmin):
    list_display = get_all_fields(BaseModel)
    search_fields = []
    autocomplete_fields = []
    
@admin.register(FileModel)
class FileAdmin(admin.ModelAdmin):
    list_display = get_all_fields(FileModel)
    search_fields = []
    autocomplete_fields = []

@admin.register(EmailModel)
class EmailAdmin(admin.ModelAdmin):
    list_display = get_all_fields(EmailModel)
    search_fields = []
    autocomplete_fields = []

@admin.register(ImageModel)
class ImageAdmin(admin.ModelAdmin):
    list_display = get_all_fields(ImageModel)
    search_fields = []
    autocomplete_fields = []

@admin.register(AcountIdModel)
class AccountAdmin(admin.ModelAdmin):
    list_display = get_all_fields(AcountIdModel)
    search_fields = []
    autocomplete_fields = []


@admin.register(PhoneNumberModel)
class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = get_all_fields(PhoneNumberModel)
    search_fields = []
    autocomplete_fields = []
