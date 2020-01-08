from django.core.management.base import BaseCommand, CommandError
from scheduler.models import Dataset


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        parser.add_argument('path', type=str)
        parser.add_argument('description', type=str)

    def handle(self, *args, **options):

        path = options['path']
        description = options['description']

        dataset = Dataset(path=path, description=description)

        try:
            dataset.save()
        except AssertionError as e:
            raise CommandError(str(e))
        self.stdout.write(self.style.SUCCESS(f'Successfully added dataset {path} ({dataset.type}) with id {dataset.id}'))
