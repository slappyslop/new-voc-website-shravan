from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET

from membership.models import Membership

User = get_user_model()

@csrf_exempt
@require_GET
def membership_verification(request):
    """
    API endpoint for use by the Discord verfication bot
    Returns the email address and membership end_date associated with the given user_id
    """
    api_key = request.headers.get("AUTH")
    if api_key != settings.API_KEY:
        return JsonResponse({"error": "Invalid API key"}, status=401)
    
    user_id = request.GET.get("id")
    if not user_id or not user_id.isdigit():
        return JsonResponse({"error": "Invalid or missing user ID"}, status=400)
    user_id = int(user_id)

    membership = Membership.objects.filter(membership__user__id=user_id, active=True).select_related("user").order_by("-enddate").first()

    if not membership or membership.end_date < timezone.now().date():
        return JsonResponse({"error": "User is not a current VOC member"}, status=400)
    
    return JsonResponse({
        "email": membership.user.email,
        "enddate": membership.end_date.isoformat()
    })
    

