from scheduler.models import Repository
from pathlib import Path
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

USER = 'test'
PASS = 'test'

HERE = Path(__file__).resolve().parent


def create_repository(url):
    return Repository.objects.create(url=url)


class RepositoryIndexViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        user = User.objects.create_user(USER, 'temporary@gmail.com', PASS)

    def test_no_repositories(self):
        """
        If no repo exist, an appropriate message is displayed.
        """
        self.client.login(username=USER, password=PASS)
        response = self.client.get(reverse('scheduler:repo_list'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No repositories are available.")
        self.assertQuerysetEqual(response.context_data['object_list'], [])

    def test_multiple_repositories(self):
        """
        The index page should display multiple questions.
        """
        self.client.login(username=USER, password=PASS)
        create_repository('git@bla')
        create_repository('git@bla')
        response = self.client.get(reverse('scheduler:repo_list'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(list(response.context_data['object_list'])), 2)
