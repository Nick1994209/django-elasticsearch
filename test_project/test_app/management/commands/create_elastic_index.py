from django.core.management import BaseCommand

from ...models import News


class Command(BaseCommand):
    elastic_recreate_for_model = {
        'News': News.es.recreate
    }
    help = 'example ./manage.py create_elastic_index News'

    def add_arguments(self, parser):
        parser.add_argument('model', nargs=1)

    def handle(self, *args, **options):
        model = options['model'][0]
        self.stdout.write('Flush index elasticsearch for model {}'.format(model))
        recreate = self.elastic_recreate_for_model.get(model)
        if not recreate:
            raise Exception

        recreate()
        self.stdout.write(self.style.SUCCESS('Success flush index elasticsearch '
                                             'for model {}'.format(model)))
