from django.db import models
from apps.accounts.models import *
from django.utils import timezone
from datetime import date

# Create your models here.



class Staff(models.Model):
    staffNumber = models.CharField(max_length=255,blank=True, null=True )
    prefix = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    other_name = models.CharField(max_length=255,default=None,  blank=True, null=True)
    surname = models.CharField(max_length=255, blank=True, null=True)
    file = models.ImageField(default=False, blank=True, null=True, upload_to='UslStaffImage/')
    dob = models.DateField(default=None)
    nationality = models.CharField(max_length=255,default=None,  blank=True, null=True)
    region = models.CharField(max_length=255,default=None,  blank=True, null=True)
    gender = models.CharField(max_length=25,default=None,  blank=True, null=True)
    qualifications = models.TextField(
        max_length=255, blank=True, null=True)  # Department belong
    highest_qualification    = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255,default=None,  blank=True, null=True)
    phone = models.CharField(max_length=255, default=None, blank=True, null=True)
    email = models.EmailField(max_length=255, default=None, blank=True, null=True)
    is_active = models.BooleanField(default=True)  # continue Staff
    timestamp = models.DateTimeField(auto_now_add=True)
    data_sync = models.BooleanField(default=False, null=True, blank=True)
    created_online = models.BooleanField(default=False, null=True, blank=True)
    currentStatus = models.CharField(max_length=255,default=None,  blank=True, null=True)
    grade = models.BooleanField(default=False, null=True, blank=True)
    recordOwner = models.ForeignKey(User,verbose_name="Created by", related_name='%(class)s_recordOwner', on_delete=models.PROTECT, null=True, blank=True)
    update_by = models.ForeignKey(User,verbose_name="Update by", related_name='%(class)s_update_by', on_delete=models.PROTECT, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if len(self.staffNumber) == 1:
            obj= '(SF-00' +self.staffNumber + ')'  
        elif len(self.staffNumber) == 2:
            obj= '(SF-0' +self.staffNumber + ')'
        else:
            obj= '(SF-' +self.staffNumber + ')'
        return '%s %s %s %s %s' % (self.prefix, self.name, self.other_name, self.surname, (obj))
    
    
    
    @property
    def getstaffNumber(self):
        if len(self.staffNumber) == 1:
            obj= 'SF-00' +self.staffNumber  
        elif len(self.staffNumber) == 2:
            obj= 'SF-0' +self.staffNumber 
        else:
            obj= 'SF' + self.staffNumber 
        return obj
    
    @property
    def full_name(self):
        return '%s %s %s %s' % (self.prefix, self.name, self.other_name, self.surname)
    @property
    def full_name2(self):
        return '%s %s %s %s %s' % (self.prefix, self.name, self.other_name, self.surname, self.staffNumber)
    @property
    def contact(self):
         return  f" {self.phone}{'/'} {self.email} {'/'}{self.address} "
             
    @property
    def calculate_age(self):
        today = date.today()
        if self.dob:
            return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))
        else:
            return "no date of birth"
        
    @property
    def get_short_name(self):
        return '%s  %s' % (self.name,  self.surname)
        
    @property
    def contact(self):
         return  f" {self.phone}{'/'} {self.email} {'/'}{self.address} "
             
    @property
    def FullName(self):
        return '%s  %s %s' % (self.name,  self.other_name, self.surname)


