from django.db import models

class Captcha(models.Model):
    captcha_id = models.CharField(max_length=20, unique=True, default='0')
    captcha_text = models.CharField(max_length=5)  # Asume que el captcha_text tiene una longitud fija de 6 caracteres
