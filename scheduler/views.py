from django.views import generic
from .models import Repository


class IndexView(generic.ListView):
    model = Repository


class DetailView(generic.DetailView):
    model = Repository