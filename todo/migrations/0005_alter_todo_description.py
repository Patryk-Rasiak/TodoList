# Generated by Django 4.0.3 on 2022-06-07 09:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0004_alter_todo_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='todo',
            name='description',
            field=models.TextField(blank=True, default=''),
        ),
    ]
