import csv
import os
import uuid

from django.conf import settings
from django.core.cache import cache
from django.http import FileResponse, HttpResponse
from django.shortcuts import render
from django.urls import reverse
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

    temp_dir = os.path.join(settings.MEDIA_ROOT, "temp")
    os.makedirs(temp_dir, exist_ok=True)

    extension = uploaded_file.name.split(".")[-1].lower()
    upload_name = f"{uuid.uuid4()}.{extension}"
    temp_upload_path = os.path.join(temp_dir, upload_name)

    job_id = str(uuid.uuid4())
    output_name = f"{job_id}.csv"
    temp_output_path = os.path.join(temp_dir, output_name)

    try:
        # Save uploaded file safely
        with open(temp_upload_path, "wb+") as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)

        # Extract emails safely
        emails = extract_emails(temp_upload_path)
        unique_emails = sorted(set(emails))

        # Write result CSV
        with open(temp_output_path, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["email"])
            for email in unique_emails:
                writer.writerow([email])

        # Store only the output file path in cache
        cache.set(f"emails_file_{job_id}", temp_output_path, timeout=CACHE_TTL)

        response = {
            "success": True,
            "job_id": job_id,
            "total_emails": len(unique_emails),
            "preview_emails": unique_emails[:PREVIEW_LIMIT],
            "download_url": request.build_absolute_uri(
                reverse("download_emails", args=[job_id])
            ),
        }

    except Exception as e:
        response = {
            "success": False,
            "message": str(e)
        }

        # Clean up failed output file if created
        if os.path.exists(temp_output_path):
            try:
                os.remove(temp_output_path)
            except Exception:
                pass

    finally:
        # Remove uploaded temp file
        if os.path.exists(temp_upload_path):
            try:
                os.remove(temp_upload_path)
            except Exception:
                pass

    return Response(response)


def download_emails(request, job_id):
    file_path = cache.get(f"emails_file_{job_id}")

    if not file_path or not os.path.exists(file_path):
        return HttpResponse(
            "Download expired or unavailable.",
            status=404
        )

    return FileResponse(
        open(file_path, "rb"),
        as_attachment=True,
        filename="extracted_emails.csv"
    )
