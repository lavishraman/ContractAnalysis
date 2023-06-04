from django.contrib import admin

# Register your models here.

from .models import Project, Location, Remark

admin.site.register(Project)
admin.site.register(Location)
admin.site.register(Remark)