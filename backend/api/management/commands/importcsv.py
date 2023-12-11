import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag

NAME_MODEL_FILE = {
    'ingredient': (Ingredient, 'ingredients.csv'),
    'tag': (Tag, 'tag.csv'),
}


class Command(BaseCommand):
    '''Загрузка данных из csv файлов в модели.'''

    @staticmethod
    def get_csv_file(filename):
        return os.path.join(settings.BASE_DIR, 'data', filename)

    @staticmethod
    def clear_model(model):
        model.objects.all().delete()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def load_model(self, model_name, field_names):
        model, file_path = NAME_MODEL_FILE.get(model_name)
        with open(self.get_csv_file(file_path), encoding='utf-8') as file:
            reader = csv.reader(file, delimiter=',')
            self.clear_model(model)
            line = 0
            for row in reader:
                if row != '' and line > 0:
                    params = dict(zip(field_names, row))
                    _, created = model.objects.get_or_create(**params)
                line += 1

    def load_ingredient(self):
        self.load_model(
            'ingredient',
            ['name', 'measurement_unit']
        )

    def load_tag(self):
        self.load_model(
            'tag',
            ['name', 'color', 'slug']
        )

    def handle(self, *args, **kwargs):
        self.load_ingredient()
        self.load_tag()
