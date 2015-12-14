from django.shortcuts import render
from django.shortcuts import render_to_response
from books.models import book
from django.http import HttpResponseRedirect, HttpResponse

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

def contribute_book(request):
	if request.method == 'POST':
		book(book_title=request.POST['title'],
			user=request.user,
			book_author=request.POST['auther'],
			description = request.POST['description'],
			details = request.POST['detail'],
			cover=request.FILES['cover_image'],
			alt_text=request.POST['alt_text'],
			genre=request.POST['genre']
		).save()
		return HttpResponseRedirect('/bookshelf')
	else:
		return render(request, "books/upload.html", {})
