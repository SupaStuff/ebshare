from django.db import models
from books.models import book
from django.contrib.auth.models import User
from django.db.models import F
import os

def get_image_path(instance, filename):
    return os.path.join('photos', filename)

class userProfile(models.Model):
	# This line links userProfile to a Django User model instance.
	# The Django User model comes with five primary attributes:
	# Username, Password, First name, Last name
	user = models.OneToOneField(User)

	# The additional attribute we want to include.
	username = models.CharField(max_length=50, primary_key=True)	
	picture = models.ImageField(upload_to=get_image_path, blank=True, null=True)
	points = models.IntegerField(default=0)
	# TODO:
	# bio = 

	# 
	# Override the __unicode__() method to return something meaningful
	def __unicode__(self):
		return self.user.username

# class review(models.Model):
	
# 	reviewTitle = models.CharField(max_length=30)
# 	reviewContent = models.CharField(max_length=150)
# 	user = models.ForeignKey(User, db_column='user')
# 	book = models.ForeignKey(book)

# 	def __unicode__(self):
# 		return self.reviewTitle

class badWords(models.Model):
	#Each user can have bad words that they can search for in books
    user = models.ForeignKey(User, db_column='user')
    badword = models.CharField(max_length=20)

    def __unicode__(self):
		return self.badword

def create_profile(user):
    # profile, crprofile = userProfile.objects.get_or_create(user = user)
    # if crprofile:
    # 	profile.user = user
    profile = userProfile()
    profile.user = user
    profile.save()

def add_profile_pic(user, picture):
	userProf = userProfile.objects.get(user=user)
	userProf.picture = picture
	userProf.save()

def add_user_book(user, cover, title, points, author, description, genre):

	userProf = userProfile.objects.get(user=user)
        userProf.points = F('points') + 50
	userProf.save()

	Book = book()
	Book.book_cover = cover
	Book.book_title = title
	Book.book_points = points
	Book.book_author = author
	Book.description = description
	Book.genre = genre
	Book.user = user
	Book.save()

def add_bad_word(user, badWord):
	Badword = badWords()
	Badword.user = user
	Badword.badword = badWord
	Badword.save()