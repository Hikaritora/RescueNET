from django.contrib import admin

from .models import Uzytkownik, Incydent, Zasob

admin.site.register(Uzytkownik)
admin.site.register(Incydent)
admin.site.register(Zasob)