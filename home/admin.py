from django.contrib import admin
from .models import Swimmer, SwimTime
# Register your models here.
class SwimTimeInLine(admin.TabularInline):
    model = SwimTime
    extra = 1

class SwimmerAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Swimmer Information', {'fields':['first_name','last_name']})
    ]
    inlines = [SwimTimeInLine]
    list_display = ('first_name','last_name')
    search_fields = ['first_name','last_name']
    
admin.site.register(Swimmer, SwimmerAdmin)