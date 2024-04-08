from django.urls import path

from stadium_management import views

app_name = "stadium_management"

urlpatterns = [
    path("stadium/", views.StadiumAddView.as_view(), name="add-stadium"),
]
