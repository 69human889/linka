import os
from datetime import datetime
# 
from django.core.exceptions import ValidationError
from django.db import models
from neomodel import db


# Create your models here.

class BaseModel(models.Model):
    name = models.CharField(max_length=128,unique=True,verbose_name='نام مکان')
    people = models.ManyToManyField('PersonModel',verbose_name='افراد')
    latitude = models.FloatField(verbose_name='lat')
    longtitude = models.FloatField(verbose_name='long')
    base_type = models.CharField(max_length=128,verbose_name='نوع مکان')
    address = models.TextField(verbose_name='آدرس')
    postal_code = models.CharField(max_length=64,verbose_name='کد پستی')

    class Meta:
        verbose_name = 'پایگاه'
        verbose_name_plural = 'پایگاه ها'

    def __str__(self):
        return self.name
    @classmethod
    def to_neo4j(cls):
        for obj in cls.objects.values():
            db.cypher_query(
                'MERGE (b:Base {name:$name})',obj
            )
        for base in cls.objects.prefetch_related('people'):
            for person in base.people.values():
                db.cypher_query(
                    'MATCH (b:Base {name:$base_name})'
                    'MATCH (p:Person {id:$person_id})'
                    'MERGE (b)-[:BASE_PERSON]-(p)'
                    ,{
                        'base_name':base.name,
                        'person_id':person['id']
                    }
                )

class RoleModel(models.Model):
    role_name = models.CharField(max_length=128,unique=True,verbose_name='نام جایگاه')
    parent = models.ForeignKey('self',on_delete=models.CASCADE,null=True,blank=True,verbose_name='جایگاه بالادستی')
    role_person = models.ForeignKey('PersonModel',on_delete=models.DO_NOTHING,null=True,blank=True,verbose_name='نفر فعلی')
    class Meta:
        verbose_name = 'جایگاه'
        verbose_name_plural = 'جایگاه ها'
    def __str__(self):
        return self.role_name

    @classmethod
    def to_neo4j(cls):
        for obj in cls.objects.prefetch_related('parent','role_person'):
            if obj.parent and obj.role_person:
                db.cypher_query(
                    'MERGE(r:Role {role_name:$role_name})'
                    'WITH r '
                    'MATCH(r2:Role {role_name:$role_parent_name})'
                    'MATCH(p:Person {id:person_id})'
                    'MERGE(r2)-[:ROLE_PARENT]-(r)'
                    'MERGE(r)-[:ROLE_PERSON]-(p)'
                    ,{
                        'role_name':obj.role_name,
                        'role_parent_name':obj.parent.role_name,
                        'person_id':obj.role_person.id
                    }
                    
                )
            elif obj.parent and not obj.role_person:
                db.cypher_query(
                    'MERGE(r:Role {role_name:$role_name})'
                    'WITH r '
                    'MATCH(r2:Role {role_name:$role_parent_name})'
                    'MERGE(r2)-[:ROLE_PARENT]-(r)'
                    ,{
                        'role_name':obj.role_name,
                        'role_parent_name':obj.parent.role_name
                    }
                    
                )
            elif not obj.parent and obj.role_person:
                db.cypher_query(
                    'MERGE(r:Role {role_name:$role_name})'
                    'WITH r '
                    'MATCH(p:Person {id:$person_id})'
                    'MERGE(r)-[:ROLE_PERSON]-(p)'
                    ,{
                        'role_name':obj.role_name,
                        'person_id':obj.role_person.id
                    }
                    
                )
            else:
                db.cypher_query(
                    'MERGE(r:Role {role_name:$role_name})'
                    ,{
                        'role_name':obj.role_name
                    } 
                )

class PhoneNumberModel(models.Model):
    number = models.CharField(max_length=32,unique=True,verbose_name='شماره')
    country_code = models.IntegerField(verbose_name='کد کشور')
    class Meta:
        verbose_name = 'شماره تماس'
        verbose_name_plural = 'شماره های تماس'
    def __str__(self):
        return f'{self.number}|{self.country_code}+'
    @classmethod
    def to_neo4j(cls):
        for obj in cls.objects.values():
            db.cypher_query(
                'MERGE (pn:PhoneNumber {number:$number,country_code:$country_code}) return pn;',obj
            )
        
class EmailModel(models.Model):
    email_address = models.EmailField(unique=True,verbose_name='آدرس ایمیل')
    person = models.ForeignKey('PersonModel',on_delete=models.DO_NOTHING,verbose_name='فرد')
    class Meta:
        verbose_name = 'ایمیل'
        verbose_name_plural = 'ایمیل ها'
    def __str__(self):
        return self.email_address

    @classmethod
    def to_neo4j(cls):
        for obj in cls.objects.prefetch_related('person'):
            db.cypher_query(
                'MERGE (e:Email {email_address:$email_address})'
                'WITH e '
                'MATCH (p:Person {id:$person_id})'
                'MERGE (p)-[:PERSON_EMAIL]-(e)'
                ,{
                    'email_address':obj.email_address,
                    'person_id':obj.person.id
                }
            )

class PlatformsChoice(models.TextChoices):
    FACEBOOK = 'facebook', 'Facebook'
    TELEGRAM = 'telegram', 'Telegram'
    WHATSAPP = 'whatsapp', 'WhatsApp'
    INSTAGRAM = 'instagram', 'Instagram'
    SIGNAL = 'signal', 'Signal'
    SLACK = 'slack', 'Slack'
    OTHER = 'other', 'Other'

class AcountIdModel(models.Model):
    person = models.ForeignKey('PersonModel',on_delete=models.DO_NOTHING,verbose_name='فرد')
    platform = models.CharField(max_length=64,choices=PlatformsChoice.choices,verbose_name='نام پلتفرم')
    account_id = models.CharField(max_length=128,verbose_name='آیدی حساب کاربری')
    class Meta:
        unique_together = ('platform', 'account_id')
        verbose_name = 'حساب کاربری'
        verbose_name_plural = 'حساب های کاربری'

    def __str__(self):
        return f'{self.account_id} ({self.platform})'
    
    @classmethod
    def to_neo4j(cls):
        for obj in cls.objects.prefetch_related('person'):
            db.cypher_query(
                'MERGE (a:Account {platform:$platform,account_id:$account_id})'
                'WITH a '
                'MATCH (p:Person {id:$person_id})'
                'MERGE (p)-[:PERSON_ACCOUNT]-(a)'
                ,{
                    'platform':obj.platform,
                    'account_id':obj.account_id,
                    'person_id':obj.person.id
                }
            )

    

class GenderChoise(models.TextChoices):
    MALE = 'm','آقا'
    FEMALE = 'f','خانم'
    OTHER = 'o','سایر'

class EducationLevelChoise(models.TextChoices):
    NONE = 'none', 'بدون تحصیلات رسمی'
    PRIMARY = 'primary', 'ابتدایی'
    SECONDARY = 'secondary', 'متوسط اول'
    HIGH_SCHOOL = 'high_school', 'متوسط دوم'
    DIPLOMA = 'diploma', 'دیپلم'
    BACHELORS = 'bachelor', 'کارشناسی'
    MASTERS = 'master', 'کارشناسی ارشد'
    DOCTORATE = 'doctorate', 'دکتری'
    OTHER = 'other', 'سایر'

class PersonModel(models.Model):
    first_name = models.CharField(max_length=128,null=True,blank=True,verbose_name='نام')
    last_name = models.CharField(max_length=128,null=True,blank=True,verbose_name='نام خانوادگی')
    hebrew_first_name = models.CharField(max_length=128,null=True,blank=True,verbose_name='نام عبری')
    hebrew_last_name = models.CharField(max_length=128,null=True,blank=True,verbose_name='نام خانوادگی عبری')
    gender = models.CharField(max_length=10,choices=GenderChoise.choices,null=True,blank=True,verbose_name='جنسیت')
    phone_numbers = models.ManyToManyField(PhoneNumberModel,blank=True,verbose_name='شماره ها')
    education = models.CharField(max_length=20,choices=EducationLevelChoise.choices,null=True,blank=True,verbose_name='تحصیلات')
    institution = models.CharField(max_length=128,null=True,blank=True,verbose_name='موسسه')
    unit = models.CharField(max_length=128,null=True,blank=True,verbose_name='واحد')
    adddress = models.CharField(max_length=128,null=True,blank=True,verbose_name='آدرس')
    martial_status = models.CharField(max_length=128,null=True,blank=True,verbose_name='وضعیت رزمی')
    birth_date = models.DateField(null=True,blank=True,verbose_name='تاریخ تولد')
    place_of_birth = models.CharField(max_length=128,null=True,blank=True,verbose_name='محل تولد')
    father_name = models.CharField(max_length=128,null=True,blank=True,verbose_name='نام پدر')
    mother_name = models.CharField(max_length=128,null=True,blank=True,verbose_name='نام مادر')
    job = models.CharField(max_length=128,null=True,blank=True,verbose_name='شغل غیر نظامی')
    military_job = models.CharField(max_length=128,null=True,blank=True,verbose_name='شغل نظامی')
    description = models.TextField(null=True,blank=True,verbose_name='سایر توضیحات')

    class Meta:
        unique_together = ('first_name', 'last_name')
        verbose_name = 'فرد'
        verbose_name_plural = 'افراد'

    def __str__(self):
        return f'{self.id}-{self.first_name}-{self.last_name}'
    @classmethod
    def to_neo4j(cls):
        for obj in cls.objects.values():
            update_keys = ' , '.join([f'p.{key}=${key}' for key,value in obj.items() if key !='id' and value])
            db.cypher_query(
                'MERGE (p:Person {id:$id}) '
                f' ON CREATE SET {update_keys}'
                f' ON MATCH SET {update_keys}'
                ,obj
            )
        for person in cls.objects.prefetch_related("phone_numbers"):
            for phonenumber in person.phone_numbers.values():
                parames = {
                    'person_id':person.id,
                    'phone_number' : phonenumber['number']
                }
                db.cypher_query(
                    'match(p:Person {id:$person_id})'
                    'match(pn:PhoneNumber {number:$phone_number})'
                    'merge (p)-[:PERSON_PHONENUMBER]-(pn)'
                    ,parames
                )

class PeopleRelationshipModel(models.Model):
    person_A = models.ForeignKey(PersonModel,on_delete=models.CASCADE,verbose_name='طرف اول',related_name="+")
    person_B = models.ForeignKey(PersonModel,on_delete=models.CASCADE, verbose_name='طرف دوم',related_name="+")
    rel_type = models.CharField(max_length=64,verbose_name='نوع رابطه')
    duration = models.CharField(max_length=64,verbose_name='مدت زمان')
    class Meta:
        unique_together = ('person_A', 'person_B')
        verbose_name = 'رابطه افراد'
        verbose_name_plural = 'رابطه های افراد'

    def __str__(self):
        return f'({self.person_A})-[{self.rel_type}]->{self.person_B}' 
    def clean(self):
        if self.person_A == self.person_B:
            raise ValidationError("A person cannot have a relationship with themselves.")


def update_image_path(instance,filename):
    name,ext = os.path.splitext(os.path.basename(filename))
    ts = datetime.now().strftime('%Y-%m-%d')
    return f'archive/images/{instance.person.id}/{ts}-{name}{ext}'
def update_file_path(instance,filename):
    name,ext = os.path.splitext(os.path.basename(filename))
    ts = datetime.now().strftime('%Y-%m-%d')
    return f'archive/files/{instance.person.id}/{ts}-{name}{ext}'

class ImageModel(models.Model):
    person = models.ForeignKey(PersonModel,on_delete=models.DO_NOTHING,verbose_name='فرد')
    image = models.ImageField(upload_to=update_image_path,unique=True,verbose_name='تصویر')
    class Meta:
        verbose_name = 'تصویر'
        verbose_name_plural = 'تصاویر'
    def __str__(self):
        return self.image.path

class FileModel(models.Model):
    person = models.ForeignKey(PersonModel,on_delete=models.DO_NOTHING,verbose_name='فرد')
    file = models.FileField(upload_to=update_file_path,unique=True,verbose_name='فایل')
    class Meta:
        verbose_name = 'فایل'
        verbose_name_plural = 'فایل ها'
    def __str__(self):
        return self.file.path