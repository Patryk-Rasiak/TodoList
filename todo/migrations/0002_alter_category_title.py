# Generated by Django 4.0.3 on 2022-06-01 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='title',
            field=models.CharField(default='None', max_length=100),
        ),
    ]
