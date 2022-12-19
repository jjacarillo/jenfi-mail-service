from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets

from .services import TrainOperatorService, PostMasterService, ParcelService, OptimizerService
from .models import Train, Line, Parcel
from .serializers import LineSerializer, TrainSerializer

train_operator_service = TrainOperatorService()
parcel_service = ParcelService()
optimizer_service = OptimizerService()
post_master_service = PostMasterService(train_operator_service, parcel_service, optimizer_service)

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

    def book_test(self, request):
        data = {
            'name': request.data.get('name'),
            'test': request.data.get('test')
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

    def delete(self, request, train_id):
        try:
            train = train_operator_service.withdraw_train(train_id)
            return Response(
                { 'res': 'Train withdrawn' },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                { 'res': str(e) },
                status=status.HTTP_400_BAD_REQUEST
            )

class ParcelView(APIView):

    def get(self, request):
        trains = Parcel.objects.all()
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
