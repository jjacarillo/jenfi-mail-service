from django.db import transaction
from django.conf import settings

from datetime import datetime, timedelta, timezone

from ..models import Line, Train, Parcel, Shipment
from ..custom_exceptions import LineNotValidException, LineNotAvailableException

class PostMasterService():
    def __init__(self, train_service, parcel_service, optimizer_service):
        self.train_service = train_service
        self.parcel_service = parcel_service
        self.optimizer_service = optimizer_service

    def create_line(self, data):
        line = Line(**data)
        line.save()
        return line

    def get_unavailable_lines(self, train):
        utc_now = datetime.now(timezone.utc)
        in_transit_shipments = Shipment.objects.filter(arrival_date__gt=utc_now).all()
        return [shipment.line for shipment in in_transit_shipments]

    def ship_train(self, train, line):
        if line not in train.lines.all():
            raise LineNotValidException()
        if line in self.get_unavailable_lines(train):
            raise LineNotAvailableException()

        parcels = self.parcel_service.get_parcels_to_fill_capacity(train.capacity)
        if not parcels:
            raise Exception('no parcels to load')

        self._book_train(train)
        self._fill_train(train, line, parcels)
        return  self._send_train(train, line)

    def _book_train(self, train):
        train.book()
        train.save()
        return train

    @transaction.atomic
    def _fill_train(self, train, line, parcels):
        train.shipment = Shipment(train=train, line=line)
        train.shipment.save()
        weight_load, volume_load = (0, 0)
        for parcel in parcels:
            weight_load += parcel.weight
            volume_load += parcel.volume
            parcel.shipment = train.shipment

            if weight_load > train.weight_capacity or volume_load > train.volume_capacity:
                raise Exception('failed to load parcels')

            parcel.save()
            train.shipment.parcels.add(parcel)

        return True

    def _send_train(self, train, line):
        self.optimizer_service.set_optimal_cost(train.shipment)
        train.shipment.departure_date = datetime.now(timezone.utc)
        train.shipment.arrival_date = train.shipment.departure_date  + timedelta(hours=settings.TRAIN_TRAVEL_TIME_HRS)
        train.shipment.save()
        return train.shipment

