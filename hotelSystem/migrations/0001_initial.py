# Generated by Django 5.1.3 on 2024-12-12 18:55

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.CreateModel(
            name='Guest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('phone_number', models.CharField(max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=10, unique=True)),
                ('room_type', models.CharField(choices=[('single', 'Single'), ('double', 'Double'), ('suite', 'Suite')], max_length=10)),
                ('price_per_night', models.DecimalField(decimal_places=2, max_digits=6)),
                ('is_available', models.BooleanField(default=True)),
                ('last_minute_discount', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
            ],
        ),
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('check_in_date', models.DateField()),
                ('check_out_date', models.DateField()),
                ('total_price', models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True)),
                ('guest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hotelSystem.guest')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hotelSystem.room')),
            ],
        ),
        migrations.CreateModel(
            name='SocialApp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('provider', models.CharField(choices=[('google', 'Google'), ('facebook', 'Facebook'), ('github', 'GitHub')], max_length=50)),
                ('name', models.CharField(max_length=100)),
                ('client_id', models.CharField(max_length=255)),
                ('secret', models.CharField(max_length=255)),
                ('sites', models.ManyToManyField(related_name='social_apps', to='sites.site')),
            ],
            options={
                'unique_together': {('provider', 'client_id')},
            },
        ),
    ]
