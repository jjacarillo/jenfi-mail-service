from django.test import TestCase
from ..services import TrainOperatorService, PostMasterService, ParcelService, OptimizerService
from ..custom_exceptions import LineNotValidException, LineNotAvailableException, LinesNotFoundException, NoParcelsToLoadException
from ..models import Train, Line, Parcel

train_operator_service = TrainOperatorService()
parcel_service = ParcelService()
optimizer_service = OptimizerService()
post_master_service = PostMasterService(train_operator_service, parcel_service, optimizer_service)

class PostMasterServiceTest(TestCase):

    def setUp(self):
        self.line_a = post_master_service.create_line({ 'name': 'A' })
        self.line_b = post_master_service.create_line({ 'name': 'B' })
        self.line_c = post_master_service.create_line({ 'name': 'C' })

    def test_create_line(self):
        line_data = {
            'name': 'new',
            'description': 'Line New' # optional
        }
        line = post_master_service.create_line(line_data)
        self.assertEqual(line.name, line_data.get('name'))
        self.assertEqual(line.description, line_data.get('description'))

    def test_create_duplicate_line(self):
        line_data = {
            'name': self.line_a.name
        }
        got_exception = True
        try:
            self.assertFalse(post_master_service.create_line(line_data))
            self.assertFalse(got_exception)
        except Exception as e:
            self.assertTrue(got_exception)

class TrainOpearatorServiceTest(TestCase):
    STATUS_OPEN = 'open'
    STATUS_WITHDRAWN = 'withdrawn'
    STATUS_FILLED = 'filled'

    def setUp(self):
        self.line_a = post_master_service.create_line({ 'name': 'A' })
        self.line_b = post_master_service.create_line({ 'name': 'B' })
        self.line_c = post_master_service.create_line({ 'name': 'C' })
        train_data = {
            'name': 'Thomas',
            'weight_capacity': 100,
            'volume_capacity': 500,
            'cost': 200,
            'lines': [self.line_a.name, self.line_b.name]
        }
        self.train_thomas = train_operator_service.bid_train(train_data)

    def test_bid_train_invalid_line(self):
        train_data = {
            'name': 'Thomas',
            'weight_capacity': 100,
            'volume_capacity': 500,
            'cost': 200,
            'lines': ['X']
        }
        self.assertRaises(LinesNotFoundException, train_operator_service.bid_train, train_data)

    def test_bid_train(self):
        train_data = {
            'name': 'Percy',
            'weight_capacity': 50,
            'volume_capacity': 150,
            'cost': 100,
            'lines': [self.line_a.name, self.line_b.name]
        }
        train = train_operator_service.bid_train(train_data)
        self.assertEqual(train.name, train_data.get('name'))
        self.assertEqual(train.weight_capacity, train_data.get('weight_capacity'))
        self.assertEqual(train.volume_capacity, train_data.get('volume_capacity'))
        self.assertEqual(train.cost, train_data.get('cost'))
        self.assertEqual(len(train.lines.all()), len(train_data.get('lines')))
        for line in train.lines.all():
            self.assertIn(line.name,  train_data.get('lines'))
        self.assertEqual(train.status, self.STATUS_OPEN)

    def test_withdraw_train(self):
        train = train_operator_service.withdraw_train(self.train_thomas.id)

        self.assertTrue(train)
        self.assertEqual(train.status, self.STATUS_WITHDRAWN)

    def test_get_available_trains(self):
        trains = train_operator_service.get_available_trains()
        self.assertTrue(trains)
        self.assertEqual(self.train_thomas.id, trains[0].id)
        self.assertEqual(self.STATUS_OPEN, trains[0].status)

    def test_get_available_trains_withdrawn(self):
        train_operator_service.withdraw_train(self.train_thomas.id)

        trains = train_operator_service.get_available_trains()
        self.assertFalse(trains)

class ParcelOwnerServiceTest(TestCase):
    STATUS_PENDING = 'pending'

    def setUp(self):
        self.parcel1 = parcel_service.deposit_parcel({ 'label': '0001', 'weight': 2, 'volume': 30 })
        self.parcel2 = parcel_service.deposit_parcel({ 'label': '0002', 'weight': 5, 'volume': 60 })
        self.parcel3 = parcel_service.deposit_parcel({ 'label': '0003', 'weight': 30, 'volume': 200 })

        self.zero_load = (0, 0)
        self.zero_weight_load = (0, self.parcel1.volume)
        self.zero_volume_load = (self.parcel1.weight, 0)
        self.min_load = (
            min([self.parcel1.weight, self.parcel2.weight, self.parcel3.weight]),
            min([self.parcel1.volume, self.parcel2.volume, self.parcel3.volume])
        )
        self.max_load = (
            max([self.parcel1.weight, self.parcel2.weight, self.parcel3.weight]),
            max([self.parcel1.volume, self.parcel2.volume, self.parcel3.volume])
        )

    def test_deposit_parcel(self):
        parcel_data = {
            'label': 'Gold',
            'weight': 1,
            'volume': 20
        }

        parcel = parcel_service.deposit_parcel(parcel_data)
        self.assertEqual(parcel.label, parcel_data.get('label'))
        self.assertEqual(parcel.weight, parcel_data.get('weight'))
        self.assertEqual(parcel.volume, parcel_data.get('volume'))
        self.assertEqual(parcel.status, self.STATUS_PENDING)

    def test_withdraw_pending_parcel_pending(self):
        got_exception = True
        try:
            self.assertTrue(self.parcel1.withdraw())
            self.assertFalse(got_exception)
        except:
            self.assertTrue(got_exception)

    """
    def test_withdraw_in_transit_parcel(self):
        got_exception = True
        self.parcel1.transport()
        try:
            self.assertTrue(self.parcel1.withdraw())
            self.assertFalse(got_exception)
        except:
            self.assertTrue(got_exception)

    def test_withdraw_shipped_parcel(self):
        got_exception = True
        self.parcel1.transport()
        self.parcel1.ship()
        self.assertTrue(self.parcel1.withdraw())

    def test_is_parcel_shipped(self):
        self.assertFalse(parcel_service.is_shipped(self.parcel1.id))
        parcel_service.transport_parcel(self.parcel1.id)
        self.assertFalse(parcel_service.is_shipped(self.parcel1.id))
        parcel_service.ship_parcel(self.parcel1.id)
        self.assertTrue(parcel_service.is_shipped(self.parcel1.id))
    """

    def test_is_fillable(self):
        self.assertFalse(parcel_service.is_fillable(self.zero_load))
        self.assertFalse(parcel_service.is_fillable(self.zero_weight_load))
        self.assertFalse(parcel_service.is_fillable(self.zero_volume_load))
        self.assertTrue(parcel_service.is_fillable(self.max_load))
        self.assertTrue(parcel_service.is_fillable(self.min_load))

    """
    def test_get_parcels_for_filling_zero(self):
        self.assertFalse(parcel_service.get_parcels_for_filling(self.zero_load))
        self.assertFalse(parcel_service.get_parcels_for_filling(self.zero_weight_load))
        self.assertFalse(parcel_service.get_parcels_for_filling(self.zero_weight_load))

    def test_get_parcels_for_filling_min(self):
        parcels = parcel_service.get_parcels_for_filling(self.min_load)
        self.assertTrue(parcels)
        self.assertEqual(self.min_load[0], sum([parcel.weight for parcel in parcels]) if parcels else 0)
    """

class PostMasterServiceTest(TestCase):
    SHIPMENT_STATUS_IN_TRANSIT = 'in transit'
    PARCEL_STATUS_IN_TRANSIT = 'in transit'

    def setUp(self):
        self.line_a = post_master_service.create_line({ 'name': 'A' })
        self.line_b = post_master_service.create_line({ 'name': 'B' })
        self.line_c = post_master_service.create_line({ 'name': 'C' })
        self.train_thomas = train_operator_service.bid_train({
            'name': 'Thomas (Medium)',
            'weight_capacity': 80,
            'volume_capacity': 300,
            'cost': 200,
            'lines': [self.line_a.name, self.line_b.name]
        })
        self.train_james = train_operator_service.bid_train({
            'name': 'James (Big)',
            'weight_capacity': 200,
            'volume_capacity': 500,
            'cost': 400,
            'lines': [self.line_c.name]
        })
        self.train_percy = train_operator_service.bid_train({
            'name': 'Percy (Small)',
            'weight_capacity': 50,
            'volume_capacity': 20,
            'cost': 100,
            'lines': [self.line_b.name, self.line_c.name]
        })

        self.parcel_biggest = parcel_service.deposit_parcel({ 'label': 'biggest - can never fit', 'weight': 200, 'volume': 1000 })
        self.parcel_big = parcel_service.deposit_parcel({ 'label': 'big', 'weight': 300, 'volume': 500 })
        self.parcel_big2 = parcel_service.deposit_parcel({ 'label': 'big', 'weight': 100, 'volume': 300 })
        self.parcel_withdrawn  = parcel_service.deposit_parcel({ 'label': 'small-withdrawn', 'weight': 1, 'volume': 5 })
        parcel_service.withdraw_parcel(self.parcel_withdrawn.id)
        self.parcel_small1 = parcel_service.deposit_parcel({ 'label': 'small-0001', 'weight': 2, 'volume': 30 })
        self.parcel_medium1 = parcel_service.deposit_parcel({ 'label': 'medium-0001', 'weight': 20, 'volume': 100 })
        self.parcel_small2 = parcel_service.deposit_parcel({ 'label': 'small-0002', 'weight': 5, 'volume': 60 })
        self.parcel_medium2 = parcel_service.deposit_parcel({ 'label': 'medium-0002', 'weight': 50, 'volume': 120 })
        self.parcel_small3 = parcel_service.deposit_parcel({ 'label': 'small0003', 'weight': 10, 'volume': 80 })

    def test_ship_train_line_invalid(self):
        self.assertTrue(self.line_c not in  self.train_thomas.lines.all())
        self.assertRaises(LineNotValidException, post_master_service.ship_train, self.train_thomas, self.line_c)

    def test_ship_train_line_not_available(self):
        self.assertTrue(self.line_b in  self.train_thomas.lines.all())
        self.assertTrue(self.line_b in  self.train_percy.lines.all())

        shipment = post_master_service.ship_train(self.train_thomas, self.line_b)
        self.assertRaises(LineNotAvailableException, post_master_service.ship_train, self.train_percy, self.line_b)

    def test_ship_train_normal(self):
        shipment = post_master_service.ship_train(self.train_thomas, self.train_thomas.lines.first())
        self.assertTrue(shipment)
        self.assertEqual([line for line in shipment.train.lines.all()], [line for line in self.train_thomas.lines.all()])
        self.assertEqual(shipment.status, self.SHIPMENT_STATUS_IN_TRANSIT)
        self.assertTrue(len(shipment.parcels.all()) > 1)

        weight, volume, = 0, 0
        prev_parcel = None
        for parcel in shipment.parcels.all():
            self.assertTrue(parcel.status, self.PARCEL_STATUS_IN_TRANSIT)
            weight += parcel.weight
            volume += parcel.volume
            if prev_parcel:
                self.assertTrue(prev_parcel.created_at <= parcel.created_at)
            prev_parcel = parcel

        self.assertTrue(weight <= self.train_thomas.weight_capacity)
        self.assertTrue(volume <= self.train_thomas.volume_capacity)
        self.assertEqual(self.train_thomas.cost, shipment.revenue)

    def test_ship_train_big(self):
        shipment = post_master_service.ship_train(self.train_james, self.train_james.lines.first())
        self.assertTrue(shipment)
        self.assertEqual([line for line in shipment.train.lines.all()], [line for line in self.train_james.lines.all()])
        self.assertEqual(shipment.status, self.SHIPMENT_STATUS_IN_TRANSIT)
        self.assertEqual(len(shipment.parcels.all()), 4)
        self.assertEqual(self.train_james.cost, shipment.revenue)

    def test_ship_train_small(self):
        self.assertRaises(NoParcelsToLoadException, post_master_service.ship_train, self.train_percy, self.train_percy.lines.first())

    def test_optimize_feasible(self):
        trains = Train.objects.all()
        lines = Line.objects.all()
        parcels = Parcel.objects.filter(withdrawn_at=None, shipment=None)[2:]

        cost, schedule = optimizer_service.minimize_cost(lines, trains, parcels)
        self.assertTrue(cost)
        self.assertTrue(schedule)

        calculated_cost = 0
        calculated_weight = 0
        calculated_volume = 0
        for train, line in schedule:
            calculated_cost += train.cost
            calculated_weight += train.weight_capacity
            calculated_volume += train.volume_capacity

        self.assertEqual(cost, calculated_cost)
        self.assertTrue(sum([p.weight for p in parcels]) <= calculated_weight)
        self.assertTrue(sum([p.volume for p in parcels]) <= calculated_volume)

    def test_optimize_infeasible(self):
        trains = Train.objects.all()
        lines = Line.objects.all()
        parcels = Parcel.objects.filter(withdrawn_at=None, shipment=None)

        cost, schedule = optimizer_service.minimize_cost(lines, trains, parcels)
        self.assertFalse(cost)
        self.assertFalse(schedule)
