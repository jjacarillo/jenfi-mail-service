from django.test import TestCase
from rest_framework.test import APIRequestFactory, RequestsClient
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from ..services import TrainOperatorService, PostMasterService, ParcelService, OptimizerService
from ..models import Train, Line, Parcel
from ..views import LineView, TrainView, ParcelView

train_operator_service = TrainOperatorService()
parcel_service = ParcelService()
optimizer_service = OptimizerService()
post_master_service = PostMasterService(train_operator_service, parcel_service, optimizer_service)

factory = APIRequestFactory()
client = RequestsClient()
line_view = LineView.as_view()
train_view = TrainView.as_view()
parcel_view = ParcelView.as_view()

class APITest(TestCase):

    def setUp(self):
        self.line_a = post_master_service.create_line({ 'name': 'A' })
        self.line_b = post_master_service.create_line({ 'name': 'B' })
        self.line_c = post_master_service.create_line({ 'name': 'C' })
        self.lines = [self.line_a, self.line_b, self.line_c]

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
        self.parcel_small1 = parcel_service.deposit_parcel({ 'label': 'small-0001', 'weight': 2, 'volume': 30 })
        self.parcel_medium1 = parcel_service.deposit_parcel({ 'label': 'medium-0001', 'weight': 20, 'volume': 100 })
        self.parcel_small2 = parcel_service.deposit_parcel({ 'label': 'small-0002', 'weight': 5, 'volume': 60 })
        self.parcel_medium2 = parcel_service.deposit_parcel({ 'label': 'medium-0002', 'weight': 50, 'volume': 120 })
        self.parcel_small3 = parcel_service.deposit_parcel({ 'label': 'small0003', 'weight': 10, 'volume': 80 })

    def test_rest_get_lines(self):
        request = factory.get('lines/')
        response = line_view(request)
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(response.data)
        self.assertEqual(len(response.data), len(self.lines))
        self.assertEqual([d.get('id') for d in response.data], [l.id for l in self.lines])

    def test_rest_create_line(self):
        line_data = {
            'name': 'D',
            'description': 'Line D' # optional
        }
        request = factory.post('/lines/', line_data)
        response = line_view(request)
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(response.data.get('id'))

    def test_rest_deposit_parcel(self):
        parcel_data = {
            'label': 'small parcel 1',
            'weight': 0.5,
            'volume': 12
        }
        request = factory.post('/parcels/', parcel_data)
        response = parcel_view(request)
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(response.data.get('id'))

    def test_index(self):
        response = self.client.get('/api/')
        self.assertTrue(status.is_success(response.status_code))

    def test_bid_train(self):
        train_data = {
            'name': 'Thomas',
            'lines': [self.line_a.name],
            'weight_capacity': 400,
            'volume_capacity': 750,
            'cost': 300
        }
        response = self.client.post('/api/trains/bid/', train_data)
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(response.data.get('id'))

    def test_withdraw_train(self):
        response = self.client.post('/api/trains/{train_id}/withdraw/'.format(train_id=self.train_thomas.id))
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(response.data.get('status'), 'withdrawn')

    def test_get_train_status(self):
        response = self.client.get('/api/trains/{train_id}/status/'.format(train_id=self.train_thomas.id))
        self.assertTrue(status.is_success(response.status_code))

    def test_deposit_parcels(self):
        parcel_data = {
            'label': 'Large Parcel 1',
            'weight': 700,
            'volume': 2000
        }
        response = self.client.post('/api/parcels/deposit/', parcel_data)
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(response.data.get('id'))

    def test_get_parcel_status(self):
        response = self.client.get('/api/parcels/{parcel_id}/status/'.format(parcel_id=self.parcel_big.id))
        self.assertTrue(status.is_success(response.status_code))

    def test_withdraw_parcel(self):
        response = self.client.post('/api/parcels/{parcel_id}/withdraw/'.format(parcel_id=self.parcel_big.id))
        self.assertTrue(status.is_success(response.status_code))
        self.assertEqual(response.data.get('status'), 'withdrawn')

    def test_withdraw_train(self):
        response = self.client.post('/api/trains/{train_id}/ship/{line_id}/'.format(train_id=self.train_thomas.id, line_id=self.train_thomas.lines.first().id))
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(response.data.get('line'))
        self.assertTrue(response.data.get('train'))
        self.assertTrue(response.data.get('parcels'))
