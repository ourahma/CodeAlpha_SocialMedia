# Generated by Django 5.0.6 on 2024-09-25 19:25

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socialmediaapp', '0008_friendrequest'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='friend_requests',
            field=models.ManyToManyField(blank=True, related_name='friend_requests', to=settings.AUTH_USER_MODEL),
        ),
    ]
