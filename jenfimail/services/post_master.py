from django.db import transaction
from django.conf import settings

from datetime import datetime, timedelta, timezone

from ..models import Line, Train, Parcel, Shipment
from ..custom_exceptions import LineNotValidException, LineNotAvailableException, NoParcelsToLoadException, FailedToLoadParcelsException

class PostMasterService():
    def __init__(self, train_service, parcel_service, optimizer_service, **args):
        self.train_service = train_service
        self.parcel_service = parcel_service
        self.optimizer_service = optimizer_service

        self.profit_margin_percentage = float(args.get('profit_margin_percentage', 0))

    def create_line(self, data):
        line = Line(**data)
        line.save()
        return line

    def get_unavailable_lines(self, train):
        utc_now = datetime.now(timezone.utc)
        in_transit_shipments = Shipment.objects.filter(arrival_date__gt=utc_now).all()
        return [shipment.line for shipment in in_transit_shipments]

    def get_train_status(self, train_id):
        status = {
            'line': None,
            'departure_date': None,
            'parcels': [],
        }
        try:
            shipment = Shipment.objects.get(train__id=train_id)
        except Shipment.DoesNotExist:
            return status

        status['line'] = shipment.line.id
        status['departure_date'] = shipment.departure_date
        status['parcels'] = [parce.id for parcel in shipment.parcels]

        return status

    def ship_train(self, train, line):
        if line not in train.lines.all():
            raise LineNotValidException()
        if line in self.get_unavailable_lines(train):
            raise LineNotAvailableException()

        parcels = self.parcel_service.get_parcels_to_fill_capacity(train.capacity)
        if not parcels:
            raise NoParcelsToLoadException()

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
                raise FailedToLoadParcelsException()

            parcel.save()
            train.shipment.parcels.add(parcel)

        return True

    def _send_train(self, train, line):
        self.set_parcel_costs(train.shipment)
        train.shipment.departure_date = datetime.now(timezone.utc)
        train.shipment.arrival_date = train.shipment.departure_date  + timedelta(hours=settings.TRAIN_TRAVEL_TIME_HRS)
        train.shipment.save()
        return train.shipment

    @transaction.atomic
    def set_parcel_costs(self, shipment, **args):
        cost_per_weight = args.get('cost_per_weight', shipment.train.cost / shipment.weight)
        for parcel in shipment.parcels.all():
            parcel.cost = round(parcel.weight * cost_per_weight * (1 + self.profit_margin_percentage), 2)
            parcel.save()

    """ TO DO: may be out of scope
    def schedule_shipments(self, **args):
        lines = Line.objects.all()
        trains = self.train_operator_service.get_available_trains()
        total_capacity = (trains.aggregate(Sum('weight_capacity')), trains.aggregate(Sum('volume_capacity')))
        parcels = self.parcel_service.get_parcels_within_capacity(total_capacity)
        cost, schedule = optimizer_service.minimize_cost(lines, trains, parcels)

        earliest_departure_date = args.get('earliest_departure_date', datetime.now(timezone.utc) + timedelta(hours=settings.TRAIN_TRAVEL_TIME_HRS))
    """

