
from django.contrib import admin
from django.urls import path
from jenfimail.views import LineView, TrainView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('lines/', LineView.as_view()),
    path('trains/', TrainView.as_view()),
]
