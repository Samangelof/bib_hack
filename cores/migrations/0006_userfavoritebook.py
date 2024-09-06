# Generated by Django 5.1.1 on 2024-09-06 19:54

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cores', '0005_alter_userlikedcategories_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserFavoriteBook',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorited_by', to='cores.book')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='favorite_books', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Favorite Book',
                'verbose_name_plural': 'Favorite Books',
                'unique_together': {('user', 'book')},
            },
        ),
    ]
