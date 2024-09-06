import openpyxl
from django.core.management.base import BaseCommand
from cores.models import Book


class Command(BaseCommand):
    help = 'Получение всех уникальных категорий и запись в Excel файл'

    def handle(self, *args, **kwargs):
        # Шаг 1: Получить все уникальные категории
        unique_categories = set()

        # Проходим по всем книгам и собираем категории
        books = Book.objects.exclude(categories__isnull=True).exclude(categories__exact='')

        for book in books:
            # Предполагаем, что категории разделены запятыми
            categories_list = book.categories.split(',')
            for category in categories_list:
                unique_categories.add(category.strip())  # Добавляем уникальные категории, убирая лишние пробелы

        # Шаг 2: Создание и запись в Excel файл
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Уникальные категории"

        # Добавляем заголовок
        sheet.append(['Категория'])

        # Записываем уникальные категории в файл
        for category in sorted(unique_categories):
            sheet.append([category])

        # Шаг 3: Сохранить Excel файл
        output_file = 'unique_categories.xlsx'
        workbook.save(output_file)

        self.stdout.write(self.style.SUCCESS(f'Уникальные категории успешно записаны в файл {output_file}'))
