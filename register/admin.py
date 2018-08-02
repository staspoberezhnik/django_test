from django.contrib import admin
from .models import User, MyApplication, AccessToken

# Register your models here.
admin.site.register(User)
admin.site.register(MyApplication)
admin.site.register(AccessToken)