
from django import template
from django.contrib.auth.models import Group
from django import template
from django.contrib.auth.models import Group
from django.db.models import Q
from django.db.models import Count
from django.db.models import Sum
from django.contrib.humanize.templatetags.humanize import *
import datetime
register = template.Library()
from apps.accounts.models import *



register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    try:
        group = Group.objects.get(name=group_name)
        return True if group in user.groups.all() else False
    except Group.DoesNotExist:
         return False



@register.simple_tag
def group_belong(user):
    group =None
    obj = User.objects.get(id=user)

    for g in obj.groups.all():
        group = g.name 
        
    return group


@register.simple_tag
def lecturer_group_belong(pk):
    try:
        user = User.objects.filter(lecturer=pk).first()
        if user:
            for g in user.groups.all():
                group = g.name 
                
            return group
        else: 
            return ''
    except User.DoesNotExist:
        return ''
