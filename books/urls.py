from django.urls import path

from . import views

app_name = "books"

urlpatterns = [
    path("", views.index, name="index"),
    path("add-book/", views.add_book, name="add_book"),
    path("add-tag/", views.add_tag, name="add_tag"),
    path("add-reading/", views.add_reading, name="add_reading"),
    path("reading-summary/", views.summary, name = "summary"),
    path("<int:book_id>/", views.detail, name = "detail")
]