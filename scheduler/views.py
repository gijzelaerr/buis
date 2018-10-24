from django.views.generic import ListView, DetailView
from .models import Repository
from .serializers import RepositorySerializer
from django.views.generic.edit import CreateView
from rest_framework.generics import ListCreateAPIView
from wes_client.util import WESClient
from django.conf import settings
from requests.exceptions import ConnectionError
from django.http import HttpResponseServerError
from django.shortcuts import render


class RepositoryIndex(ListView):
    model = Repository


class RepositoryDetail(DetailView):
    model = Repository


class RepositoryCreate(CreateView):
    model = Repository
    fields = ['url']


class RepositoryListCreate(ListCreateAPIView):
    queryset = Repository.objects.all()
    serializer_class = RepositorySerializer


def job_list(request):
    client = WESClient(service={'auth': settings.WES_AUTH, 'proto': settings.WES_PROTO, 'host': settings.WES_HOST})
    try:
        context = client.list_runs()
    except ConnectionError as e:
        return HttpResponseServerError(e)
    else:
        return render(request, 'scheduler/job_list.html', context)


