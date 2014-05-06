# App specific import
from app.models import *

f = open('questions', 'rU')

for question in f.readlines():

    split = question.split('\\')
    if len(split) > 3:
        split_slice = split[1:-2]
        print split
        new_question = Question(
            text=split[0], group=split[-2].rstrip(), category=split[-1].rstrip())
        new_question.save()
        for option in split_slice:
            new_option = Option(text=option)
            new_option.save()
            new_question.options.add(new_option)
    else:
        new_question = Question(
            text=split[0], group=split[-2].rstrip(), category=split[-1].rstrip())
        new_question.save()
