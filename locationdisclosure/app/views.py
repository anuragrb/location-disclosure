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
    zipcode = ''
    zity = ''
    if 'MID' in request.GET:

        if User.objects.filter(username=request.GET['MID']):

            if request.user.is_authenticated():
                return redirect('/survey_page')
            else:
                user = authenticate(username=request.GET['MID'], password='')
                login(request, user)
                return redirect('/survey_page')
        else:

            if len(request.GET['MID']) > 30:
                MID = request.GET['MID'][0:30]
            else:
                MID = request.GET['MID']
            new_user = User.objects.create_user(username=MID, password='')
            new_user.save()
            user = authenticate(username=MID, password='')
            login(request, user)
            request.session['username'] = MID

            try:
                r = requests.get(
                    'http://freegeoip.net/csv/' + get_client_ip(request))
                city = r.text.split(',')[5]
                city = city[1:-1]
                zipcode = r.text.split(',')[6]
                zipcode = zipcode[1:-1]
                state = r.text.split(',')[4]
                state = state[1:-1]
                country = r.text.split(',')[2]
                country = country[1:-1]
                
            except Exception as e:
                logger.exception(
                    'There was a key error while retrieving data from freegeoip.net')
                city = ''
                request.session['city'] = ''

            condition = random.randint(1, 3)
            request.session['conint'] = condition
            new_profile = User_Profile(user=new_user, MID=MID, ip_address=get_client_ip(request), city=city, zipcode=zipcode, state=state, country=country, experimental_condition=condition)
            new_profile.save()
            condition = random.randint(1, 3)
            request.session['conint'] = condition
            return render(request, 'objects/landing.html')

    else:        
        if request.user.is_authenticated():
            return redirect('/survey_page')

        context['error'] = 'MID information is incorrect or absent.'
        return render(request, "objects/landing.html", context)


def welcome(request):

    context = {'page':'welcome'}

    if not 'answered_group' in request.session:
        request.session['answered_group'] = 0

    if not 'next_up' in request.session:
        request.session['next_up'] = 0

    if not 'conint' in request.session:
        return redirect('/')

    request.session['counter'] = 0

    conint = request.session['conint']

    user_profile = User_Profile.objects.get(user=request.user)
    questions = Question.objects.filter(group=str(request.session['answered_group']))
    questions_array = []
    if conint == 1:
        data = user_profile.zipcode
        new_data = ''
        if len(data) == 5:

            i = 0
            while i < len(data):

                if i < 2:
                    new_data = new_data + data[i]
                else:
                    new_data = new_data + '*'
                i = i + 1

        if len(data) >= 6:

            i = 0
            while i < len(data):

                if i < 3:
                    new_data = new_data + data[i]
                else:
                    new_data = new_data + '*'
                i = i + 1
        
        zipcode = new_data
        country = user_profile.country
        state = user_profile.state
        city = user_profile.city
        i = 0
        for question in questions:
            q = {}
            q['question'] = question
            if i == 0:
                question.text = '{0}: {1}'.format(question.text, city)
            elif i == 1:
                question.text = '{0}: {1}'.format(question.text, state)
            elif i == 2:
                question.text = '{0}: {1}'.format(question.text, country)
            else:
                question.text = '{0}: {1}'.format(question.text, zipcode)

            q['text'] = question.text
            q['options'] = question.options.all()
            q['category'] = question.category

            questions_array.append(q)
            i = i + 1
            if i == 4:
                break

    if conint == 2:
        i = 0
        for question in questions:
            if i < 4:
                i = i + 1
            else:
                q = {}
                q['question'] = question
                q['text'] = question.text
                q['category'] = question.category
                questions_array.append(q)
                i = i + 1

    context['questions'] = questions_array
    context['conint'] = conint
    request.session['counter'] += 1
    request.session['answered_group'] = request.session['counter']
    if conint == 3:
        request.session['counter'] += 1
        request.session['answered_group'] = request.session['counter']
        return redirect('/survey_page')

    return render(request, 'objects/welcome.html', context)


def survey_page(request):

    context = {'page': 'survey'}
    if request.session['counter'] == 2:
        increment_counter(request)
    context['current_group'] = request.session['answered_group']
    context['questions'] = []
    user_profile = User_Profile.objects.get(user=request.user)
    questions = Question.objects.filter(
        group=request.session['answered_group'])
    context['user_profile'] = user_profile
    for question in questions:
        q = {}
        q['question'] = question
        q['text'] = question.text
        q['options'] = question.options.all()
        q['category'] = question.category
        context['questions'].append(q)
    return render(request, 'objects/survey.html', context)


def submit_survey(request):
    context = {'page': 'submit_survey'}
    increment_counter(request)
    if request.is_ajax:
        try:
            keys = request.POST.iterkeys()
            for key in keys:
                if key != 'csrfmiddlewaretoken' and key != 'race':
                    question = Question.objects.get(id=key)
                    new_answer = Answer(
                        question=question, user=request.user, text=request.POST[key])
                    new_answer.save()
                    if str(key) == '34':
                        user_profile = User_Profile.objects.get(user=request.user)
                        user_profile.completed = 1
                        user_profile.save()
                elif str(key) == 'race':
                    races = ''
                    for race in request.POST.getlist('race'):

                        races = '{0}, {1}'.format(races, race)
                    
                    new_answer = Answer(
                        question=question, user=request.user, text=races)
                    new_answer.save()

        except Exception as e:
            logger.exception('Something terrible happened while saving survey data. Check stack trace')
        if 'answered_group' in request.session:
            if request.session['answered_group'] == 5:
                return redirect('/thanks')
            else:
                if request.session['counter'] == 1:
                    increment_counter(request)
                return redirect('/survey_page')
        else:
            return redirect('/survey_page')


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def thanks(request):
    return render(request, 'objects/thanks.html')


def goodbye(request):
    return render(request, 'objects/thanks.html')


def increment_counter(request):

    if request.session['counter'] == 1:
        request.session['counter'] += 1

    if request.session['counter'] == 2:

        next_up = random.randint(2, 3) #This decides if census questions will come first, or if sensitive questions will come first

        if next_up == 2:

            request.session['answered_group'] = random.randint(1, 2)
            if next_up == request.session['answered_group']:
                request.session['next_up'] = 1
                request.session['counter'] += 1
            else:
                request.session['next_up'] = 2
                request.session['counter'] += 1

        else:
            request.session['answered_group'] = 3
            request.session['counter'] += 1

    elif request.session['counter'] == 3:

        if request.session['answered_group'] == 3:

            next_up = random.randint(1, 2)
            request.session['answered_group'] = random.randint(1, 2)
            if next_up == request.session['answered_group']:
                request.session['next_up'] = 1
                request.session['counter'] += 1
            else:
                request.session['next_up'] = 2
                request.session['counter'] += 1
        else:
            request.session['answered_group'] = request.session['next_up']
            request.session['next_up'] = 3
            request.session['counter'] += 1
            # if request.session['answered_group'] == 1:
            #     request.session['answered_group'] = 2
            #     request.session['counter'] += 1
            #     request.session['next_up'] = 3
            # else:
            #     request.session['answered_group'] = 1
            #     request.session['counter'] += 1
            #     request.session['next_up'] = 3


    elif request.session['counter'] == 4:
        request.session['answered_group'] = request.session['next_up']
        request.session['counter'] += 1
        request.session['next_up'] = 4
        
    elif request.session['counter'] == 5:

        request.session['answered_group'] = request.session['next_up']
        request.session['next_up'] += 1

    else:
        pass


def finish(request):

    if 'comments' in request.POST:
        new_answer = Answer(text=request.POST['comments'], user=request.user)
        new_answer.save()

    return render(request, 'objects/finish.html')
    