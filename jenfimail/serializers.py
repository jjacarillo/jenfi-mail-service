from rest_framework import serializers
from .models import Line, Train, Parcel

class LineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Line
        fields = ["id", "name", "description"]

class TrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = ['id', 'name', 'cost', 'weight_capacity', 'volume_capacity', 'lines', 'status']

class ParcelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parcel
        fields = ['id', 'name', 'cost', 'weight', 'volume', 'status', 'train']
