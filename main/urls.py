# Entrance of the url (link)
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    
    # if https://127.0.0.0.1:8000/admin === opens admin page
    # django has inbuilt admin page
    path('admin/', admin.site.urls),
    
    #if no url extension means https://127.0.0.0.1:8000/
    # Goes inside api (django-app) urls
    path('',include('api.urls'))
]
