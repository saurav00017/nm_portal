from django.urls import path
from .views import industry_registration, industries, industry
from .internship.views import internship, internships
from .jobs.views import job, jobs
from .trainings.views import training, trainings
from .mentorships.views import mentorship, mentorships
urlpatterns = [
    path("registration/", industry_registration),
    path("list/", industries),
    path("update/", industry),
    # internship
    path("internship/add/", internship),
    path("internship/list/", internships),
    # internship
    path("job/add/", job),
    path("job/list/", jobs),
    # training
    path("training/add/", training),
    path("training/list/", trainings),
    # mentorships
    path("mentorship/add/", mentorship),
    path("mentorship/list/", mentorships),
]
