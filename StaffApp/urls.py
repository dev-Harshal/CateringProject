from django.urls import path
from StaffApp.views import *

urlpatterns = [
    path('',Userorder,name='u-order'),
    path('ingredients/',ingredients,name='ingredients'),
    path('staff_login/',staffLogin,name="staff-login"),
]
