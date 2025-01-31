from django.shortcuts import render,redirect
from django.views.generic import View
from django.contrib.auth import authenticate,login,logout
# Create your views here.
class SignoutView(View):

    def get(self,request,*args,**kwargs):

        logout(request)

        return redirect("login")
    
