from django.test import TestCase
from rest_framework.test import APIRequestFactory, RequestsClient
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from ..services import TrainOperatorService, PostMasterService, ParcelService, OptimizerService
from ..custom_exceptions import LineNotValidException, LineNotAvailableException, LinesNotFoundException, NoParcelsToLoadException
from ..models import Train, Line, Parcel
from ..views import LineView

train_operator_service = TrainOperatorService()
parcel_service = ParcelService()
optimizer_service = OptimizerService()
post_master_service = PostMasterService(train_operator_service, parcel_service, optimizer_service)

factory = APIRequestFactory()
client = RequestsClient()
line_view = LineView.as_view()

class PostMasterEndpointTest(TestCase):

    def setUp(self):
        self.line_a = post_master_service.create_line({ 'name': 'A' })
        self.line_b = post_master_service.create_line({ 'name': 'B' })
        self.line_c = post_master_service.create_line({ 'name': 'C' })
        self.lines = [self.line_a, self.line_b, self.line_c]

    def test_get_lines(self):
        request = factory.get('lines/')
        response = line_view(request)
        self.assertTrue(status.is_success(response.status_code))
        self.assertTrue(response.data)
        self.assertEqual(len(response.data), len(self.lines))
        self.assertEqual([d.get('id') for d in response.data], [l.id for l in self.lines])

    def test_create_line(self):
        line_data = {
            'name': 'D',
            'description': 'Line D' # optional
        }
        request = factory.post('/lines/', line_data)
        response = line_view(request)
        self.assertTrue(status.is_success(response.status_code))
