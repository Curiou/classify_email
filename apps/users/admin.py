from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import UserProfile

# Register your models here.
# 用UserAdmin 去注册 UserProfile
admin.site.register(UserProfile, UserAdmin)
