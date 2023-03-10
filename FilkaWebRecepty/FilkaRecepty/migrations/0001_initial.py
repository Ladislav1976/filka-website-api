# Generated by Django 4.1 on 2023-01-10 17:11

import FilkaRecepty.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FoodTags',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('foodTag', models.CharField(max_length=60)),
            ],
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ingredient', models.CharField(max_length=60, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Steps',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('step', models.CharField(max_length=500, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unit', models.CharField(max_length=60, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Ingredients',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('volume', models.CharField(max_length=60)),
                ('ingredientName', models.ManyToManyField(related_name='ingredientName', to='FilkaRecepty.ingredient')),
                ('units', models.ManyToManyField(related_name='units', to='FilkaRecepty.unit')),
            ],
        ),
        migrations.CreateModel(
            name='Foods',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60)),
                ('image', models.ImageField(blank=True, null=True, upload_to=FilkaRecepty.models.get_upload_path, verbose_name='Food image')),
                ('date', models.DateField()),
                ('foodTags', models.ManyToManyField(related_name='foodTags', to='FilkaRecepty.foodtags')),
                ('ingredients', models.ManyToManyField(related_name='ingredients', to='FilkaRecepty.ingredients')),
                ('steps', models.ManyToManyField(related_name='steps', to='FilkaRecepty.steps')),
            ],
        ),
    ]
