import logging
import os
import pandas as pd
from django.conf import settings
from django.contrib.auth import logout
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from .models import Company_data
from functools import wraps
import time
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Company_data
from .serializers import CompanySerializer, QueryParamsSerializer
from django.shortcuts import render
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import models
from .serializers import QueryParamsSerializer
from .forms import QueryForm
logger = logging.getLogger(__name__)

# Custom decorator to log execution time
def log_execution_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        logger.info(f"{func.__name__} executed in {execution_time:.4f} seconds")
        return result
    return wrapper

class TemporaryFileHandler:
    @staticmethod
    def get_temp_file_path(upload_id):
        """
        Get the path to the temporary binary file for the upload.
        """
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp_chunks')
        os.makedirs(temp_dir, exist_ok=True)
        return os.path.join(temp_dir, f'{upload_id}.tmp')

class ChunkedUploadView(View):
    http_method_names = ['post']

    @log_execution_time
    def post(self, request, *args, **kwargs):
        try:
            upload_id = request.POST.get('upload_id')
            chunk_number = int(request.POST.get('chunk_number'))
            total_chunks = int(request.POST.get('total_chunks'))
            file = request.FILES.get('file')

            if not file:
                return JsonResponse({'error': 'No file found in request'}, status=400)

            # Save chunk data to the temporary binary file
            self.save_chunk(file, upload_id, chunk_number)

            # Check if this is the last chunk
            if chunk_number == total_chunks - 1:
                # Last chunk, process and save to database
                temp_file_path = TemporaryFileHandler.get_temp_file_path(upload_id)
                self.process_and_save(temp_file_path)

                # Clean up temporary files after processing
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)

            return JsonResponse({'message': 'Chunk uploaded successfully'}, status=200)

        except Exception as e:
            logger.error(f"Error in post method: {e}")
            return JsonResponse({'error': str(e)}, status=500)


    @log_execution_time
    def save_chunk(self, file, upload_id, chunk_number):
        """
        Save chunk data to a temporary binary file.
        """
        try:
            temp_file_path = TemporaryFileHandler.get_temp_file_path(upload_id)
            mode = 'ab' if os.path.exists(temp_file_path) else 'wb'

            with open(temp_file_path, mode) as temp_file:
                for chunk in file.chunks():
                    temp_file.write(chunk)

        except Exception as e:
            logger.error(f"Error saving chunk {chunk_number}: {e}")
            raise Exception(f"Error saving chunk {chunk_number}: {e}")

    @log_execution_time
    def process_and_save(self, temp_file_path):
        """
        Process and save the assembled binary file data to the database.
        """
        try:
            # Read the assembled binary file as a CSV
            df_all = pd.read_csv(temp_file_path, low_memory=False)

            # Transform data if necessary
            df_all = self.transform_data(df_all)

            # Save to database
            self.save_to_database(df_all)

            logger.info("Data processed and saved successfully.")

        except pd.errors.ParserError as pe:
            logger.error(f"Error parsing assembled CSV file: {pe}")
            raise ValueError("Error parsing assembled CSV file")
        except Exception as e:
            logger.error(f"Error processing and saving data: {e}")
            raise Exception(f"Error processing and saving data: {e}")

    @log_execution_time
    def transform_data(self, df):
        """
        Transform CSV data if necessary.
        """
        try:
            df['year founded'] = pd.to_numeric(df['year founded'], errors='coerce')
            df['current employee estimate'] = pd.to_numeric(df['current employee estimate'], errors='coerce')
            df['total employee estimate'] = pd.to_numeric(df['total employee estimate'], errors='coerce')

            # Log rows where conversion failed
            problematic_rows = df[df['year founded'].isna() | df['current employee estimate'].isna() | df['total employee estimate'].isna()]
            if not problematic_rows.empty:
                logger.warning(f"Problematic rows found: {problematic_rows}")

            # Drop rows with any null values
            df.dropna(inplace=True)

            # Split locality into city and state
            df[['city', 'state']] = df['locality'].str.split(',', expand=True, n=1)

            df.drop(columns=['locality'], inplace=True)

            # Convert to int
            df['year founded'] = df['year founded'].astype(int)
            df['current employee estimate'] = df['current employee estimate'].astype(int)
            df['total employee estimate'] = df['total employee estimate'].astype(int)

            return df

        except Exception as e:
            logger.error(f"Error transforming data: {e}")
            raise Exception(f'Error transforming data: {e}')

    @log_execution_time
    def save_to_database(self, df):
        try:
            instances = []
            for _, row in df.iterrows():
                instance = Company_data(
                    name=row['name'],
                    domain=row['domain'],
                    year_founded=row['year founded'],
                    industry=row['industry'],
                    size_range=row['size range'],
                    city=row.get('city', '').strip(),
                    state=row.get('state', '').strip(),
                    country=row['country'],
                    linkedin_url=row.get('linkedin url', '').strip(),
                    current_employee_estimate=row['current employee estimate'],
                    total_employee_estimate=row['total employee estimate']
                )
                instances.append(instance)

            # Bulk create instances
            Company_data.objects.bulk_create(instances)

        except Exception as e:
            logger.error(f"Error saving data to database: {e}")
            raise Exception(f'Error saving data to database: {e}')

def home(request):
    return render(request, 'home.html')

def logout_view(request):
    logout(request)
    return redirect('/')

def base(request):
    return render(request, 'base.html')

def upload_data(request):
    return render(request, 'upload_data.html')



def users(request):
    return render(request, 'users.html')

class QueryBuilderView(View):
    def get(self, request, *args, **kwargs):
        form = QueryForm()
        count = None
        industries = Company_data.objects.values_list('industry', flat=True).distinct()
        years = Company_data.objects.values_list('year_founded', flat=True).distinct()
        countries = Company_data.objects.values_list('country', flat=True).distinct()
        states = Company_data.objects.values_list('state', flat=True).distinct()
        cities = Company_data.objects.values_list('city', flat=True).distinct()

        if request.GET:
            form = QueryForm(request.GET)
            if form.is_valid():
                api_view = CompanyCountView()
                response = api_view.get(request)
                count = response.data.get('count', None) if response.status_code == status.HTTP_200_OK else None

        return render(request, 'query_data.html', {
            'form': form,
            'count': count,
            'industries': industries,
            'years': years,
            'countries': countries,
            'states': states,
            'cities': cities
        })

    def post(self, request, *args, **kwargs):
        form = QueryForm(request.POST)
        if form.is_valid():
            api_view = CompanyCountView()
            response = api_view.get(request)
            count = response.data.get('count', None) if response.status_code == status.HTTP_200_OK else None

            return render(request, 'query_data.html', {
                'form': form,
                'count': count,
                'industries': industries,
                'years': years,
                'countries': countries,
                'states': states,
                'cities': cities
            })

from django.http import JsonResponse
from django.views import View
from .models import Company_data

class DynamicFieldsView(View):
    def get(self, request, *args, **kwargs):
        country = request.GET.get('country')
        state = request.GET.get('state')

        logger.info(f"Requested country: {country}, state: {state}")

        if country:
            states = self.get_states(country)
        else:
            states = []

        if state:
            cities = self.get_cities(state)
        else:
            cities = []

        data = {
            'states': states,
            'cities': cities
        }
        logger.info(f"Returning data: {data}")
        return JsonResponse(data)

    def get_states(self, country):
        states_qs = Company_data.objects.filter(country=country).values_list('state', flat=True).distinct()
        states = list(states_qs)
        return states

    def get_cities(self, state):
        cities_qs = Company_data.objects.filter(state=state).values_list('city', flat=True).distinct()
        cities = list(cities_qs)
        return cities

class CompanyCountView(APIView):
    def get(self, request, *args, **kwargs):
        serializer = QueryParamsSerializer(data=request.GET)
        if serializer.is_valid():
            queryset = self.filter_queryset(serializer.validated_data)
            count = queryset.count()
            return Response({'count': count}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def filter_queryset(self, params):
        queryset = Company_data.objects.all()
        
        if params.get('keyword'):
            keyword = params['keyword']
            queryset = queryset.filter(
                Q(name__icontains=keyword) | 
                Q(linkedin_url__icontains=keyword)
            )
        
        if params.get('city'):
            queryset = queryset.filter(city__icontains=params['city'])
        
        if params.get('employees_from') is not None:
            queryset = queryset.filter(current_employee_estimate__gte=params['employees_from'])
        
        if params.get('employees_to') is not None:
            queryset = queryset.filter(current_employee_estimate__lte=params['employees_to'])
        
        if params.get('industry'):
            queryset = queryset.filter(industry__icontains=params['industry'])
        
        if params.get('year_founded') is not None:
            queryset = queryset.filter(year_founded=params['year_founded'])
        
        if params.get('state'):
            queryset = queryset.filter(state__icontains=params['state'])
        
        if params.get('country'):
            queryset = queryset.filter(country__icontains=params['country'])

        return queryset