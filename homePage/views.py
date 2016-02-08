from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext
from viewbook.models import reader
from viewbook.views import weightedRating
from books.models import book


def renderHome(request):
        #get general context
	context = RequestContext(request)
        #initialize empty QuerySet
        unSorted = book.objects.none()
        #get reader entries of books read by user
        readerEntrys= reader.objects.filter(user=request.user.id)

        #if user is authenticated and has read a book in the past, get a QuerySet of books that are of one of those books' genres
        if request.user.is_authenticated and readerEntrys.count() > 0:
            unSorted = book.objects.filter(genre=readerEntrys[0].book.genre).exclude(blacklist=True).exclude(approved=False)
        else:
            #if user is not authenticated or user did not read anything yet, get a QuerySet of all available books
            unSorted = book.objects.all().exclude(blacklist=True).exclude(approved=False)
        
        #add to the context the list of books, sorted by their rating
        context['recommend'] = sorted(unSorted.all(), key= lambda x: weightedRating(x.id), reverse=True)
        # No context variables to pass to the template system, hence the 
	# blank dictionary object
	return render_to_response('homePage/home.html', {}, context)

def renderAbout(request):
        #get general context
	context = RequestContext(request)
	return render_to_response('homePage/about.html', {}, context)
