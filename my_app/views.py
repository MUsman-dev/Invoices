import pandas as pd
import datetime
from django.db import IntegrityError
from rest_framework import generics, status
from rest_framework.response import Response

from my_app.models import Invoice, InvoiceDetail
from .serializers import InvoiceSerializer, InvoiceDetailSerializer
from rest_framework.pagination import PageNumberPagination


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class InvoiceListView(generics.ListCreateAPIView):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = []
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        try:
            file = request.FILES.get('file', None)
            if not file:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={"message": "Attachment missing !!!",
                                                                          "status": 'FAILED'})
            if file.name.split('.')[1] != 'csv':
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={"message": "Attachment Type should be csv !!!", "status": 'FAILED'})

            serializer = self.get_serializer(data=request.data)

            if serializer.is_valid(raise_exception=True):
                instance = serializer.save()
                today = datetime.datetime.today().date()

                with pd.read_csv(instance.file, chunksize=900) as reader:
                    row_counter = 1
                    for chunk in reader:
                        for row in chunk.values:
                            row_counter += 1
                            try:
                                attrs = dict(meta=dict(errors=[], data=[]))
                                attrs['invoice_id'] = instance.pk
                                attrs['status'] = 's'

                                try:
                                    attrs['uuid'] = str(row[0]).strip()
                                except (KeyError, ValueError, IndexError):
                                    attrs.pop('uuid', None)
                                    attrs['meta']['errors'].append('Invalid Invoice ID')
                                    attrs['meta']['row_Id'] = row_counter
                                    attrs['status'] = 'f'
                                try:
                                    attrs['amount'] = float(str(row[1]).strip())
                                except (KeyError, ValueError, IndexError):
                                    attrs.pop('uuid', None)
                                    attrs['meta']['errors'].append('Invalid Amount')
                                    attrs['meta']['row_id'] = row_counter
                                    attrs['status'] = 'f'

                                due_date = None
                                try:
                                    due_date = datetime.datetime.strptime(str(row[2]).strip(), '%Y-%m-%d')
                                    attrs['due_date'] = due_date.date()
                                except (KeyError, ValueError, IndexError, Exception):
                                    attrs.pop('uuid', None)
                                    attrs['meta']['errors'].append('Invalid due date')
                                    attrs['meta']['row_id'] = row_counter
                                    attrs['status'] = 'f'

                                try:
                                    if due_date:
                                        days = (today - due_date.date()).days
                                        attrs['coefficient'] = 0.3 if days <= 30 else 0.5
                                        attrs['selling_price'] = float(str(row[1]).strip()) * attrs['coefficient']

                                except (KeyError, ValueError, IndexError):
                                    attrs.pop('uuid', None)
                                    attrs['meta']['errors'].append('Invalid Selling Price Amount')
                                    attrs['meta']['row_id'] = row_counter
                                    attrs['status'] = 'f'

                                InvoiceDetail.objects.create(**attrs)

                            except IntegrityError as ex:
                                attrs.pop('uuid', None)
                                attrs['amount'] = 0.0
                                attrs['coefficient'] = 0.0
                                attrs['selling_price'] = 0.0
                                attrs['status'] = 'f'
                                attrs['meta']['errors'].append("Invoice should be unique !!")
                                attrs['meta']['row_id'] = row_counter
                                InvoiceDetail.objects.create(**attrs)

                            except Exception as ex:
                                attrs.pop('uuid', None)
                                attrs['amount'] = 0.0
                                attrs['coefficient'] = 0.0
                                attrs['selling_price'] = 0.0
                                attrs['status'] = 'f'
                                attrs['meta']['errors'].append("Please Correct the data on Row : {}".
                                                               format(row_counter))
                                attrs['meta']['row_id'] = row_counter
                                InvoiceDetail.objects.create(**attrs)
                        # chunk.to_csv('final.csv', mode='a', header=write_header, index=False)

                return Response(status=status.HTTP_201_CREATED, data=serializer.data)
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"message": serializer.errors, 'status': "FAILED"})
        except Exception as ex:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"message": repr(ex), 'status':'FAILED'})


class InvoiceDetailView(generics.ListAPIView):
    serializer_class = InvoiceDetailSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = []
    authentication_classes = []

    def get_queryset(self):
        pk = self.kwargs.get('pk', None)
        if pk:
            return InvoiceDetail.objects.filter(invoice_id=pk).select_related('invoice')
        return InvoiceDetail.objects.all().select_related('invoice')
