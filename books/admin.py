from django.contrib import admin
from books.models import book, review
 
 # Register your models here.

class bookAdmin(admin.ModelAdmin):
    pass
admin.site.register(book, bookAdmin)


class reviewAdmin(admin.ModelAdmin):
	pass
admin.site.register(review, reviewAdmin) 