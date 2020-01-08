# Generated by Django 2.1.15 on 2020-01-08 09:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0009_workflow_command'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dataset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('path', models.CharField(max_length=400)),
                ('description', models.CharField(max_length=100)),
                ('type', models.CharField(choices=[('DIR', 'Directory'), ('FILE', 'File')], default='FILE', max_length=4)),
            ],
        ),
    ]
