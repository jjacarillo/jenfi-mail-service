from ..models import Parcel

class ParcelService():

    def deposit_parcel(self, data):
        parcel = Parcel(**data)
        parcel.save()
        return parcel

    def transport_parcel(self, parcel_id):
        parcel = Parcel.objects.get(pk=parcel_id)

        parcel.transport()
        parcel.save()
        return parcel

    def ship_parcel(self, parcel_id):
        parcel = Parcel.objects.get(pk=parcel_id)

        parcel.ship()
        parcel.save()
        return parcel

    def is_shipped(self, parcel_id):
        parcel = Parcel.objects.get(pk=parcel_id)
        if not parcel:
            raise Exception('invalid parcel id')

        return parcel.status == Parcel.STATUS_SHIPPED

    def get_parcels_within_capacity(self, capacity):
        weight_capacity, volume_capacity = capacity
        return Parcel.objects.filter(volume__lte=volume_capacity, weight__lte=weight_capacity, shipment=None)

    def is_fillable(self, capacity):
        weight_capacity, volume_capacity = capacity
        if not weight_capacity or not volume_capacity:
            return False

        try:
            return bool(self.get_parcels_within_capacity(capacity).first())
        except Parcel.DoesNotExist:
            return False

    def get_parcels_to_fill_capacity(self, capacity):
        result = []
        weight_capacity, volume_capacity = capacity
        if not weight_capacity or not volume_capacity:
            return result

        remaining_capacity = capacity
        while self.is_fillable(remaining_capacity):
            try:
                parcels = self.get_parcels_within_capacity(remaining_capacity)
                for parcel in parcels:
                    if parcel.weight > remaining_capacity[0] or parcel.volume > remaining_capacity[1]:
                        break

                    remaining_capacity = (
                        remaining_capacity[0] - parcel.weight,
                        remaining_capacity[1] - parcel.volume
                    )
                    result.append(parcel)

            except Parcel.DoesNotExist:
                break

        return result
