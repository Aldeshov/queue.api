from django.contrib import admin

# Register your models here.
from app.models import Queue, Member

admin.site.register(Queue)
admin.site.register(Member)
