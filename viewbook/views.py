from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import Context
from django.template import RequestContext
from django.db.models import Q
from django.db.models import F
from books.models import book, review
from viewbook.models import reader
from userAuth.models import userProfile
from userAuth.models import badWords
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.contrib.auth.models import User
from viewbook.models import invite
from django.utils.timezone import now
import json
import string
import math
import os.path

# Create your views here.
def renderviewbook(request, book_id):
        #needed for authentication stuff
        c = RequestContext(request)
        #get reviews list and put it into the context
        b = book.objects.get(pk=book_id)
        revs = review.objects.filter(book_review=b)
        c['reviews'] = revs
        #if the user is autheticated, get that user's reader object list (one element). Also get the user's points
        #otherwise, get an empty list. There will be 0 points available for guest, therefore, they can't purchase
        if(request.user.is_authenticated()):
            r = reader.objects.filter(Q(book=b) & Q(user=request.user))
            profile = userProfile.objects.get(user=request.user)
            c['user_points'] = profile.points
        else:
            r = reader.objects.none()
            c['user_points'] = 0
        #get books with same genre or author
        #remove this one from list
        related = book.objects.filter(Q(book_author__contains=b.book_author) | Q(genre__contains=b.genre)).exclude(blacklist=True).exclude(pk=book_id).exclude(approved=False)
        
        #get the weighted rating for this book
        c['rating'] = weightedRating(book_id)
        
        #put appropriate time_left and time_read into the context
        if r.count() > 0:
            c['time_left'] = r[0].time_left
            c['time_read'] = r[0].time_read
        else:
            c['time_left'] = 0
            c['time_read'] = 0

        #combine book details and related books into Context
        c['book'] = b
        c['related'] = related

	return render_to_response("viewbook/viewbook.html", c)

def renderreader(request, book_id):
        #get the reader object associated with this user and book
        c = RequestContext(request);
        b = book.objects.get(pk=book_id)
        r = reader.objects.filter(Q(book=b) & Q(user=request.user))
        #update this book's last read time
        b.last_opened=now()
        b.save()
        
        #put time_left into the context
        if r.count() > 0:
            c['time_left'] = r[0].time_left
        else:
            c['time_left'] = 0
        #heroku might complain about the path, so we get an absolute path
        DIR_T = os.path.abspath(os.path.dirname(__name__))
        #open file in absolute path. replace %20 in string with a space...
        with open(os.path.join(DIR_T, b.book_text.url).replace("%20", " "), 'r') as myfile:
            data=myfile.read().replace('\n', '')
        #put the book contents onto the returned context
        c['book_text'] = data

        #put the id into the context
        c['id'] = book_id
        return render_to_response("viewbook/reader.html", c)


#This is a bad idea if we care about security, but it's all good in the hood.
#It lets post requests happen without authentication.
@csrf_exempt
def purchasebook(request, book_id, price, seconds):
        #make the purchase
        purchase(request.user, book_id, price, seconds)

        return HTTPResponse('1')

def purchase(user, book_id, price, seconds):
        b = book.objects.get(pk=book_id)
        #created is required. Do not touch. It returns a 2-tuple
        #get or create a reader object for this book and user
        readerEntry, created = reader.objects.get_or_create(user=user, book=b)
        #add time for the user to reader this book
        readerEntry.time_left = F('time_left') + seconds
        readerEntry.save()
        #deduct points used to pay for this book
        profile = userProfile.objects.get(user=user)
        profile.points = F('points') - price
        profile.save()
        
@csrf_exempt
def updatetime(request, book_id, seconds):
        b = book.objects.get(pk=book_id)
        #get the reader object for this book and user
        readerEntry = reader.objects.get(user=request.user, book=b)
        #add time to the book and save
        #should remove this property since it is not used anymore
        b.time_read = F('time_read') + seconds
        b.save();
        #add to the user's total time reading this book and subtract from their time left for this book
        readerEntry.time_read = F('time_read') + seconds
        readerEntry.time_left = F('time_left') - seconds   
        readerEntry.save()
        
        return HTTPResponse('1')

@csrf_exempt
def add_review(request,book_id):
        #create a new review object for this user and book
	book_selected = book.objects.get(pk=book_id)
	rev = review(user=request.user,book_review=book_selected,content=request.POST['review'])
	rev.save()
	#return a json object. Not sure why we can't use it in the js success function.
        jsonObj = {}
	jsonObj['\'user\''] = rev.user.username
	jsonObj['\'content\''] = rev.content
	return JsonResponse(jsonObj)
    #return HttpResponse(json.dumps(jsonObj), content_type="application/json")


@csrf_exempt
def update_rating(request,book_id):
        #get the reader object associated with this book and user
        book_selected = book.objects.get(pk=book_id)
        r = reader.objects.get(book=book_selected, user=request.user)
        #update the rating with the rating submitted by the user
        r.rating = request.POST['rating']
        r.save()
        #return a json object. Not sure why we can't use it in the js success function.
	jsonObj = {}
        jsonObj['rating'] = request.POST['rating']
	return JsonResponse(jsonObj)

@csrf_exempt
def search_curses(request,book_id):
        #initialize the number of bad words counter
        curses = 0;
        #get the book entry and the user
	book_selected = book.objects.get(pk=book_id)
        user = request.user
        #heroku might complain about the path, so we get an absolute path
        DIR_T = os.path.abspath(os.path.dirname(__name__))
        #open file in absolute path. replace %20 in string with a space...
        with open(os.path.join(DIR_T, book_selected.book_text.url).replace("%20", " "), 'r') as myfile:
            data=myfile.read().replace('\n', '')
        #tokenize the book's contents and query the user's badWords table entries
        for word in data.split():
            #the word needs to be stripped of puntuation
            badword = word.encode('ascii','ignore').translate(string.maketrans("",""), string.punctuation)
            #the query needs to be case insensitive
            if badWords.objects.filter(Q(user=user) & Q(badword__iexact=badword)).count() > 0:
                #increment the bad words count if this word was found in the table
                curses+=1
        #returns the number of curses
        return HttpResponse(curses)

@csrf_exempt
def complain(request,book_id):
	#get the book, the user, and the reader object to store the complaint in, and initialize response
        book_selected = book.objects.get(pk=book_id)
        user = request.user
        response = 0
        r = reader.objects.get(book=book_selected, user=request.user)
        #if the user has not complained yet, add to the book's complaints
        if not r.complained:
            r.complained = True
            r.save()
            book_selected.complaints += 1
            book_selected.save()
            #if this is the 3rd or moreth complaint, blacklist the book
            if book_selected.complaints >= 3:
                blacklistBook(book_selected)
                response = 1
        else:
            response = -1
         
        #return 0 for complaint processed, -1 for complaint was already there, and 1 for book removed
        return HttpResponse(response)

def blacklistBook(book):
        #blacklist the selected book
        book.blacklist = True
        #get the uploader's profile and deduct 100 points and add 1 strike
        profile = userProfile.objects.get(user=book.user)
        profile.points = F('points') - 100
        profile.strikes += 1
        #if there are 2 or more strikes, blacklist the user
        if profile.strikes >= 2:
            profile.blacklist = True
        profile.save()
        book.save()

def sendInvite(request, book_id):
        #return status (assumes existing invite)
        ok=0
        #get book
        book_selected = book.objects.get(pk=book_id)
        #calculate the cost for the desired time
        cost= math.floor((float(book_selected.book_points) * (1 + (math.sqrt(float(request.POST['time'])/10) * 1.5))/2))
        #get friend
        to_usr = User.objects.filter(username=request.POST['buddy'])

        #if friend exists

        if to_usr.count()>0:
            #if invitation is not already pending, create it
            inv, created = invite.objects.get_or_create(book=book_selected, to_usr=to_usr[0], from_usr=request.user, pending=True)
            if created:
                #add cost and time to the invite and set return status to ok
                inv.cost = cost
                inv.time = request.POST['time']
                inv.save()
                ok=1
        else:
            ok=-1
        return HttpResponse(ok)
    

def acceptinvite(request, book_id, friend_id):
        #get invitation entry
        book_selected = book.objects.get(pk=book_id)
        from_usr = User.objects.get(pk=friend_id)
        inv = invite.objects.get(book=book_selected, to_usr=request.user, from_usr=from_usr, pending=True)
        #reset pending flag and save
        inv.pending=False
        inv.save()

        #purchase the book for inviter and invitee
        purchase(from_usr, book_id, inv.cost, inv.time)
        purchase(request.user, book_id, inv.cost, inv.time)

        #load the book
        return renderreader(request, book_id)

def weightedRating(book_id):
        #gets weighted rating
        #get the book to search for all reader objects with a rating greater than 0
        book_selected = book.objects.get(pk=float(book_id))
        readers = reader.objects.filter(Q(book=book_selected) & Q(rating__gt=0))

        #get the denominator for avg and initialize rating
        book_time = sum([readers[i].time_read for i in range(len(readers))])
        rating = 0
        # denominator is not 0 compute the weighted rating.
        # if book has not been rated, book_time would be 0
        if book_time > 0:
            #this is the most pythonic statement in this entire project
            rating = sum([readers[i].rating * readers[i].time_read for i in range(len(readers))]) / book_time
        return rating

@csrf_exempt
def clean(request):
    books = book.objects.filter(approved=True)
    for b in books:
        #delta time
        dt = now() - b.last_opened
        #after 4 minutes of no reading, remove book from bookshelf
        if dt.total_seconds() > 240:
            b.approved=False
            #also deduct 5 points from user
            user = userProfile.objects.get(user=b.user)
            user.points = F('points') - 5
            user.save()
            b.save()
    #no response necessary
    return HttpResponse()
