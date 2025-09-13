import os
from django.db import models
from datetime import datetime
# Create your models here.

class BaseModel(models.Model):
    name = models.CharField(max_length=128,unique=True,verbose_name='نام پایگاه')
    people = models.ManyToManyField('PersonModel',verbose_name='افراد')
    class Meta:
        verbose_name = 'پایگاه'
        verbose_name_plural = 'پایگاه ها'

    def __str__(self):
        return self.name

class RoleModel(models.Model):
    role_name = models.CharField(max_length=128,unique=True,verbose_name='نام جایگاه')
    parent = models.ForeignKey('self',on_delete=models.CASCADE,null=True,blank=True,verbose_name='جایگاه بالادستی')
    role_person = models.ForeignKey('PersonModel',on_delete=models.DO_NOTHING,verbose_name='فرد')
    class Meta:
        verbose_name = 'جایگاه'
        verbose_name_plural = 'جایگاه ها'
    def __str__(self):
        return self.role_name

class PhoneNumberModel(models.Model):
    number = models.CharField(max_length=32,unique=True,verbose_name='شماره')
    country_code = models.IntegerField(verbose_name='کد کشور')
    class Meta:
        verbose_name = 'شماره تماس'
        verbose_name_plural = 'شماره های تماس'
    def __str__(self):
        return f'{self.number}|{self.country_code}+'

class EmailModel(models.Model):
    email_address = models.EmailField(unique=True,verbose_name='آدرس ایمیل')
    person = models.ForeignKey('PersonModel',on_delete=models.DO_NOTHING,verbose_name='فرد')
    class Meta:
        verbose_name = 'ایمیل'
        verbose_name_plural = 'ایمیل ها'
    def __str__(self):
        return self.email_address

class PlatformsChoice(models.TextChoices):
    FACEBOOK = 'facebook', 'Facebook'
    TELEGRAM = 'telegram', 'Telegram'
    WHATSAPP = 'whatsapp', 'WhatsApp'
    INSTAGRAM = 'instagram', 'Instagram'
    SIGNAL = 'signal', 'Signal'
    SLACK = 'slack', 'Slack'
    OTHER = 'other', 'Other'

class AcountIdModel(models.Model):
    platform = models.CharField(max_length=64,choices=PlatformsChoice.choices,verbose_name='نام پلتفرم')
    account_id = models.CharField(max_length=128,verbose_name='آیدی حساب کاربری')
    class Meta:
        unique_together = ('platform', 'account_id')
        verbose_name = 'حساب کاربری'
        verbose_name_plural = 'حساب های کاربری'

    def __str__(self):
        return f'{self.account_id} ({self.platform})'

class GenderChoise(models.TextChoices):
    MALE = 'm','آقا'
    FEMALE = 'f','خانم'
    OTHER = 'o','سایر'

class EducationLevel(models.TextChoices):
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
    education = models.CharField(max_length=20,choices=EducationLevel.choices,null=True,blank=True,verbose_name='تحصیلات')
    institution = models.CharField(max_length=128,null=True,blank=True,verbose_name='موسسه')
    unit = models.CharField(max_length=128,null=True,blank=True,verbose_name='واحد')
    adddress = models.CharField(max_length=128,null=True,blank=True,verbose_name='آدرس')
    martial_status = models.CharField(max_length=128,null=True,blank=True,verbose_name='وضعیت رزمی')
    birth_date = models.DateField(null=True,blank=True,verbose_name='تاریخ تولد')
    place_of_birth = models.CharField(null=True,blank=True,verbose_name='محل تولد')
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
        return self.first_name+' '+self.last_name


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