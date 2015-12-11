from django.shortcuts import render, redirect
from django.shortcuts import render_to_response
from userAuth.forms import UserForm, UserProfileForm
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.core.context_processors import csrf # for Cross Site Request Forgery.
from userAuth.models import add_user_book
from userAuth.models import userProfile
from userAuth.models import add_profile_pic, create_profile, add_bad_word
from books.models import book
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json


def renderProfile(request):
	return render_to_response("userAuth/profile.html")

def renderSignin(request):
	return render_to_response("userAuth/signin.html")

def register(request):
	context = RequestContext(request)

	# Boolean value for telling the template whether the registration was successful
	# Initially set to False. Changes to True when registration succeeds.
	registered = False

	# If it's a HTTP POST, we're interested in processing form data.
	if request.method == 'POST':
		# Attempt to grab information from the raw form information.
		user_form = UserForm(data=request.POST)

		if user_form.is_valid():
		# Save the user's form data to the database.
			user = user_form.save()
			# Hash the password with the set_password method.
			# Once hashed, we can update the user object.
			user.set_password(user.password)
			user.save()
			# Now sort out the UserProfile instance.
			create_profile(user)
			# update our variable to tell the template registration was successful.
			registered = True
			# Invalid form or forms - mistakes or something
			# Print problems to the terminal and show them to user.
		else:
			print user_form.errors
	# Not a HTTP POST, so we render our form using two ModelForm instances.
	# These forms will be blank waiting for user input.
	else:
		user_form = UserForm()
	# Render the template depending on the context.
	return render_to_response('userAuth/register.html',
		{'user_form': user_form, 'registered': registered}, context)

def user_login(request):
	# We obtain the context for the user's request.
	context = RequestContext(request)

	# If the request is a HTTP POST, try to pull out relevant information.
	if request.method == 'POST':
		# Gather the username and password provided by the user.
		# This information is obtained from the Login form.
		username = request.POST['username']
		password = request.POST['password']

		# Use Django's machinery to attempt to see if the username/password
		# combination is valid - a User object is returned if it is.
		user = authenticate(username=username, password=password)

		# If we have a user object, the details are correct.
		# If None, no user with matching credentials was found.
		if user:
			# If the account active? It could have been disabled.
			if user.is_active:
				# If the account is valid and active, we can log the user in (using Django machinery).
				# We'll send the user back to the homepage.
				login(request, user)
				return HttpResponseRedirect('/')
			else:
				# An inactive account was used - no logging in
				return HttpResponse("Your account is disabled.")
		else:
			# Bad login details were provided. Don't log the user in.
			# TODO: create an html page to redirect to with a login fail message
			print "Invalid Login details"
			return HttpResponse("Invalid login details was used")

	# The request is not a HTTP POST, so display the login form.
	# This scenario would most likely be a HTTP GET
	else:
		# No context variables to pass to the template system, hence the 
		# blank dictionary object
		return render_to_response('userAuth/login.html', {}, context)

@login_required
def user_profile(request):
	
    context = RequestContext(request)
    user = request.user
    bookList = book.objects.filter(user=user)
    profile = userProfile.objects.get(user=user) 
    args = {'user': user, 'bookList': bookList, 'profile': profile}
    args.update(csrf(request))
    return render_to_response('userAuth/profile.html', args, context)


@login_required
def user_logout(request):
	# Since we know the user is loggin in, we can now just log them out.
	logout(request)

	# Take the user back to the homepage.
	return HttpResponseRedirect('/')

@csrf_exempt	
def addPic(request):
	user = request.user
	picture = request.FILES['picture']
	add_profile_pic(user, picture)
	return HttpResponse()

def addBook(request):

	user = request.user
	bCover = request.FILES['cover'] 
	c_srf = {'user': user}
	c_srf.update(csrf(request))
	bTitle = str(request.POST.get('title'))
	bPoints = str(request.POST.get('points'))
	bAuthor = str(request.POST.get('author'))
	bDescription = str(request.POST.get('description'))
	bGenre = str(request.POST.get('genre'))
	add_user_book(user, bCover, bTitle, bPoints, bAuthor, bDescription, bGenre)
	
	return HttpResponseRedirect('/bookshelf/')

@csrf_exempt	
def badWord(request):
	user = request.user
	badWord = str(request.POST.get('badword'))
	add_bad_word(user, badWord)
	jsonObj = {}
	jsonObj['\'user\''] = user.username
	jsonObj['\'badWord\''] = badWord
	return JsonResponse(jsonObj)	

