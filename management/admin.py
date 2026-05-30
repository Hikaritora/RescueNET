from django.contrib import admin

from .models import User, Incident, Resource

class IncidentAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.full_clean()
        super().save_model(request, obj, form, change)

admin.site.register(User)
admin.site.register(Incident, IncidentAdmin)
admin.site.register(Resource)
