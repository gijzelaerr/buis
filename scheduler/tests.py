from django.test import TestCase
from .models import Repository
from django.urls import reverse
from django.contrib.auth import get_user_model
from toil.cwl import cwltoil
from pathlib import Path
from tempfile import NamedTemporaryFile
import json

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

    def test_toil(self):
        workflow = str((HERE / "../testdata/sleep.cwl").resolve())
        job_dict = {'seconds': 1}

        with NamedTemporaryFile(mode='wt') as tf:
            json.dump(job_dict, tf.file)
            tf.file.flush()
            args = [workflow, tf.name]
            cwltoil.main(args=args)
