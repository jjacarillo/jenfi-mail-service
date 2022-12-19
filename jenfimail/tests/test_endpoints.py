from django.test import TestCase
from rest_framework.test import APIRequestFactory, RequestsClient
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from ..services import TrainOperatorService, PostMasterService, ParcelService, OptimizerService
from ..custom_exceptions import LineNotValidException, LineNotAvailableException, LinesNotFoundException, NoParcelsToLoadException
from ..models import Train, Line, Parcel

train_operator_service = TrainOperatorService()
parcel_service = ParcelService()
optimizer_service = OptimizerService()
post_master_service = PostMasterService(train_operator_service, parcel_service, optimizer_service)

factory = APIRequestFactory()
client = RequestsClient()

class PostMasterEndpointTest(TestCase):

    def setUp(self):
        self.line_a = post_master_service.create_line({ 'name': 'A' })
        self.line_b = post_master_service.create_line({ 'name': 'B' })
        self.line_c = post_master_service.create_line({ 'name': 'C' })

    def test_create_line(self):
        line_data = {
            'name': 'new',
            'description': 'Line New' # optional
        }
        response = client.get('http://127.0.0.1:8000')
        self.assertEqual(response.status_code, 1)
