# Generated by Django 5.0.2 on 2024-02-07 22:33

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Consumer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('street', models.CharField(max_length=255)),
                ('status', models.CharField(max_length=100)),
                ('previous_jobs_count', models.PositiveIntegerField()),
                ('amount_due', models.DecimalField(decimal_places=2, max_digits=10)),
                ('lat', models.FloatField()),
                ('lng', models.FloatField()),
            ],
            options={
                'db_table': 'consumer',
            },
        ),
    ]
