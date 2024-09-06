import openpyxl
from django.core.management.base import BaseCommand
from cores.models import Book


class Command(BaseCommand):
    help = 'Импорт данных о книгах из файла Excel'

    def handle(self, *args, **kwargs):
        workbook = openpyxl.load_workbook('./cores/books.xlsx')
        sheet = workbook.active

        # Получаем названия колонок из первой строки
        headers = [cell.value for cell in sheet[1]]
        print(headers)
        print()

        for row in sheet.iter_rows(min_row=2, values_only=True):  # Пропускаем заголовки
            data = dict(zip(headers, row))

            isbn13 = data['isbn13']
            isbn10 = data['isbn10']
            title = data['title']
            subtitle = data.get('subtitle', '')
            authors = data['authors'] or 'Неизвестный автор'
            categories = data.get('categories', '')
            thumbnail = data.get('thumbnail', '')
            description = data.get('description', '')
            published_year = int(data['published_year']) if data['published_year'] else None
            average_rating = float(data['average_rating']) if data['average_rating'] else None
            num_pages = int(data['num_pages']) if data['num_pages'] else None
            ratings_count = int(data['ratings_count']) if data['ratings_count'] else None

            book, created = Book.objects.update_or_create(
                isbn13=isbn13,
                defaults={
                    'isbn10': isbn10,
                    'title': title,
                    'subtitle': subtitle,
                    'authors': authors,
                    'categories': categories,
                    'thumbnail': thumbnail,
                    'description': description,
                    'published_year': published_year,
                    'average_rating': average_rating,
                    'num_pages': num_pages,
                    'ratings_count': ratings_count,
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Книга "{title}" добавлена в базу данных'))
            else:
                self.stdout.write(self.style.WARNING(f'Книга "{title}" уже существует, обновлена'))
