# -*- encoding: utf-8 -*-
"""
Copyright (c) 2024 - present TechMinds SL Ltd
"""

from django import forms

# from django.contrib.auth.models import User
from .models import *
from PIL import Image
from django.core.files import File


from django.contrib.auth.models import Group
from django.db.models import Q

class Staff_Form(forms.ModelForm):

    genderchoices = (("Male", "Male"), ("Female", "Female"))
    parent_status_choices = (
        ("Not Single Parent", "Not Single Parent"),
        ("Single Parent", "Single Parent"),
    )
    is_activechoices = ((True, "Active"), (False, "Inactive"))
    designationchoices = (
        ("Registrar", "Registrar"),
        ("Admin staff", "Admin staff"),
        ("Finance Office", "Finance Office"),
        ("Exam Officer", "Exam Officer"),
    )
    prefixchoices = (
        ("Mr", "Mr"),
        ("Mrs", "Mrs"),
        ("Miss", "Miss"),
        ("Dr.", "Dr."),
        ("Prof.", "Prof."),
    )
    regionchoices = (
        ("Northern Province", "Northern Province"),
        ("Western Area.", "Western Area."),
        ("North West Province", "North West Province"),
        ("Southern Province", "Southern Province"),
        ("Eastern Province.", "Eastern Province."),
    )

    x = forms.FloatField(required=False, widget=forms.HiddenInput())
    y = forms.FloatField(required=False, widget=forms.HiddenInput())
    width = forms.FloatField(required=False, widget=forms.HiddenInput())
    height = forms.FloatField(required=False, widget=forms.HiddenInput())

    
    group = forms.ModelChoiceField(
        required=True,
        queryset=Group.objects.all().exclude(Q(name="Lecturer") | Q(name="HoD") | Q(name="Dean") | Q(name="Student") | Q(name="Principal")  | Q(name="Student Warden") | Q(name="TechMindS Manager") | Q(name="TechMinds Support")),  
        widget=forms.Select(
           attrs={
                'class': 'form-control group',
                'style': 'width:100%!important',
                   }
            )
        )
    file = forms.ImageField(
        required=True,
    )

    prefix = forms.ChoiceField(
        required=True,
        choices=prefixchoices,
        widget=forms.Select(
            attrs={
                "class": "form-control prefix",
                "style": "width:100%!important",
            }
        ),
    )

    staffNumber = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                # "placeholder" : "Registration Number",
                "class": "form-control"
            }
        ),
    )
    name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                # "placeholder" : "Name",
                "class": "form-control"
            }
        ),
    )
    surname = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                # "placeholder" : "Surname",
                "class": "form-control"
            }
        ),
    )
    other_name = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                # "placeholder" : "Other Name",
                "class": "form-control"
            }
        ),
    )
    gender = forms.ChoiceField(
        required=True,
        choices=genderchoices,
        widget=forms.Select(
            attrs={
                "class": "form-control gender",
                "style": "width:100%!important",
            }
        ),
    )
    dob = forms.CharField(
        widget=forms.DateInput(
            attrs={
                "class": "form-control",
                "type": "date",
            }
        )
    )
    email = forms.EmailField(
        required=False, widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                # "placeholder" : "Other Name",
                "class": "form-control"
            }
        ),
    )
    blood_Group = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                # "placeholder" : "Other Name",
                "class": "form-control"
            }
        ),
    )
    address = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                # "placeholder" : "Other Name",
                "class": "form-control"
            }
        ),
    )

    region = forms.ChoiceField(
        choices=regionchoices,
        widget=forms.Select(
            attrs={
                "class": "form-control region",
                "style": "width:100%!important",
            }
        ),
    )
    nationality = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                # "placeholder" : "Nationality",
                "class": "form-control"
            }
        ),
    )
    qualifications = forms.CharField(
        required=True,
        widget=forms.Textarea(
            attrs={
                # "placeholder" : "Name",
                "class": "form-control",
                "id": "qualifications",
            }
        ),
    )
    is_active = forms.ChoiceField(
        required=True,
        choices=is_activechoices,
        widget=forms.Select(
            attrs={
                "class": "form-control active1",
                "style": "width:100%!important",
            }
        ),
    )

    class Meta:
        model = Staff
        fields = (
            "file",
            "x",
            "y",
            "width",
            "height",
            "address",
            "blood_Group",
            "phone",
            "email",
            "dob",
            "gender",
            "other_name",
            "surname",
            "name",
            "prefix",
            "qualifications",
            "is_active",
            "nationality",
            "region",
            "staffNumber",
            "group",
        )

    def save(self):
        formObj = super(Staff_Form, self).save()

        x = self.cleaned_data.get("x")
        y = self.cleaned_data.get("y")
        w = self.cleaned_data.get("width")
        h = self.cleaned_data.get("height")

        try:
            image = Image.open(formObj.file)
            cropped_image = image.crop((x, y, w + x, h + y))
            resized_image = cropped_image.resize((200, 200), Image.ANTIALIAS)
            resized_image.save(formObj.file.path)
            return formObj
        except:
            cropped_image = None
