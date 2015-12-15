from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from books.models import book, review
from userAuth.models import userProfile

#admin.site.register(book)
admin.site.register(review)

@admin.register(book)
class bookAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if change:
            if obj.reqpoints <= obj.approvedpoints:
                obj.approved = True
                obj.last_opened = now()
                user = userProfile.objects.get(user=obj.user)
                user.points += obj.approvedpoints
                user.save()
            else:
                obj.blacklist = True
        obj.save()
