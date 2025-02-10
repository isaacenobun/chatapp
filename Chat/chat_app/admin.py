from django.contrib import admin

from .models import User, Messages, Contacts

# Register your models here.
admin.site.register(User)
admin.site.register(Messages)
admin.site.register(Contacts)