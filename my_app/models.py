import os
from django.contrib.postgres.fields import JSONField
from django.conf import settings
from django.db import models
# Create your models here.


def upload_logo(instance, filename):
    """
    return file path
    """
    split_name = str(filename).split('.')
    ext = split_name[-1]
    file_name = split_name[0]
    file_dir = os.path.join(settings.MEDIA_ROOT, 'files/')
    if ext == 'csv':
        file_name = file_name + '.' + ext
    if not os.path.isdir(file_dir):
        os.makedirs(file_dir, 0o777)
    return os.path.join('files', file_name)


class Invoice(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to=upload_logo, null=True, blank=True)

    class Meta:
        db_table = 'invoices'

    def __str__(self):
        return '{}'.format(self.name)


class InvoiceDetail(models.Model):
    STATUS = (
        ('s', 'Success'),
        ('f', 'Failed'),
        ('x', 'N/A'),
    )
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    uuid = models.CharField(max_length=36, unique=True, null=True, blank=True)
    # if any record has the same invoice id. need to show error on UI for this.
    status = models.CharField(choices=STATUS, default='x', max_length=2)
    amount = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
    coefficient = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(default=0.00, max_digits=10, decimal_places=2)
    meta = JSONField(default={'errors': []})
    due_date = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'invoices_detail'

    def __str__(self):
        return '{} - {}'.format(self.invoice.name, dict(self.STATUS).get(self.status))
