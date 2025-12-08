from django import template
from django.contrib.auth.models import Group
from apps.accounts.models import User


register = template.Library()

@register.simple_tag
def DR_name(campus):
    full_name =None
    if campus== 1:
        user = User.objects.get(groups__name='IPAM_DR')
        full_name =user.adminStaffNumberIPAM.prefix +" " + user.full_name
    elif campus== 2:
        user = User.objects.get(groups__name='COMAHS_DR')
        full_name =user.adminStaffNumberCOMAHS.prefix +" " + user.full_name
    elif campus== 3:
        user = User.objects.get(groups__name='FBC_DR')
        full_name =user.adminStaffNumberFBC.prefix +" " + user.full_name
    
    return full_name
             

