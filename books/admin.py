from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from books.models import book, review

admin.site.register(book)
admin.site.register(review) 
