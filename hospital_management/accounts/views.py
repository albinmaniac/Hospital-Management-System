from django.shortcuts import render,redirect
from django.views.generic import View
from django.contrib.auth import authenticate,login,logout
from accounts.forms import SignInForm

# Create your views here.
class SignoutView(View):

    def get(self,request,*args,**kwargs):

        logout(request)

        return redirect("login")
    
class SignInView(View):

    template_name='login.html'

    form_class=SignInForm

    def get(self,request,*args,**kwargs):

        form_instance=self.form_class()

        return render(request,self.template_name,{'form':form_instance})
    
    def post(self,request,*args,**kwargs):

        form_instance=self.form_class(request.POST)

        if form_instance.is_valid():

            uname=form_instance.cleaned_data.get('username')

            pwd=form_instance.cleaned_data.get('password')

            user_object=authenticate(request,username=uname,password=pwd)

            if user_object:

                login(request,user_object)

                return redirect('dashboard')
            
        return render(request,self.template_name,{'form':form_instance})