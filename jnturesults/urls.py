from . import views
from django.urls import path
urlpatterns=[
    path('',views.home,name='home'),
    path('results/', views.results, name='results'),
    path('results/<path:exam_link>/', views.results, name='results'),
    ]