from django.urls import path

from .views import (
    test_api,
    upload_file,
    home,
    download_emails
)

urlpatterns = [

    # HOME PAGE
    path("", home, name="home"),

    # API
    path("upload/", upload_file, name="upload_file"),
    path("download/<str:job_id>/", download_emails, name="download_emails"),

    # TEST
    path("test/", test_api, name="test_api"),
]
