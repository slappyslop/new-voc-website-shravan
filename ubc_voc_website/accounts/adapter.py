from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse
from ubc_voc_website.utils import is_member

# This exists just to redirect non-members to the join form rather than the home page when they log in
class CustomAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        user = request.user

        if user.is_staff: # So the webmaster account doesn't get redirected to the join form every time
            return super().get_login_redirect_url(request)
        
        if not is_member(user):
            return reverse("join")
        else:
            return super().get_login_redirect_url(request)