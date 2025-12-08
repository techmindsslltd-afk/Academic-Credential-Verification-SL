from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.template import loader
import json
from django.http import JsonResponse
import datetime

from django.http import HttpResponse
from django import template
import sweetify
from django.db.models.deletion import ProtectedError


from .models import *
from .forms import *
import re

from apps.accounts.views import *

from django.db.models import Q, Case, When, Value, CharField
# Create your views here.


@login_required(login_url="/login/")
def index(request):
    showing_data = False
    # Get the current month and year
    fullname  =""
    regno =""
    
    if request.method == "POST":
        showing_data = True  
        regno = request.POST.get('regno') 
        if regno: 
            numeric_part = re.sub(r'\D', '', regno)
            # Use 'numeric_part' for further processing
            objects = Staff.objects.filter(staffNumber=numeric_part,campus=request.user.campus.id).order_by("-id")
        else:
            fullname = request.POST.get('fullname')
            if fullname:
                # Split the fullname into parts
                parts = fullname.split()
                # Create a query that searches across multiple fields
                query = Q()
                for part in parts:
                    query |= Q(name__icontains=part) | Q(surname__icontains=part) | Q(other_name__icontains=part)

                # Add a conditional ordering to prioritize exact matches
                if len(parts) >= 3:  # Ensure at least three parts exist
                    objects = Staff.objects.filter(query,campus=request.user.campus.id).annotate(
                        exact_match=Case(
                            When(name__iexact=parts[0], other_name__iexact=parts[1], surname__iexact=parts[2], then=Value(1)),
                            default=Value(0),
                            output_field=CharField(),
                        )
                    ).order_by('-exact_match', '-id')
                    
                elif len(parts) == 2:
                    
                    objects = Staff.objects.filter(query,campus=request.user.campus.id).annotate(
                        exact_match=Case(
                            When(name__iexact=parts[0], surname__iexact=parts[1], then=Value(1)),
                            default=Value(0),
                            output_field=CharField(),
                        )
                    ).order_by('-exact_match', '-id')
                    
                elif len(parts) == 1:
                    # Handle case for only one part (e.g., first name or last name only)
                    objects = Staff.objects.filter(query).order_by('-id')  # Modify ordering for 1 part
                
            else: 
                objects = Staff.objects.filter(campus=request.user.campus.id).order_by("-id")[:50]
    else: 
        objects = Staff.objects.filter(campus=request.user.campus.id).order_by('-id')[:50]

    context = {
        'segment': 'staffs',
        'objects': objects,
        'showing_data':showing_data,
        'fullname':fullname,
        'regno':regno
    }

    html_template = loader.get_template( 'staff/index.html' )
    return HttpResponse(html_template.render(context, request))



@login_required(login_url="/login/")
#@allowed_users(allowed_roles=['IPAM_Student','COMAHS_Student','FBC_Student'])
def create(request):
    if request.method == "POST":
        form = Staff_Form(request.POST, request.FILES)
        if form.is_valid():
            staffNumber = form.cleaned_data.get("staffNumber")
            if staffNumber:
                sNumber = re.sub(r'\D', '', staffNumber)
            else:
                sNumber = staffNumber
            if sNumber:
                if Staff.objects.filter(staffNumber=sNumber,campus=request.user.campus.id).exists():
                    sweetify.error(
                        request,
                        "Error",
                        text="This Staff number already exists.",
                        persistent="Ok",
                    )
                    context = {
                        "segment": "Add_Staff",
                        "form": form,
                    }
                    html_template = loader.get_template("staff/form.html")
                    return HttpResponse(html_template.render(context, request))
                else:
                    form.save()
            else:
                form.save()
            latest = Staff.objects.latest("timestamp")
            if staffNumber:
                # Remove non-numeric characters from staffNumber using regular expressions
                staffNumber = re.sub(r'\D', '', staffNumber)
            else:
                try:
                    last_order =  Staff.objects.filter(campus=request.user.campus.id).latest("staffNumber")
                    if last_order.staffNumber:
                        staffNumber = int(last_order.staffNumber) + 1
                    else:
                        staffNumber = 1
                except Staff.DoesNotExist:
                    # If no previous record exists, start with staffNumber as 1
                    staffNumber = 1

            latest.staffNumber = staffNumber
            latest.recordOwner = request.user
            latest.save()
            
            group = form.cleaned_data.get("group") 
            auto_add_user(request, group.name , latest.pk)
            
            sweetify.success(request, 'Good job!', text='successfully submitted', persistent='Ok')
            return redirect("staff")
    else:
        form =Staff_Form()

    context = {
        'segment': 'staffs',
        'form' : form,
    }
    html_template = loader.get_template( 'staff/form.html' )
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
#@student_bio_data_crud 
def update(request, id):   
    context = {}
    
    if request.method == "POST":
        my_record = Staff.objects.get(id=id)
        form = Staff_Form(request.POST, request.FILES, instance=my_record)
        if form.is_valid():
            staffNumber = form.cleaned_data.get("staffNumber")
            if staffNumber:
                sNumber = re.sub(r'\D', '', staffNumber)
            else:
                sNumber = staffNumber
            if Staff.objects.filter(staffNumber=sNumber,campus=request.user.campus.id).exclude(id=id).exists():
                sweetify.error(
                    request,
                    "Error",
                    text="This Staff number already exists.",
                    persistent="Ok",
                )
                context = {
                    "segment": "Add_Staff",
                    "form": form,
                }
                html_template = loader.get_template("staff/form.html")
                return HttpResponse(html_template.render(context, request))
            else:
                form.save()
            my_record.update_by = request.user
            my_record.save()
            
            group = form.cleaned_data.get("group") 
            auto_add_user(request, group.name , my_record.pk)
            
            sweetify.success(request, 'Good job!', text='Successfully updated ', persistent='Ok')
            return redirect("staff")
   
    else:
        my_record = Staff.objects.get(id=id) 
        form = Staff_Form(instance=my_record)
        context = {
        'segment': 'staffs',
        'form' : form,
        }

    html_template = loader.get_template( 'staff/form.html' )
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def show(request, id):
    object = Staff.objects.get(id=id)
 
 
    context = {
        'segment': 'staffs',
        'object': object,
    }
    html_template = loader.get_template( 'staff/show.html' )
    return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
#@staff_bio_data_crud  
def delete(request, id):   
      
    try:
        instance = Staff.objects.get(pk=id)
        instance.delete()
        return JsonResponse({'status': 'True','message': 'Deleted Successfully'})
    except ProtectedError:
        return JsonResponse({'status': 'False', 'message': "Cannot delete order it's in used aready"})

