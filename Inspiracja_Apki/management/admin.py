from django.contrib import admin

from .models import User, Incident, Resource

admin.site.register(User)
admin.site.register(Incident)
admin.site.register(Resource)
