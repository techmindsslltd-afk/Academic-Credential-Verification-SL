from django import forms

from .models import *
from django.utils.text import slugify

# Constants for form choices
STATUS_CHOICES = (
    (False, 'Pending'),
    (True, 'Publish')
)

NEWS_CATEGORY_CHOICES = (
    ('General News', 'General News'),
    ('Governance', 'Governance'),
    ('Memo', 'Memo'),
    ('Community', 'Community'),
    ('Research & Innovation', 'Research & Innovation'),
    ('Announcements', 'Announcements'),
    ('Sierra Leone Development', 'Sierra Leone Development'),
    ('Partnerships', 'Partnerships'),
    ('Events & Conferences', 'Events & Conferences')
)

EVENT_CATEGORY_CHOICES = (
    ('General Events', 'General Events'),
    (' Governance', ' Governance'),
    ('Academic Conferences', 'Academic Conferences'),
    ('Community Events', 'Community Events'),
    ('Partnership Events', 'Partnership Events'),
    ('Sierra Leone Development', 'Sierra Leone Development')
)

       
class GeneralSettingsForm(forms.ModelForm):
    
    grade_view=((True, 'Pay fee before viewing grades.'),(False,'Can view grades without Fee payment'))  
    
    site_name = forms.CharField(
        required=False, 
        widget=forms.TextInput(
            attrs={             
                "class"       : "form-control"
            }
        ))
    site_name_abb = forms.CharField(
        required=False, 
        widget=forms.TextInput(
            attrs={             
                "class"       : "form-control"
            }
        ))
    file = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={"class": "form-control"})
    )
    file_2 = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={"class": "form-control"})
    )
    slogan = forms.CharField( 
        required=False, 
        widget=forms.TextInput(
            attrs={             
                "class"       : "form-control"
            }
        ))
    primary_color = forms.CharField(
        required=False, 
        widget=forms.TextInput(
            attrs={             
                "class"       : "form-control"
            }
        ))
    secondary_color = forms.CharField(
        required=False, 
        widget=forms.TextInput(
            attrs={             
                "class"       : "form-control"
            }
        ))
    email = forms.CharField(
        required=False, 
        widget=forms.TextInput(
            attrs={             
                "class"       : "form-control",
                "type": "email",
            }
        ))
    email2 = forms.CharField(
        required=False, 
        widget=forms.TextInput(
            attrs={             
                "class"       : "form-control",
                "type": "email",
            }
        ))
    site_desc = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
               # "placeholder" : "Name",              
                "class"       : "form-control",
                'id': 'qualifications',
            }
        ))
    site_keyword = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
               # "placeholder" : "Name",              
                "class"       : "form-control",
                'id': 'qualifications',
            }
        ))
    google_code = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={                
                "class": "form-control"
            }
        ))
    street = forms.CharField(
        required=False, 
        widget=forms.TextInput(
            attrs={               
                "class": "form-control"
            }
        ))
    city = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder" : "",                
                "class": "form-control"
            }
        ))
    country = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder" : "",                
                "class": "form-control"
            }
        ))
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder" : "",                
                "class": "form-control"
            }
        ))
    city = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder" : "",                
                "class": "form-control"
            }
        ))
    street2 = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder" : "",                
                "class": "form-control"
            }
        ))
    city2 = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder" : "",                
                "class": "form-control"
            }
        ))
    country2 = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder" : "",                
                "class": "form-control"
            }
        ))
    phone2 = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder" : "",                
                "class": "form-control"
            }
        ))
    facebook = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder" : "",                
                "class": "form-control"
            }
        ))
    twitter = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder" : "",                
                "class": "form-control"
            }
        ))
    linkedin = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder" : "",                
                "class": "form-control"
            }
        ))
    instagram = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder" : "",                
                "class": "form-control"
            }
        ))
    google = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder" : "",                
                "class": "form-control"
            }
        ))
    reddit = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder" : "",                
                "class": "form-control"
            }
        ))
    tumblr = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder" : "",                
                "class": "form-control"
            }
        ))
    status = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder" : "",                
                "class": "form-control"
            }
        ))
    
    status = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder" : "",                
                "class": "form-control"
            }
        ))
    class Meta:
        model = GeneralSettings
        fields = ('site_name_abb','site_name', 'email','email2','site_desc','site_keyword','google_code','street','city','country','phone','street2','city2','country2','phone2','facebook','twitter','linkedin','google','reddit','tumblr','status','secondary_color','primary_color','slogan','file','file_2',)
        
        
  


class ContactForm(forms.Form): 
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={
                'placeholder':"Enter email address",                
                "class": "form-control",
            }
        ))  
    name = forms.CharField( 
        required=True,
        widget=forms.TextInput(
            attrs={             
                "class"       : "form-control",
                'placeholder':"Enter your name",
            }
        ))
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={             
                "class"       : "form-control",
                'placeholder':"Enter phone number",
            }
        ))
    subject = forms.CharField( 
        required=True,
        widget=forms.TextInput(
            attrs={             
                "class"       : "form-control",
                'placeholder':"Enter Subject",
            }
        ))
    interest = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Select an option'),
            ('volunteer', 'Volunteering'),
            ('donate', 'Making a Donation'),
            ('partner', 'Partnership Opportunities'),
            ('programs', 'Program Information'),
            ('other', 'Other')
        ],
        widget=forms.Select(
            attrs={             
                "class"       : "form-control",
            }
        ))
    message = forms.CharField( 
        required=True,
        widget=forms.Textarea(
            attrs={             
                "class"       : "form-control",
                'placeholder':"Enter Message",
            }
        ))
    


