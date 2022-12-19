from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.decorators import api_view

from .services import TrainOperatorService, PostMasterService, ParcelService, OptimizerService
from .models import Train, Line, Parcel
from .serializers import LineSerializer, TrainSerializer, ParcelSerializer, ShipmentSerializer

train_operator_service = TrainOperatorService()
parcel_service = ParcelService()
optimizer_service = OptimizerService()
post_master_service = PostMasterService(train_operator_service, parcel_service, optimizer_service)

@api_view(('GET',))
def index(request):
    return Response({ 'status': 'operational' }, status=status.HTTP_200_OK)

@api_view(('POST',))
def bid_train(request):
    data = {
        'name': request.data.get('name'),
        'cost': request.data.get('cost'),
        'weight_capacity': request.data.get('weight_capacity'),
        'volume_capacity': request.data.get('volume_capacity'),
        'lines': request.data.get('lines')
    }
    serializer = TrainSerializer(data=data)
    if serializer.is_valid():
        train = train_operator_service.bid_train(data)
        serializer = TrainSerializer(train)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(('POST',))
def withdraw_train(request, train_id):
    try:
        train = train_operator_service.withdraw_train(train_id)
        serializer = TrainSerializer(train)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({ 'error': str(e)  }, status=status.HTTP_400_BAD_REQUEST)

@api_view(('POST',))
def ship_train(request, train_id, line_id):
    try:
        train = Train.objects.get(pk=train_id)
        line = Line.objects.get(pk=line_id)
        shipment = post_master_service.ship_train(train, line, request.data.get('optimized_cost_per_weight'))
        serializer = ShipmentSerializer(shipment)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({ 'error': str(e)  }, status=status.HTTP_400_BAD_REQUEST)

@api_view(('GET',))
def get_train_status(request, train_id):
    try:
        result = post_master_service.get_train_status(train_id)
        return Response(result, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({ 'error': str(e)  }, status=status.HTTP_400_BAD_REQUEST)

@api_view(('POST',))
def deposit_parcel(request):
    data = {
        'label': request.data.get('label'),
        'weight': request.data.get('weight'),
        'volume': request.data.get('volume'),
    }
    serializer = ParcelSerializer(data=data)
    if serializer.is_valid():
        parcel = parcel_service.deposit_parcel(data)
        serializer = ParcelSerializer(parcel)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(('POST',))
def withdraw_parcel(request, parcel_id):
    try:
        parcel = parcel_service.withdraw_parcel(parcel_id)
        serializer = ParcelSerializer(parcel)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({ 'error': str(e)  }, status=status.HTTP_400_BAD_REQUEST)

@api_view(('GET',))
def get_parcel_status(request, parcel_id):
    try:
        parcel = Parcel.objects.get(pk=parcel_id)
        serializer = ParcelSerializer(parcel)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({ 'error': str(e)  }, status=status.HTTP_400_BAD_REQUEST)

class LineView(APIView):

    def get(self, request):
        lines = Line.objects.all()
        serializer = LineSerializer(lines, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = {
            'name': request.data.get('name'),
            'description': request.data.get('description')
        }
        serializer = LineSerializer(data=data)
        if serializer.is_valid():
            line = post_master_service.create_line(data)
            serializer = LineSerializer(line)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TrainView(APIView):

    def get(self, request):
        trains = Train.objects.all()
        serializer = TrainSerializer(trains, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = {
            'name': request.data.get('name'),
            'cost': request.data.get('cost'),
            'weight_capacity': request.data.get('weight_capacity'),
            'volume_capacity': request.data.get('volume_capacity'),
            'lines': request.data.get('lines')
        }
        serializer = TrainSerializer(data=data)
        if serializer.is_valid():
            train = train_operator_service.bid_train(data)
            serializer = TrainSerializer(train)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ParcelView(APIView):

    def get(self, request):
        parcels = Parcel.objects.all()
        serializer = ParcelSerializer(parcels, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = {
            'label': request.data.get('label'),
            'weight': request.data.get('weight'),
            'volume': request.data.get('volume')
        }
        serializer = ParcelSerializer(data=data)
        if serializer.is_valid():
            parcel = parcel_service.deposit_parcel(data)
            serializer = ParcelSerializer(parcel)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
