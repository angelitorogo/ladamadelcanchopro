from django.shortcuts import render, redirect, reverse
# Para hacer login, hay que importar el modulo de autenticacion
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .forms import UserCreationFormWithEmail
from django.core.mail import EmailMessage
from django.core import signing
from datetime import datetime, timedelta


# Create your views here.

def login_page(request): 
        
    if request.user.is_authenticated: # esto es por si intentas entrar una vez logado a la url de login o registro manualmente, te redirecciona a inicio
        
        redirect_url = '/rutas'
        return redirect(redirect_url) 

    else:

        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            
            if username == '' or password == '':
                redirect_url = '/accounts/login/?formFault'
                return redirect(redirect_url)

            user = authenticate(request, username=username, password=password)
            
           

            if user is not None:
                
                login(request, user) 
                    
                redirect_url = request.GET.get('next', '/rutas')  # Si 'next' no está presente, redirige a la página principal
                return redirect(redirect_url)               
                
            else:
                
                redirect_url = '/accounts/login/?noMatch'
                return redirect(redirect_url) 


    return render(request, 'registration/login.html', {'title': 'Inicie sesión'})

def register_page(request):

    
    if request.user.is_authenticated:  # esto es por si intentas entrar una vez logado a la url de login o registro manualmente, te redirecciona a inicio

        redirect_url = '/rutas'
        return redirect(redirect_url)

    else:

        # Nuestro formulario personalizado basado en el model user de Djano (forms.py)
        register_form = UserCreationFormWithEmail()        
    
        if request.method == 'POST':

            register_form = UserCreationFormWithEmail(request.POST)
            
            
            if register_form.is_valid():
                email = register_form.cleaned_data['email']
                
                username = register_form.cleaned_data['username']
                                

                if User.objects.filter(email=email).exists():
                                                            
                    redirect_url = '/accounts/signup/?existeMail'
                    return redirect(redirect_url) 
                
                
                else:

                    register_form.save()

                    redirect_url = '/accounts/login/?register'

                    return redirect(redirect_url) 
            else:
                
                redirect_url = '/accounts/signup/?formfault'
                return redirect(redirect_url) 
        

        return render(request, 'registration/signup.html', {'title': 'Registro de usuario'})
       
def logout_user(request):
    
    logout(request)

    return redirect('rutas')

def reset_password(request):
    
    if request.user.is_authenticated: # esto es por si intentas entrar una vez logado a la url de login o registro manualmente, te redirecciona a inicio
        
        redirect_url = '/rutas'
        return redirect(redirect_url)

    else:
        
        if request.method == 'POST':
            email = request.POST.get('email')
        
            if User.objects.filter(email=email).exists():     
                
                fechaHora_envio = datetime.now()
                fechaString = fechaHora_envio.strftime("%Y-%m-%d %H:%M:%S")
                
                arrayData = [email, fechaString]
                
                #Encriptar email, para enviarlo en el correo
                encrypted_email = signing.dumps(arrayData)           
    
                #enviar correo con instrucciones....basicamente redireccionar a otro html donde poner la nueva contraseña
                #enviamos el correo con EmailMessage
                email = EmailMessage(
                    "La Dama del Cancho", 
                    #'De no-contestar <no-reply@angelrodriguez.es>\n\nPara recuperar su contraseña ingrese a esta url:\n\nhttp://argomez.com/accounts/new-password/?email={}'.format(email_encriptado),
                    'De no-contestar <no-reply@ladamadelcancho.es>\n\nPara recuperar su contraseña ingrese a esta url:\n\nhttp://www.ladamadelcancho.es/accounts/new-password/?email={}\nEste enlace expirará en 10 minutos.'.format(encrypted_email),
                    "no-reply@ladamadelcancho.es", 
                    [email], # aquien se le envia
                    reply_to=["no-reply@ladamadelcancho.es"]
                )
                
                try:
                    email.send()
                    #suponiendo que todo bien redireccionamos
                    redirect_url = '/accounts/login/?existe'
                    return redirect(redirect_url)
                
                except:
                    #Algo no ha ido bien, redireccionamos a FAIL
                    redirect_url = '/accounts/reset-password/?fallo'
                    return redirect(redirect_url)
                
                
            
                
            
            else:
            
                redirect_url = '/accounts/reset-password/?noexiste'
                return redirect(redirect_url)

    


        return render(request, 'registration/reset_password.html', {'title': 'Resetear contraseña'})
    
    
def new_password(request):
    
    dataEncrypt = request.GET.get('email')

    try:
        data = signing.loads(dataEncrypt)
        fecha_hora_link = datetime.strptime(data[1], '%Y-%m-%d %H:%M:%S')

        # Definir un timedelta de 600 segundos
        delta = timedelta(seconds=600)
        
        # Calcular la fecha 600 segundos más tarde
        fecha_hora_link_exp = fecha_hora_link + delta
        fechaHora_actual = datetime.now()

    
        if (fecha_hora_link_exp < fechaHora_actual):
            redirect_url = '/accounts/login/?expirado'
            return redirect(redirect_url)
        
        
        user = User.objects.get(email=data[0])
    except: 
        redirect_url = '/accounts/login/?errornewpassword'
        return redirect(redirect_url)
    
    
    if request.user.is_authenticated or dataEncrypt == None:  # esto es por si intentas entrar una vez logado a la url de login o registro manualmente, te redirecciona a inicio

        redirect_url = '/rutas'
        return redirect(redirect_url)

    else:
        
        if request.method == 'POST':
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')
            
            if password1 != "" and password1 == password2:
                                
                user.set_password(password1)
                user.save()
                    
                redirect_url = '/accounts/login/?changed'
                return redirect(redirect_url)
            
            if password1 != password2:
                # Obtenemos la URL actual usando reverse() con el nombre de la vista actual
                url_actual = reverse(new_password)
     
                # Agregamos el nuevo parámetro a la URL
                redirect_url = f"{url_actual}?error&email={dataEncrypt}"
                
                return redirect(redirect_url)  
    
        return render(request, 'registration/new-password.html', {'title': 'Nueva contraseña'})