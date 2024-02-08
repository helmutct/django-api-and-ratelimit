from rest_framework import generics, pagination
from rest_framework.response import Response
from django.urls import reverse
from io import StringIO
import requests
import csv
from .models import Consumer
from .serializers import ConsumerSerializer
from django_consumer_api.rate_limit_decorator import rate_limit
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import api_view

class ConsumerPagination(pagination.PageNumberPagination):
    page_size = 10

class ConsumerListView(generics.ListAPIView):
    serializer_class = ConsumerSerializer
    pagination_class = ConsumerPagination

    @rate_limit(rate=60) # Allow 1 request per minute (60 seconds)
    def get_queryset(self):
        queryset = Consumer.objects.all().order_by('id')

        min_previous_jobs_count = self.request.query_params.get('min_previous_jobs_count')
        max_previous_jobs_count = self.request.query_params.get('max_previous_jobs_count')
        previous_jobs_count = self.request.query_params.get('previous_jobs_count')
        status = self.request.query_params.get('status')

        if min_previous_jobs_count is not None:
            queryset = queryset.filter(previous_jobs_count__gte=min_previous_jobs_count)
        if max_previous_jobs_count is not None:
            queryset = queryset.filter(previous_jobs_count__lte=max_previous_jobs_count)
        if previous_jobs_count is not None:
            queryset = queryset.filter(previous_jobs_count=previous_jobs_count)
        if status is not None:
            queryset = queryset.filter(status=status)

        return queryset

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('min_previous_jobs_count', openapi.IN_QUERY, description="Minimum number of previous jobs held.", type=openapi.TYPE_INTEGER),
            openapi.Parameter('max_previous_jobs_count', openapi.IN_QUERY, description="Maximum number of previous jobs held.", type=openapi.TYPE_INTEGER),
            openapi.Parameter('previous_jobs_count', openapi.IN_QUERY, description="Exact number of previous jobs held.", type=openapi.TYPE_INTEGER),
            openapi.Parameter('status', openapi.IN_QUERY, description="Status of the debt collected.", type=openapi.TYPE_STRING),
        ],
        responses={200: ConsumerSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_paginated_response(self, data):
        # Constructing the next link for pagination using web linking
        next_url = self.request.build_absolute_uri(reverse('consumer-list')) + '?' + self.request.META['QUERY_STRING']
        return Response({
            'next': next_url if self.paginator.get_next_link() else None,
            'results': data
        })

    @api_view(['POST']) 
    @swagger_auto_schema(
        operation_description="Import data from a CSV file.",
        responses={200: "Data imported successfully"}
    )
    def import_data_from_csv(request):
        csv_url = "https://drive.google.com/uc?id=1gzh1GczznM8p-qW0UNm4H9HLnydXnf6Q"
        response = requests.get(csv_url)
        if response.status_code == 200:
            try:
                csv_content = response.text
                csv_reader = csv.DictReader(StringIO(csv_content))
                imported_count = 0
                for row in csv_reader:
                    # Check if consumer already exists based on a unique identifier
                    # For example, you can use a combination of fields like 'street' and 'status'
                    if not Consumer.objects.filter(street=row['id']).exists():
                        Consumer.objects.create(
                            id=int(row['id']),
                            street=row['street'],
                            status=row['status'],
                            previous_jobs_count=int(row['previous_jobs_count']),
                            amount_due=float(row['amount_due']),
                            lat=float(row['lat']),
                            lng=float(row['lng'])
                        )
                        imported_count += 1

                if imported_count > 0:
                    return Response(f"{imported_count} data imported successfully", status=200)
                else:
                    return Response("No new data imported", status=200)
            except Exception as e:
                return Response(f"Failed to import data: {str(e)}", status=500)
        else:
            return Response("Failed to fetch CSV file", status=500)