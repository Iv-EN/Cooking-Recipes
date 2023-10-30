import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag

NAME_MODEL_FILE = {
    'ingredient': (Ingredient, 'ingredients.csv'),
    'tags': (Tag, 'tag.csv'),
}


class Command(BaseCommand):
    help = 'Load data from csv file to model.'

    @staticmethod
    def get_csv_file(filename):
        return os.path.join(settings.BASE_DIR, 'data', filename)

    @staticmethod
    def clear_model(model):
        model.objects.all().delete()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def print_to_terminal(self, message):
        self.stdout.write(self.style.SUCCESS(message))

    def load_model(self, model_name, field_names):
        model, file_path = NAME_MODEL_FILE.get(model_name)
        with open(self.get_csv_file(file_path), encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=',')
            self.clear_model(model)
            line = 0
            for row in reader:
                if ','.join(row).strip() and line >= 0:
                    params = dict(zip(field_names, row))
                    _, created = model.objects.get_or_create(**params)
                line += 1
        self.print_to_terminal(f'{line} objects added to {model_name}')

    def load_ingredient(self):
        self.load_model(
            'ingredient', ['name', 'measurement_unit']
        )

    def load_tags(self):
        self.load_model(
            'tags', ['name', 'color', 'slug']
        )

    def handle(self, *args, **kwargs):
        self.load_ingredient()
        self.load_tags()
