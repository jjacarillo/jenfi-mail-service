from ..models import Train, Line
from ..custom_exceptions import LinesNotFoundException

class TrainOperatorService():

    def bid_train(self, data):
        line_ids = data.get('lines', [])
        lines = Line.objects.filter(name__in=line_ids).all()
        if not lines:
            raise LinesNotFoundException()

        train = Train(name=data.get('name'))
        train.cost = float(data.get('cost'))
        train.weight_capacity = float(data.get('weight_capacity'))
        train.volume_capacity = float(data.get('volume_capacity'))
        train.save()
        train.lines.set(lines)

        return train

    def withdraw_train(self, train_id):
        train = Train.objects.get(pk=train_id)
        if not train:
            raise LinesNotFoundException()

        train.withdraw()
        train.save()
        return train

    def get_available_trains(self):
        return Train.objects.filter(status=Train.STATUS_OPEN).all()

    def has_capacity(self, load):
        weight, volume = load
        return self.weight_capacity > weight and self.volume_capacity > volume
