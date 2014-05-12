from django.db import models

from django.contrib.auth.models import User

class Option(models.Model):

    text = models.CharField(max_length=500)


class Question(models.Model):

    text = models.CharField(max_length=500)
    group = models.CharField(max_length=2)
    category = models.CharField(max_length=2)
    options = models.ManyToManyField(Option)
    category = models.CharField(max_length=2)


class Answer(models.Model):

    text = models.CharField(max_length=10000)
    user = models.ForeignKey(User)
    question = models.ForeignKey(Question, null=True)
    time_posted = models.DateTimeField(auto_now_add=True)

class User_Profile(models.Model):

    MID = models.CharField(max_length=30)
    user = models.OneToOneField(User)
    ip_address = models.CharField(max_length=40)
    city = models.CharField(max_length=100)
    browser = models.CharField(max_length=100)
    entrance_time = models.DateTimeField(auto_now_add=True)
    begin_time = models.DateTimeField(auto_now_add=False, null=True)
    end_time = models.DateTimeField(auto_now_add=False, null=True)
    experimental_condition = models.CharField(max_length=2)
    questions_answered = models.ManyToManyField(Question)
    answers = models.ManyToManyField(Answer)
    mturk_payment_code = models.CharField(max_length=10)
    country = models.CharField(max_length=25)
    state = models.CharField(max_length=25)
    zipcode = models.CharField(max_length=25)
    completed = models.IntegerField(default=0)
