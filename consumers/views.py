from django.urls import reverse
from rest_framework import generics, pagination
from rest_framework.response import Response
from io import StringIO
import requests
import csv

from .models import Consumer
from .serializers import ConsumerSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.decorators import api_view
from django_consumer_api.rate_limit_decorator import rate_limit

class ConsumerPagination(pagination.PageNumberPagination):
    page_size = 10

class ConsumerListView(generics.ListAPIView):
    serializer_class = ConsumerSerializer
    pagination_class = ConsumerPagination

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('min_previous_jobs_count', openapi.IN_QUERY, description="Minimum number of previous jobs held.", type=openapi.TYPE_INTEGER),
            openapi.Parameter('max_previous_jobs_count', openapi.IN_QUERY, description="Maximum number of previous jobs held.", type=openapi.TYPE_INTEGER),
            openapi.Parameter('previous_jobs_count', openapi.IN_QUERY, description="Exact number of previous jobs held.", type=openapi.TYPE_INTEGER),
            openapi.Parameter('status', openapi.IN_QUERY, description="Status of the debt collected.", type=openapi.TYPE_STRING),
        ],
        responses={200: ConsumerSerializer(many=True)}
    )
    @rate_limit(rate=2)
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
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

    def get_paginated_response(self, data):
        # Constructing the next and prev links for pagination using web linking
        next_url = None
        prev_url = None
        base_url = self.request.build_absolute_uri(reverse('consumer-list'))
        query_params = self.request.GET.copy()  # Get a copy of current query parameters

        if self.paginator.get_next_link():
            next_page_number = self.paginator.page.number + 1
            query_params['page'] = next_page_number
            next_url = f"{base_url}?{query_params.urlencode()}"
        if self.paginator.get_previous_link():
            previous_page_number = self.paginator.page.number - 1
            query_params['page'] = previous_page_number
            prev_url = f"{base_url}?{query_params.urlencode()}"

        return Response({
            'next': next_url,
            'prev': prev_url,
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
