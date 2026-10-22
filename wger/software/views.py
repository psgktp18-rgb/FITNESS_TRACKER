# This file is part of wger Workout Manager.
#
# wger Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# wger Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License

# Standard Library
import logging

# Django
from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.shortcuts import render

# Third Party
import requests

# wger
from wger.core.forms import WgerSignupForm
from wger.exercises.models import Exercise
from wger.nutrition.models import Ingredient


logger = logging.getLogger(__name__)

CACHE_KEY = 'landing-page-context'
GITHUB_API_URL = 'https://api.github.com/repos/wger-project/wger'
GITHUB_API_TIMEOUT = 5
CACHE_TTL_SUCCESS = 60 * 60 * 24 * 7  # one week
CACHE_TTL_FAILURE = 60 * 60  # one hour


def fetch_github_stats() -> dict:
    return {
        'nr_users': User.objects.count(),
        'nr_exercises': Exercise.objects.count(),
        'nr_ingredients': Ingredient.objects.count(),
        'nr_stars': '10,000',
    }


def features(request):
    """
    Render the landing page
    """

    context = fetch_github_stats()

    form = WgerSignupForm()
    form.fields['username'].widget.attrs.pop('autofocus', None)

    context['form'] = form
    context['allow_registration'] = settings.WGER_SETTINGS['ALLOW_REGISTRATION']
    context['allow_guest_users'] = settings.WGER_SETTINGS['ALLOW_GUEST_USERS']

    return render(request, 'features.html', context)
