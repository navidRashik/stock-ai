# Generated by Django 2.2 on 2023-10-28 13:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TickerUpdate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ltp', models.FloatField(blank=True)),
                ('high', models.FloatField(blank=True)),
                ('low', models.FloatField(blank=True)),
                ('close', models.FloatField(blank=True)),
                ('ycp', models.FloatField(blank=True)),
                ('change', models.FloatField(blank=True)),
                ('trade', models.IntegerField()),
                ('value', models.FloatField(blank=True)),
                ('volume', models.IntegerField()),
                ('updated_at', models.DateTimeField(auto_now_add=True, verbose_name='Updated at')),
                ('ticker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='portfolio.Ticker')),
            ],
        ),
    ]
