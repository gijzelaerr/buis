from django.test import TestCase
from .models import Repository
from django.urls import reverse


def create_repository(url):
    return Repository.objects.create(url=url)


class RepositoryIndexViewTests(TestCase):
    def test_no_repositories(self):
        """
        If no repo exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('scheduler:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No repositories are available.")
        self.assertQuerysetEqual(response.context['object_list'], [])

    def test_multiple_repositories(self):
        """
        The index page should display multiple questions.
        """
        create_repository('git@bla')
        create_repository('git@bla')
        response = self.client.get(reverse('scheduler:index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(list(response.context['object_list'])), 2)


