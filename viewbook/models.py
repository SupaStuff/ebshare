from django.db import models
from django.contrib.auth.models import User
from books.models import book
import os

class reader(models.Model):
    user = models.ForeignKey(User, db_column='user')
    book = models.ForeignKey(book, db_column='book_id')
    time_read = models.IntegerField(default=0)
    time_left = models.IntegerField(default=0)
    rating = models.IntegerField(default=0)
    complained = models.BooleanField(default=False)
    def __unicode__(self):
		return self.time_read
