from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'), # The root now points to the dashboard
    path('room/<int:room_id>/', views.seating_plan_view, name='seating_plan'),
    path('api/save-absentees/', views.save_absentees, name='save_absentees'),
    
    path('upload/', views.upload_students, name='upload_students'),
    path('arrange/<int:room_id>/', views.auto_arrange_seating, name='auto_arrange_seating'),
    
    path('report/download/', views.download_report, name='download_report'),
    path('room/<int:room_id>/download/', views.download_seating_plan, name='download_seating_plan'),
]
