from django.contrib import admin

# Register your models here.
from .models import Captcha

# Register your models here.
class CaptchaAdmin(admin.ModelAdmin):
    list_display=('id','captcha_text', 'captcha_id')
    
admin.site.register(Captcha, CaptchaAdmin)