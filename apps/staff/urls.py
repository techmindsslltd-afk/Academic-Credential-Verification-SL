# -*- encoding: utf-8 -*-
"""
Copyright (c) 2024 - present TechMinds SL Ltd
"""
from django.urls import path, re_path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
 
    path('staff', views.index, name='staff'), 
    path('add_staff_2', views.create, name='add_staff'),
    path('update_staff/<int:id>', views.update, name='update_staff'),
    path('show_staff/<int:id>', views.show, name='show_staff'),
    path('delete_staff/<int:id>', csrf_exempt(views.delete), name='delete_staff'),
]