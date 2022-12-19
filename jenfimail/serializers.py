from rest_framework import serializers
from .models import Line, Train, Parcel, Shipment

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
        fields = ['id', 'label', 'weight', 'volume', 'status', 'cost']

class ShipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipment
        fields = ['id',  'train', 'line', 'parcels', 'weight', 'volume', 'status']
