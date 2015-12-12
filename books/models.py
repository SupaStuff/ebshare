from django.db import models
from django.contrib.auth.models import User
import os

def get_image_path(instance, filename):
    return os.path.join('photos', str(instance.book_title), filename)

class book(models.Model):
    # Book Attributes
    book_title = models.CharField(max_length=20)
    book_author = models.CharField(max_length=60)
    book_cover = models.ImageField(upload_to=get_image_path, blank=True, null=True)
    alt_text = models.CharField(max_length=20)
    description = models.CharField(max_length=750)
    details = models.CharField(max_length=400)
    genre = models.CharField(max_length=20)
    book_points = models.CharField(max_length=50, default='50')
    # User who uploaded it
    user = models.ForeignKey(User, db_column='user', default="DevTeam")#, blank=True, null=True,)
    time_read = models.IntegerField(default=0)
    
    #ideally, these would 1 non-array field with the paragraph text
    #current error: "need more than 1 value to unpack"
    #description = ArrayField(models.CharField(max_length=500))
    #details = ArrayField(models.CharField(max_length=200))

    def __unicode__(self):
		return self.book.book_title

class review(models.Model):
    user = models.ForeignKey(User)
    book_review = models.ForeignKey(book)
    content = models.CharField(max_length=750)

    def __unicode__(self):
        return str(self.id)

#class txtbook(book):
#    fixtures = ['books.json']
