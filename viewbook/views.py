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

        c = RequestContext(request)
        b = book.objects.get(pk=book_id)
        revs = review.objects.filter(book_review=b)
        if(request.user.is_authenticated()):
            r = reader.objects.filter(Q(book=b) & Q(user=request.user))
        else:
            r = reader.objects.none()
        #get books with same genre or author
        #remove this one from list
        related = book.objects.filter(Q(book_author__contains=b.book_author) | Q(genre__contains=b.genre)).exclude(blacklist=True).exclude(pk=book_id).exclude(approved=False)
        
        c['rating'] = weightedRating(book_id)
        
        if request.user.is_authenticated():
            profile = userProfile.objects.get(user=request.user)
            c['user_points'] = profile.points
        else:
            c['user_points'] = 0
        
        if r.count() > 0:
            c['time_left'] = r[0].time_left
            c['time_read'] = r[0].time_read
        else:
            c['time_left'] = 0
            c['time_read'] = 0

        #combine book details and related books into Context
        c['book'] = b
        c['related'] = related
        c['reviews'] = revs

	return render_to_response("viewbook/viewbook.html", c)

def renderreader(request, book_id):
        c = RequestContext(request);
        b = book.objects.get(pk=book_id)
        r = reader.objects.filter(Q(book=b) & Q(user=request.user))
        b.last_opened=now()
        b.save()
        #b = book.objects.get(pk=book_id)
        #get books with same genre or author
        #remove this one from list
        
       
        #combine book details and related books into Context
        if r.count() > 0:
            c['time_left'] = r[0].time_left
        else:
            c['time_left'] = 0
        with open(STATIC_URL + b.book_text.url, 'r') as myfile:
            data=myfile.read().replace('\n', '')
        c['book_text'] = data

        
        c['id'] = book_id
        return render_to_response("viewbook/reader.html", c)


#This is a bad idea if we care about security, but it's all good in the hood.
#It lets post requests happen without authentication.
@csrf_exempt
def purchasebook(request, book_id, price, seconds):    
        purchase(request.user, book_id, price, seconds)

        return HTTPResponse('1')

def purchase(user, book_id, price, seconds):
        b = book.objects.get(pk=book_id)
        #created is required. Do not touch
        readerEntry, created = reader.objects.get_or_create(user=user, book=b)
        readerEntry.time_left = F('time_left') + seconds
        readerEntry.save()
        profile = userProfile.objects.get(user=user)
        profile.points = F('points') - price
        profile.save()
        
@csrf_exempt
def updatetime(request, book_id, seconds):
        b = book.objects.get(pk=book_id)
        #created is required. Do not touch
        readerEntry, created = reader.objects.get_or_create(user=request.user, book=b)
        
        b.time_read = F('time_read') + seconds
        b.save();

        readerEntry.time_read = F('time_read') + seconds
        readerEntry.time_left = F('time_left') - seconds   
        readerEntry.save()
        
        return HTTPResponse('1')

@csrf_exempt
def add_review(request,book_id):
	c = RequestContext(request)
	book_selected = book.objects.get(pk=book_id)
	rev = review(user=request.user,book_review=book_selected,content=request.POST['review'])
	rev.save()
	jsonObj = {}
	jsonObj['\'user\''] = rev.user.username
	jsonObj['\'content\''] = rev.content
	return JsonResponse(jsonObj)
    #return HttpResponse(json.dumps(jsonObj), content_type="application/json")


@csrf_exempt
def update_rating(request,book_id):
	c = RequestContext(request)
	book_selected = book.objects.get(pk=book_id)
        r = reader.objects.get(book=book_selected, user=request.user)
        r.rating = request.POST['rating']
        r.save()
	jsonObj = {}
        jsonObj['rating'] = request.POST['rating']
	return JsonResponse(jsonObj)

@csrf_exempt
def search_curses(request,book_id):
        curses = 0;
	#c = RequestContext(request)
	book_selected = book.objects.get(pk=book_id)
        user = request.user
        with open(book_selected.book_text.url, 'r') as myfile:
            data=myfile.read().replace('\n', '')
        for word in data.split():
            badword = word.encode('ascii','ignore').translate(string.maketrans("",""), string.punctuation)
            if badWords.objects.filter(Q(user=user) & Q(badword__iexact=badword)).count() > 0:
                curses+=1
        return HttpResponse(curses)

@csrf_exempt
def complain(request,book_id):
	#c = RequestContext(request)
	book_selected = book.objects.get(pk=book_id)
        user = request.user
        response = 0
        r = reader.objects.get(book=book_selected, user=request.user)
        if not r.complained:
            r.complained = True
            r.save()
            book_selected.complaints += 1
            book_selected.save()
            if book_selected.complaints >= 3:
                blacklistBook(book_selected)
        else:
            response = -1
         
        return HttpResponse(response)

def blacklistBook(book):
        book.blacklist = True
        profile = userProfile.objects.get(user=book.user)
        profile.points = F('points') - 100
        profile.strikes += 1
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
        book_selected = book.objects.get(pk=float(book_id))
        readers = reader.objects.filter(Q(book=book_selected) & Q(rating__gt=0))

        book_time = sum([readers[i].time_read for i in range(len(readers))])
        rating = 0
        if book_time > 0:
            #this is the most pythonic statement in this entire project
            rating = sum([readers[i].rating * readers[i].time_read for i in range(len(readers))]) / book_time
        return rating

@csrf_exempt
def clean(request):
    books = book.objects.filter(approved=True)
    for b in books:
        #delta time
        #dt=70
        dt = now() - b.last_opened
        #after 10 minutes of no reading, remove book from bookshelf
        if dt.total_seconds() > 240:
        #if dt > 240:
            b.approved=False
            user = userProfile.objects.get(user=b.user)
            user.points = F('points') - 5
            user.save()
            b.save()
    return HttpResponse()
