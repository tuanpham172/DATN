from django.urls import path
from . import views
from . import views2
from django.conf.urls import url

app_name = "home"
urlpatterns = [
    path('', views.choose_algorithm, name = "HOME"),
    path('recommendItemByUser/', views2.recommendItemByUser, name = "recommendItemByUser"),
    path('recommendItemByItem/', views2.recommendItemByItem, name = "recommendItemByItem"),
    path('/recommend/<int:user_id>/', views.recommend, name = "recommend"),
    path('search/', views.search, name="search"),
    path('ContentBased/', views.ContentBased, name='ContentBased'),
    path('NeighborhoodBased/', views2.NeighborhoodBased, name='NeighborhoodBased'),
]