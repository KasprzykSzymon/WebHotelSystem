# Generated by Django 5.1.3 on 2024-12-28 20:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotelSystem', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='RoomImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='room_images/')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='hotelSystem.room')),
            ],
        ),
    ]
