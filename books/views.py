from django.shortcuts import render
from django.shortcuts import render_to_response
from books.models import book
from django.http import HttpResponseRedirect, HttpResponse
from viewbook.models import invite
from django.db.models import Q
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

def index(request):
	bookList = book.objects.all().exclude(blacklist=True).exclude(approved=False)
	context = {'bookList': bookList}
	return render(request, "books/bookshelf.html", context)


#class bookList(ListView):
#    model = book

#    def get_context_data(self):
#        context = super(bookList, self).get_context_data("*")
#        return context
def renderbookshelf(request):	
	return index(request)
#	return render_to_response("books/bookshelf.html")

@csrf_exempt
def rendersearch(request):
        q = str(request.POST.get('q'))
	bookList = book.objects.filter(Q(book_author__contains=q) | Q(genre__contains=q) |
                Q(book_title__contains=q) | Q(details__contains=q) | Q(description__contains=q) |
                Q(book_text__contains=q)).exclude(blacklist=True).exclude(approved=False)
	context = {'bookList': bookList}
        return render(request, "books/bookshelf.html", context)

def invites(request):
    c = RequestContext(request)
    c['invites'] = invite.objects.filter(Q(to_usr=request.user) & Q(pending=True))
    return render_to_response("books/invites.html", c)

def contribute_book(request):
	if request.method == 'POST':
		book(book_title=request.POST['title'],
			user=request.user,
			book_author=request.POST['author'],
			description = request.POST['description'],
			details = request.POST['detail'],
			cover=request.FILES['cover_image'],
			alt_text=request.POST['alt_text'],
			genre=request.POST['genre'],
			book_text=request.FILES['book_text']
		).save()
		return HttpResponseRedirect('/bookshelf')
	else:
		return render(request, "books/upload.html", {})
