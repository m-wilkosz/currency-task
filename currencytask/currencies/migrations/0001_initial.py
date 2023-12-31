# Generated by Django 4.2 on 2023-11-19 13:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('code', models.CharField(max_length=3, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='ExchangeRate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField()),
                ('exchange_rate', models.DecimalField(decimal_places=4, max_digits=10)),
                ('interval', models.CharField(max_length=2)),
                ('first_currency_code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exchange_first_code', to='currencies.currency')),
                ('second_currency_code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exchange_second_code', to='currencies.currency')),
            ],
        ),
    ]
