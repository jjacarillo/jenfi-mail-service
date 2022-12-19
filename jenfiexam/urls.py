
from django.contrib import admin
from django.urls import path
from jenfimail.views import LineView, TrainView, ParcelView, index, bid_train, withdraw_train, get_train_status, deposit_parcel, get_parcel_status, withdraw_parcel, ship_train

urlpatterns = [
    path('admin/', admin.site.urls),
    # RESTful endpoints
    path('lines/', LineView.as_view()),
    path('trains/', TrainView.as_view()),
    path('parcels/', ParcelView.as_view()),

    # main API
    path('api/', index),
    path('api/trains/bid/', bid_train),
    path('api/parcels/deposit/', deposit_parcel),
    path('api/parcels/<int:parcel_id>/status/', get_parcel_status),
    path('api/parcels/<int:parcel_id>/withdraw/', withdraw_parcel),
    path('api/trains/<int:train_id>/withdraw/', withdraw_train),
    path('api/trains/<int:train_id>/status/', get_train_status),
    path('api/trains/<int:train_id>/ship/<int:line_id>/', ship_train),
]
