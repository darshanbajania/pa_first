#Date Created: 29-5-20

#contains views for the App
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from .forms import BookForm,ProposalForm, UserUpdateForm, ProfileUpdateForm
from .models import Book
from .models import Proposal,profile
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import confusion_matrix
import nltk
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize 
from sklearn.cluster import KMeans
import pandas as pd
import pickle
import numpy as np
import string
import re
from . import categorize
import collections
import random
from . import kmeans


# Create your views here.
# to test for upload 
#def upload(request):
#        print(uploaded_file.size)
#        fs = FileSystemStorage()
#        name = fs.save(uploaded_file.name,uploaded_file)
#        context['url'] = fs.url(name)
    
 #   return render(request, 'pol/upload.html',context)
# to show uploaded books
# def book_list(request):
#    books = Book.objects.all()
#    return render(request,'pol/book_list.html',{
#        'books':books
#    })

# to upload user pdf
def Upload_book(request):
    if request.session.has_key('my_car'): # checking for session
        form = ProposalForm()             # creating instance of proposal form 
        if request.method == 'POST':
            form = ProposalForm(request.POST,
                                    request.FILES,
                                    instance=request.user.profile)
            if form.is_valid():           # if form data is valid then
                form.save()               # save it and redirect to dashboard
                return redirect('pol:dashboard')
            else:                         # else stay on he same page 
                form = ProposalForm(instance=request.user.profile)

        return render(request,'pol/Upload_book.html',{'form':form})
    else :
        return redirect('pol:mhome')

# home page
def index_view(request):
    if request.user.is_authenticated :          # checking is user authenticated
        request.session['my_car'] = True        # setting sessions value 
        return render(request, 'pol/index.html') # if user is authenticated go to home page
    else :
        return redirect('pol:login_urls')       #else to login page


#Categotizer page
def home_view(request):
    #takes value from search
    text=request.POST.get('searches')
    
    new_text = text
    w_tfidf={}
    [w_tfidf,word_v]=categorize.categorize_idf(new_text)
    
    if new_text!=None:
        categ_text=kmeans.kmean_categorize(new_text)
        text_categ = {
            'categ_text' : categ_text,
        }
    else:
        categ_text = {
            'km' : "  "
        }
    
    categ_str = {
        'h' : '',
        'string' : new_text,
    }
    categ_extract = kmeans.kmean_categorize(word_v)
    categ1 = {
        'categ_extract' : categ_extract,
    }    
    #print(z)
    return render(request, 'pol/base.html', {'w_tfidf' : w_tfidf,'categ1' : categ1, 
    'categ_str' : categ_str, 'categ_text' : categ_text})

def Resource_View(request):
    if request.session.has_key('my_car'):     
        return render(request,'pol/resources.html')
    else:
        return redirect('pol:mhome')

@login_required

def Profile_View(request):
    if request.session.has_key('my_car'): 
        if request.method == 'POST':
            u_form = UserUpdateForm(request.POST, instance=request.user)
            p_form = ProfileUpdateForm(request.POST,
                                    request.FILES,
                                    instance=request.user.profile)
            if u_form.is_valid() and p_form.is_valid():
                u_form.save()
                p_form.save()
                messages.success(request, f'Your account has been updated!')
                return redirect('pol:profile')

        else:
            u_form = UserUpdateForm(instance=request.user)
            p_form = ProfileUpdateForm(instance=request.user.profile)

        context = {
            'u_form': u_form,
            'p_form': p_form
        }

        return render(request,'pol/profile.html',context)

    else:
        return redirect('pol:mhome')
    

def dashboard_view(request):       #for dashboard
    prop = ProposalForm(instance=request.user.profile)
    return render(request,'pol/dashboard.html',{'prop':prop})

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pol:login_urls')
    else:
        form = UserCreationForm()
    return render(request,'registration/register.html',{'form':form})

