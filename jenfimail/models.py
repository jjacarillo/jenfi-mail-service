from django.db import models
from django_fsm import FSMField, transition
from django.conf import settings

from datetime import datetime, timedelta, timezone

class Line(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=250, null=True, blank=True)

class Train(models.Model):
    name = models.CharField(max_length=50)
    cost = models.FloatField()
    weight_capacity = models.FloatField()
    volume_capacity = models.FloatField()
    lines = models.ManyToManyField(Line, through='TrainLine', related_name='trains')

    STATUS_OPEN = 'open'
    STATUS_BOOKED  = 'booked'
    STATUS_WITHDRAWN = 'withdrawn'
    STATUS = [
        (STATUS_OPEN, STATUS_OPEN),
        (STATUS_BOOKED, STATUS_BOOKED),
        (STATUS_WITHDRAWN, STATUS_WITHDRAWN),
    ]
    status = FSMField(choices=STATUS, default=STATUS_OPEN, protected=True)

    @transition(field=status, source=STATUS_OPEN, target=STATUS_WITHDRAWN)
    def withdraw(self):
        return self

    @transition(field=status, source=STATUS_OPEN, target=STATUS_BOOKED)
    def book(self):
        return self

    @property
    def capacity(self):
        return (self.weight_capacity, self.volume_capacity)

    @property
    def density(self):
        return self.weight_capacity / self.volume_capacity

class TrainLine(models.Model):
    train = models.ForeignKey(Train, on_delete=models.CASCADE)
    line = models.ForeignKey(Line, on_delete=models.CASCADE)

class Parcel(models.Model):
    label = models.CharField(max_length=100)
    weight = models.FloatField()
    volume = models.FloatField()
    cost = models.FloatField(null=True)
    description = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    withdrawn_at = models.DateTimeField(null=True)
    shipment = models.ForeignKey('Shipment', on_delete=models.RESTRICT, blank=True, null=True)

    STATUS_PENDING = 'pending'
    STATUS_IN_TRANSIT = 'in transit'
    STATUS_SHIPPED = 'shipped'
    STATUS_WITHDRAWN = 'withdrawn'

    """ Removed to favor solution not needing cron jobs / scheduler
    STATUS = [
        (STATUS_PENDING, STATUS_PENDING),
        (STATUS_IN_TRANSIT, STATUS_IN_TRANSIT),
        (STATUS_SHIPPED, STATUS_SHIPPED),
        (STATUS_WITHDRAWN, STATUS_WITHDRAWN),
    ]
    status = FSMField(choices=STATUS, default=STATUS_PENDING, protected=True)

    @transition(field=status, source=STATUS_PENDING, target=STATUS_IN_TRANSIT)
    def transport(self):
        return self

    @transition(field=status, source=STATUS_IN_TRANSIT, target=STATUS_SHIPPED)
    def ship(self):
        return self

    @transition(field=status, source=STATUS_SHIPPED, target=STATUS_WITHDRAWN)
    def withdraw(self):
        return self
    """

    @property
    def status(self):
        if self.withdrawn_at:
            return self.STATUS_WITHDRAWN

        if not self.shipment:
            return self.STATUS_PENDING

        return self.STATUS_SHIPPED if self.shipment.has_arrived else self.STATUS_IN_TRANSIT

    @property
    def load(self):
        return (self.weight, self.volume)

    @property
    def density(self):
        return self.weight / self.volume

    def __str__(self):
        return '{id}-{label}: {load} {status} {shipment_id} {cost}'.format(id=self.id, label=self.label, load=self.load, status=self.status, shipment_id=self.shipment.id if self.shipment else 'NA', cost=self.cost)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['weight', 'volume', 'withdrawn_at'])
        ]

class Shipment(models.Model):
    train = models.OneToOneField(Train, on_delete=models.RESTRICT)
    parcels = models.ManyToManyField(Parcel, through='ShipmentParcel', related_name='shipments')
    departure_date = models.DateTimeField(null=True)
    arrival_date = models.DateTimeField(null=True)
    line = models.ForeignKey(Line, on_delete=models.RESTRICT)
    optimized_cost_per_weight = models.FloatField(null=True)

    STATUS_IN_TRANSIT = 'in transit'
    STATUS_ARRIVED  = 'arrived'
    @property
    def has_arrived(self):
        return self.arrival_date and datetime.now(timezone.utc) > self.arrival_date

    @property
    def status(self):
        return self.STATUS_ARRIVED if self.has_arrived else self.STATUS_IN_TRANSIT

    @property
    def weight(self):
        return self.parcels.all().aggregate(weight=models.Sum('weight'))['weight']

    @property
    def volume(self):
        return self.parcels.all().aggregate(volume=models.Sum('volume'))['volume']

    @property
    def density(self):
        return self.weight / self.volume

    @property
    def revenue(self):
        return self.parcels.all().aggregate(revenue=models.Sum('cost'))['revenue']

class ShipmentParcel(models.Model):
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE)
    porcel = models.ForeignKey(Parcel, on_delete=models.CASCADE)
