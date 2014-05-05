from datetime import datetime
import re
import random
import string

# Django specific imports
from django.shortcuts import render, render_to_response, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import requests
import logging

from app.models import *

logger = logging.getLogger('custom.logger')

def landing(request):

    context = {'page': 'landing'}
    if 'MID' in request.GET:

        if User.objects.filter(username=request.GET['MID']):

            if request.user.is_authenticated():
                return redirect('/survey_page')
            else:
                user = authenticate(username=request.GET['MID'], password='')
                login(request, user)
                return redirect('/survey_page')
        else:

            new_user = User.objects.create_user(username=request.GET['MID'], password='')
            new_user.save()
            if len(request.GET['MID']) > 30:
                MID = request.GET['MID'][0:30]
            else:
                MID = request.GET['MID']
            user = authenticate(username=MID, password='')
            login(request, user)
            request.session['username'] = MID
            try:
                r = requests.get(
                    'http://freegeoip.net/csv/' + get_client_ip(request))
                city = r.text.split(',')[5]
                city = city[1:-1]
                if len(city) < 1:
                    request.session['city'] = ''
                else:
                    request.session['city'] = city
            except Exception as e:
                logger.exception(
                    'There was a key error while retrieving a city or country from freegeoip.net')
                city = ''
                request.session['city'] = ''

            new_profile = User_Profile(user=new_user, MID=MID, ip_address=get_client_ip(request), city=city)
            new_profile.save()
            condition = random.randint(1, 3)
            request.session['conint'] = condition
            return render(request, 'objects/landing.html')

    else:        
        if request.user.is_authenticated():
            return redirect('/survey_page')

        context['error'] = 'MID information is incorrect or absent.'
        return render(request, "objects/landing.html", context)


def survey_page(request):

    return render(request, 'objects/survey.html')


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip