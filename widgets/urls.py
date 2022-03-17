from django.urls import path

from . import views

urlpatterns = [
    path('', views.Widgets.as_view(), name='index'),
    path('<int:widget_id>/', views.ExistingWidget.as_view(), name='existing'),
]