from django.urls import path

from .views import student_placement
from .students.views import student_placement_list
from .reports.views import placement_overview

urlpatterns = [
    path('details/', student_placement),
    path('list/', student_placement_list),
    path('placement_overview/', placement_overview)
]
