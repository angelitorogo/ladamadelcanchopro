from django.shortcuts import render,redirect
from django.core.mail import EmailMessage
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import uuid
from .models import Captcha
from django.conf import settings
import os
import string

# Create your views here.
def contacto_page(request):
    
    
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        content = request.POST.get('content')
        captcha = request.POST.get('captcha_input')
        captcha_id = request.POST.get('captcha_id')
            
        #print(nombre)
        #print(email)
        #print(content)
        #print(captcha)
        #print(captcha_id)
        
        try:
            captchaDB = Captcha.objects.get(captcha_id=captcha_id)
            if captcha == captchaDB.captcha_text:
                # El CAPTCHA se ha pasado exitosamente
                
                #enviamos el correo con EmailMessage
                email = EmailMessage(
                    "La Dama del Cancho", 
                    "De {} <{}>\n\nEscribio:\n\n{}".format(nombre, email, content),
                    "no-reply@ladamadelcancho.es", 
                    ["argomez_81@hotmail.com"],
                    reply_to=[email]
                )
                
                try:
                    email.send()
                    #suponiendo que todo bien redireccionamos
                    captchaDB.delete()  # Elimina el captcha de la base de datos después de ser usado
                    
                    redirect_url = '/contacto?ok'
                    return redirect(redirect_url)
                
                except:
                    #Algo no ha ido bien, redireccionamos a FAIL
                    captchaDB.delete()  # Elimina el captcha de la base de datos después de ser usado
                    redirect_url = '/contacto?ko'
                    return redirect(redirect_url)
                        
                        
                
                
                
            else:
                # Respuesta incorrecta
                captchaDB.delete()
                redirect_url = '/contacto?no-captcha'
                return redirect(redirect_url)
        except Captcha.DoesNotExist:
            # Manejar el caso en el que el captcha no existe en la base de datos
            redirect_url = '/contacto?no-captcha'
            return redirect(redirect_url)

    Captcha.objects.all().delete()
       
    captcha_image, captcha_text = generate_captcha()
        
    # Guarda captcha_text en la base de datos
    captcha_id = str(uuid.uuid4())[:20]  # Genera un identificador único (en este caso, una versión corta de un UUID)
    Captcha.objects.create(captcha_id=captcha_id,captcha_text=captcha_text)
    
    
    return render(request, 'contacto/contacto.html', {'title': 'Contacto', 'captcha_image': captcha_image, 'captcha_text': captcha_text, 'captcha_id': captcha_id})
        
        


def generate_captcha():
    width, height = 125, 50
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    font = ImageFont.load_default()
    font = ImageFont.truetype("arial.ttf", 30)  # Cambia el tamaño de la fuente a 36 (puedes ajustar este valor)
    
    caracteres = string.ascii_letters + string.digits  # Incluye letras y números
    captcha_text = ''.join(random.choices(caracteres, k=5))

    draw.text((10, 10), captcha_text, font=font, fill=(0, 0, 0))

    # Agrega un poco de ruido a la imagen
    for _ in range(4500):
        x = random.randint(0, width-1)
        y = random.randint(0, height-1)
        draw.point((x, y), fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    
    
    if settings.DEBUG == False:
        url = os.path.join(settings.STATICFILES_DIRS[0], 'captcha', 'captcha_image.png')
    else:
        url = 'static/captcha/captcha_image.png'    
    
     
    image.save(url)

    return image, captcha_text