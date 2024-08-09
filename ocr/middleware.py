from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

class AutoLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            ip_address = request.META.get('REMOTE_ADDR')
            username = ip_address
            password = ip_address

            user, created = User.objects.get_or_create(username=username)
            if created:
                user.set_password(password)
                user.save()
            
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)

        response = self.get_response(request)
        return response
