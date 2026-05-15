import csv
import os
import uuid

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .utils.extractor import extract_emails
from .utils.validators import validate_uploaded_file


PREVIEW_LIMIT = 20
CACHE_TTL = 60 * 30  # 30 minutes


def home(request):
    return render(request, "index.html")


@api_view(["GET"])
def test_api(request):
    return Response({
        "success": True,
        "message": "Backend working"
    })


@api_view(["POST"])
def upload_file(request):
    uploaded_file = request.FILES.get("file")

    if not uploaded_file:
        return Response({
            "success": False,
            "message": "No file uploaded"
        }, status=400)

    is_valid, error = validate_uploaded_file(uploaded_file)
    if not is_valid:
        return Response({
            "success": False,
            "message": error
        }, status=400)

    extension = uploaded_file.name.split(".")[-1]
    filename = f"{uuid.uuid4()}.{extension}"

    temp_path = os.path.join(
        settings.MEDIA_ROOT,
        "temp",
        filename
    )

    with open(temp_path, "wb+") as f:
        for chunk in uploaded_file.chunks():
            f.write(chunk)

    try:
        emails = extract_emails(temp_path)
        job_id = str(uuid.uuid4())

        cache.set(
            f"emails_{job_id}",
            emails,
            timeout=CACHE_TTL
        )

        response = {
            "success": True,
            "job_id": job_id,
            "total_emails": len(emails),
            "preview_emails": emails[:PREVIEW_LIMIT]
        }

    except Exception as e:
        response = {
            "success": False,
            "message": str(e)
        }

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    return Response(response)


def download_emails(request, job_id):
    emails = cache.get(f"emails_{job_id}")

    if not emails:
        return HttpResponse(
            "Download expired or unavailable.",
            status=404
        )

    response = HttpResponse(
        content_type="text/csv"
    )
    response["Content-Disposition"] = 'attachment; filename="emails.csv"'

    writer = csv.writer(response)
    writer.writerow(["email"])

    for email in emails:
        writer.writerow([email])

    return response