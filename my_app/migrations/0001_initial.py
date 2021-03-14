# Generated by Django 3.1.7 on 2021-03-14 17:02

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import my_app.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('file', models.FileField(blank=True, null=True, upload_to=my_app.models.upload_logo)),
            ],
            options={
                'db_table': 'invoices',
            },
        ),
        migrations.CreateModel(
            name='InvoiceDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.CharField(blank=True, max_length=36, null=True, unique=True)),
                ('status', models.CharField(choices=[('s', 'Success'), ('f', 'Failed'), ('x', 'N/A')], default='x', max_length=2)),
                ('amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('coefficient', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('selling_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('meta', django.contrib.postgres.fields.jsonb.JSONField(default={'errors': []})),
                ('due_date', models.DateField(blank=True, null=True)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='my_app.invoice')),
            ],
            options={
                'db_table': 'invoices_detail',
            },
        ),
    ]
