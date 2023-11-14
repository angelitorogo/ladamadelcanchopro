from datetime import datetime

def contexto_year(request):

    contexto = {}
    year = datetime.now().year
    contexto['year'] = year
    
    return contexto
