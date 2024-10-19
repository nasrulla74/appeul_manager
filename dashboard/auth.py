from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)

class CustomLoginView(LoginView):
    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(self.request, username=username, password=password)
        if user is not None:
            login(self.request, user)
            logger.info(f"User {username} authenticated successfully")
            return HttpResponseRedirect(self.get_success_url())
        else:
            logger.warning(f"Failed login attempt for user {username}")
            return self.form_invalid(form)