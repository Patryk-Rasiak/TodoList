# Generated by Django 4.0.3 on 2022-06-18 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0006_alter_todo_category_alter_todo_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='todo',
            name='category',
            field=models.TextField(blank=True, default='All', null=True),
        ),
    ]
