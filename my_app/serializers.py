from rest_framework import serializers
from my_app.models import Invoice, InvoiceDetail

status_mapping = dict((
        ('s', 'Success'),
        ('f', 'Failed'),
        ('x', 'N/A'),
    ))


class InvoiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Invoice
        fields = '__all__'


class InvoiceDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceDetail
        fields = '__all__'

    def to_representation(self, instance):
        r = super(InvoiceDetailSerializer, self).to_representation(instance)
        r.pop("id", None)
        r['status'] = status_mapping.get(r['status'])
        meta = r.pop("meta", {})
        r['errors'] = meta.get('errors', [])
        r['row_id'] = meta.get('row_id', None)
        return r
