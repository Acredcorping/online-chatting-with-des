# Generated by Django 4.1 on 2023-05-23 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0005_application'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='remark',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='备注'),
        ),
    ]
