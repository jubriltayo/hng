from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

from .models import Profile
from .services.genderize_client import GenderizeClient
from .services.agify_client import AgifyClient
from .services.nationalize_client import NationalizeClient


# Helper function
def format_profile_response(profile):
    """Format profile data consistently across all endpoints"""
    return {
        "id": str(profile.id),
        "name": profile.name,
        "gender": profile.gender,
        "gender_probability": profile.gender_probability,
        "sample_size": profile.sample_size,
        "age": profile.age,
        "age_group": profile.age_group,
        "country_id": profile.country_id,
        "country_probability": round(profile.country_probability, 2),
        "created_at": profile.created_at.replace(microsecond=0).isoformat().replace("+00:00", "Z")
    }


@csrf_exempt
@require_http_methods(["GET", "POST", "OPTIONS"])
def profile_list(request):
    """
    GET /api/profiles - List all profiles (with optionalfilters)
    POST /api/profiles - Create a new profile
    """
    
    if request.method == "OPTIONS":
        return JsonResponse({}, status=200)
    
    # ========== GET ALL PROFILES ==========
    if request.method == "GET":
        queryset = Profile.objects.all()
        
        # Case-insensitive filtering
        gender = request.GET.get("gender")
        if gender:
            queryset = queryset.filter(gender__iexact=gender)
        
        country_id = request.GET.get("country_id")
        if country_id:
            queryset = queryset.filter(country_id__iexact=country_id)
        
        age_group = request.GET.get("age_group")
        if age_group:
            queryset = queryset.filter(age_group__iexact=age_group)
        
        data = [
            {
                "id": str(p.id),
                "name": p.name,
                "gender": p.gender,
                "age": p.age,
                "age_group": p.age_group,
                "country_id": p.country_id,
            }
            for p in queryset
        ]
        
        return JsonResponse({
            "status": "success",
            "count": len(data),
            "data": data
        }, status=200)
    
    # ========== CREATE PROFILE ==========
    if request.method == "POST":
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                "status": "error",
                "message": "Invalid JSON"
            }, status=400)
        
        name = body.get("name")
        
        # Validation
        if name is None:
            return JsonResponse({
                "status": "error",
                "message": "Missing or empty name"
            }, status=400)

        if not isinstance(name, str):
            return JsonResponse({
                "status": "error",
                "message": "Invalid type"
            }, status=422)
        
        name = name.strip()

        if not name:
            return JsonResponse({
                "status": "error",
                "message": "Missing or empty name"
            }, status=400)
        
        # Check if profile already exists
        existing_profile = Profile.objects.filter(name__iexact=name).first()
        if existing_profile:
            return JsonResponse({
                "status": "success",
                "message": "Profile already exists",
                "data": format_profile_response(existing_profile)
            }, status=200)
        
        # Fetch data from external APIs
        gender_data = GenderizeClient.fetch_gender_data(name)
        if not gender_data:
            return JsonResponse({
                "status": "error",
                "message": "Genderize returned an invalid response"
            }, status=502)
        
        age_data = AgifyClient.fetch_age_data(name)
        if age_data is None:
            return JsonResponse({
                "status": "error",
                "message": "Agify returned an invalid response"
            }, status=502)
        
        nationality_data = NationalizeClient.fetch_nationality_data(name)
        if nationality_data is None:
            return JsonResponse({
                "status": "error",
                "message": "Nationalize returned an invalid response"
            }, status=502)
        
        # Create new profile
        profile = Profile.objects.create(
            name=name.lower(),
            gender=gender_data["gender"],
            gender_probability=gender_data["probability"],
            sample_size=gender_data["sample_size"],
            age=age_data["age"],
            age_group=age_data["age_group"],
            country_id=nationality_data["country_id"],
            country_probability=nationality_data["country_probability"]
        )
        
        return JsonResponse({
            "status": "success",
            "data": format_profile_response(profile)
        }, status=201)


@csrf_exempt
@require_http_methods(["GET", "DELETE", "OPTIONS"])
def profile_detail(request, profile_id):
    """
    GET /api/profiles/{id} - Retrieve a specific profile
    DELETE /api/profiles/{id} - Delete a specific profile
    """
    
    if request.method == "OPTIONS":
        return JsonResponse({}, status=200)
    
    try:
        profile = Profile.objects.get(id=profile_id)
    except (ValidationError, Profile.DoesNotExist):
        return JsonResponse({
            "status": "error",
            "message": "Profile not found"
        }, status=404)

    if request.method == "GET":
        return JsonResponse({
            "status": "success",
            "data": format_profile_response(profile)
        }, status=200)
    
    if request.method == "DELETE":
        profile.delete()
        return JsonResponse({}, status=204)