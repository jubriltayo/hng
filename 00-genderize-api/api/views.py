from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from datetime import datetime, timezone
from .services.genderize_client import GenderizeClient


@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])
def classify_name(request):
    """GET /api/classify?name={name}"""

    # Handle CORS preflight
    if request.method == "OPTIONS":
        return JsonResponse({})

    # Extract name parameter
    name = request.GET.get("name", "").strip()

    # Validation: Missing or empty
    if not name:
        return JsonResponse(
            {"status": "error", "message": "Missing or empty name parameter"},
            status=400,
        )

    # Validation: Must be string
    if not isinstance(name, str):
        return JsonResponse(
            {"status": "error", "message": "name is not a string"}, status=422
        )

    # Call external API
    genderize_data = GenderizeClient.fetch_gender_data(name)

    # Handle upstream failure
    if genderize_data is None:
        return JsonResponse(
            {"status": "error", "message": "Upstream or server failure"}, status=502
        )

    # Edge case: No prediction available
    if genderize_data.get("gender") is None or genderize_data.get("count", 0) == 0:
        return JsonResponse(
            {
                "status": "error",
                "message": "No prediction available for the provided name",
            },
            status=404,
        )

    # Extract and transform data
    probability = genderize_data.get("probability", 0)
    sample_size = genderize_data.get("count", 0)

    # Calculate confidence
    is_confident = (probability >= 0.7) and (sample_size >= 100)

    # Generate timestamp
    processed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    # Success response
    response_data = {
        "status": "success",
        "data": {
            "name": name.lower(),
            "gender": genderize_data.get("gender"),
            "probability": probability,
            "sample_size": sample_size,
            "is_confident": is_confident,
            "processed_at": processed_at,
        },
    }

    response = JsonResponse(response_data, status=200)
    response["Access-Control-Allow-Origin"] = "*"
    return response
