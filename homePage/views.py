from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext
from viewbook.models import reader
from books.models import book


# Create your views here.
def renderHome(request):
	context = RequestContext(request)
        if request.user.is_authenticated:
            readerEntrys= reader.objects.filter(user=request.user.id)
            if readerEntrys.count() > 0:
                context['recommend'] = book.objects.filter(genre=readerEntrys[0].book.genre).exclude(blacklist=True).exclude(approved=False)
            else:
                context['recommend'] = book.objects.all().exclude(blacklist=True).exclude(approved=False)
        else:
            context['recommend'] = book.objects.all().exclude(blacklist=True).exclude(approved=False)
        # No context variables to pass to the template system, hence the 
	# blank dictionary object
	return render_to_response('homePage/home.html', {}, context)
