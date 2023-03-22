from django.urls import path
from . import views
app_name = 'home'
urlpatterns = [
    path('', views.HomePageView.as_view(), name='index'),
    #--swimmer paths
    path('swimmers/', views.SwimmerListView.as_view(), name='swimmers'),
    path('swimmer/create/',views.SwimmerFormView.as_view(),name='add swimmer'),
    path('swimmer/detail/<int:pk>/',views.SwimmerDetailView.as_view(), name = 'detail'),
    path('swimmer/update/<int:pk>/',views.SwimmerUpdateView.as_view(), name = 'update'),

    #-- competition paths
    path('competition/', views.CompetitonMenu.as_view(), name='comp_menu'),
    path('competition/list', views.CompetitionList.as_view(), name='comp_list'),
    path('competition/add',views.CompetitionCreateView.as_view(),name='comp_create'),
    path('competition/detail/<int:pk>/',views.CompRaceView.as_view(),name='comp_detail'),
    path('competition/update/<int:pk>/',views.CompetitionUpdateView.as_view(), name = 'comp_update'),

    #-- race paths
    path('competition/race/detail/<int:pk>/',views.RaceView.as_view(),name='race_detail'),
    path('competition/race/update/<int:pk>/',views.RaceUpdateView.as_view(), name = 'race_update'),

    #-- delete paths
    path('delete-comp/<int:pk>/', views.delete_competition, name='delete_competition'),
    path('delete-swimmer/<int:pk>/', views.delete_swimmer, name='delete_swimmer'),
    path('delete-race/<int:pk>/', views.delete_race, name='delete_race'),
]