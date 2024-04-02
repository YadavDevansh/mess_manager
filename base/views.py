from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
import os
from . import models
from .menu_process import process
import requests
import datetime
import json
from json2html import *
from collections import defaultdict
from collections import Counter
import pandas as pd
from django.conf import settings
#import pytz

# Create your views here.

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful.')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid login credentials.')
            return render(request, 'login.html')
        
    elif request.user.is_authenticated:
        return redirect('dashboard')
    else:
        return render(request, 'login.html')

def user_logout(request):
    logout(request)
    messages.info(request, 'Logged out successfully.')
    return redirect('home')

def home(request):
    return render(request,'home.html')

@login_required
def dashboard(request):
    if request.user.is_staff or request.user.is_superuser:
        if request.method=='POST':
            data={}
            users=list(models.User.objects.filter(is_staff=False).values())
            users_list=[]
            fees_list=[]
            for user in users:
                fees=0
                today=datetime.date.today()
                fivedaysback=today-datetime.timedelta(days=5)
                attendance=list(models.Attendance.objects.filter(user_id=user['username'],date__gte=fivedaysback).values())
                for i in attendance:
                    if i['meal_type']=='breakfast':
                        fees+=80
                    elif i['meal_type']=='lunch':
                        fees+=180
                    elif i['meal_type']=='dinner':
                        fees+=150
                users_list.append(user['username'])
                fees_list.append(fees)
            data['Student']=users_list
            data['Fees']=fees_list
            df=pd.DataFrame(data)
            writer=open(f'static/bills/bill-{datetime.datetime.now().date()}.xlsx','wb+')
            df.to_excel(writer, sheet_name='Bills', index=False)
            writer.close()
        today=datetime.date.today()
        fivedaysback=today-datetime.timedelta(days=5)
        attendance=list(models.Attendance.objects.filter(date__gte=fivedaysback).values())
        #print(fivedaysback)
        data=[]
        for i in range(0,6):
            data.append({'date':today-datetime.timedelta(days=i),'breakfast':0,'lunch':0,'dinner':0})
        for i in attendance:
            index=(today-i['date']).days
            data[index][i['meal_type']]+=1
        print(data)
        context={'data':data}
        return render(request,'staff_dashboard.html',context)
    else:
        fi=open('static/menu/menu.json')
        menu=eval(fi.read())
        #print(menu)
        if menu:
            #context={'menu':menu}
            #eastern_tz = pytz.timezone('America/Sao_Paulo')
            #now = datetime.datetime.now(eastern_tz)
            
            #print(now)
            context={}
            now = datetime.datetime.now()
            now=now.replace(minute=0, hour=0, second=0, microsecond=0)
            print(type(menu[now]))
            if datetime.time(7,0,0)<=datetime.datetime.now().time()<=datetime.time(9,0,0):
                context['meal_type']='breakfast'
                context['menu']=menu[now]['breakfast']
            elif datetime.time(12,0,0)<=datetime.datetime.now().time()<=datetime.time(14,0,0):
                context['meal_type']='lunch'
                context['menu']=menu[now]['lunch']
            elif datetime.time(19,0,0)<=datetime.datetime.now().time()<=datetime.time(21,0,0):
                print('ok')
                context['meal_type']='dinner'
                context['menu']=menu[now]['dinner']
            elif datetime.datetime.now().time()<datetime.time(7,0,0):
                context['menu']=menu[now]['breakfast']
            elif datetime.datetime.now().time()<datetime.time(12,0,0):
                context['menu']=menu[now]['lunch']
            elif datetime.datetime.now().time()<datetime.time(19,0,0):
                context['menu']=menu[now]['dinner']
            elif datetime.datetime.now().time()>datetime.time(21,0,0):
                context['menu']=menu[now+datetime.timedelta(days=1)]['breakfast']
            print(context)
            if request.method == 'POST':
                attendance=models.Attendance(user_id=request.user.username,date=datetime.datetime.now().date(),meal_type=context['meal_type'])
                attendance.save()
                models.LastAttendance.objects.filter(user_id=request.user.username).delete()
                last_attendance=models.LastAttendance(user_id=request.user.username,date=datetime.datetime.now().date(),meal_type=context['meal_type'])
                last_attendance.save()
            try:
                if list(models.Attendance.objects.filter(user_id=request.user.username,date=datetime.datetime.now().date(),meal_type=context['meal_type']).all().values())==list(models.LastAttendance.objects.filter(user_id=request.user.username,date=datetime.datetime.now().date(),meal_type=context['meal_type']).all().values()):
                    del context['meal_type']
            except:
                pass
            return render(request,'student_dashboard.html',context)
        else:
            return render(request,'student_dashboard.html')
        

@login_required
def menu_upload(request):
    if request.user.is_staff or request.user.is_superuser:
        if request.method == 'POST' and request.FILES['upload']:
            upload = request.FILES['upload']
            try:
                os.remove('menu/'+str(upload.name))
            except:
                pass
            fss = FileSystemStorage(location='static/menu')
            file = fss.save(upload.name, upload)
            file_url = fss.url(file)
            result=process('static/menu'+requests.utils.unquote(file_url))
            models.MenuItem.objects.all().delete()
            models.Rating.objects.all().delete()
            for a,b in result.items():
                print(b)
                for c,d in b.items():
                    for k in d:
                        menuitem=models.MenuItem(date=a,name=k,meal_type=c)
                        menuitem.save()
            fi=open('static/menu/menu.json','w+')
            print(result,file=fi)
            fi.close()
            return render(request, 'menu_upload.html', {'uploaded': True})
        return render(request, 'menu_upload.html')
    else:
        return render(request,'student_dashboard.html')
    
@login_required
def file_complaint(request):
    if not request.user.is_staff or request.user.is_superuser:
        if request.method == 'POST' and request.FILES['upload']:
            upload = request.FILES['upload']
            title=request.POST['title']
            description=request.POST['description']
            student=request.user.username
            date_time=datetime.datetime.now()
            fss = FileSystemStorage(location='static/complaints')
            file = fss.save(upload.name, upload)
            file_url = 'complaints'+requests.utils.unquote(fss.url(file))
            print(file_url)
            complaint=models.Complaint(date_time=date_time,student=student,file_url=file_url,title=title,description=description)
            complaint.save()
            return render(request, 'file_complaint.html', {'uploaded': True})
        return render(request, 'file_complaint.html')
    else:
        return render(request,'staff_dashboard.html')
    
@login_required
def view_complaints(request):
    if request.user.is_staff or request.user.is_superuser:
        data=models.Complaint.objects.all().values()
        context={'complaints':data}
        return render(request,'view_complaints.html',context)
    else:
        return render(request,'student_dashboard.html')

@login_required
def rate_menu(request):
    if not request.user.is_staff or request.user.is_superuser:
        if request.method == 'POST':
            item_id = request.POST['item_id']
            rating = request.POST['rating']
            ratings=models.Rating(user_id=request.user.username,item_id=item_id,rating=rating)
            ratings.save()
        menu=list(models.MenuItem.objects.all().values())
        your_ratings=list(models.Rating.objects.filter(user_id=request.user.username).values())
        print(menu)
        print(your_ratings)
        d = defaultdict(dict)
        for item in menu + your_ratings:
            d[item['item_id']].update(item)
        final=list(d.values())
        context={'menu':final}
        return render(request,'rate_menu.html',context)
    else:
        return render(request,'staff_dashboard.html')
@login_required
def view_ratings(request):
    if request.user.is_staff or request.user.is_superuser:
        item_ids=len(models.MenuItem.objects.all())
        print(item_ids)
        data=[]
        for i in range(1,item_ids+1):
            fetched=list(models.Rating.objects.filter(item_id=i).values())
            fetched2=list(models.MenuItem.objects.filter(item_id=i).values())[0]
            sum=0
            for j in fetched:
                sum+=j['rating']
            try:
                avg=sum/len(fetched)
            except:
                avg=0
            data.append({'item_id':i,'name':fetched2['name'],'date':fetched2['date'],'meal_type':fetched2['meal_type'],'avg_rating':avg})
        print(data)
        context={'data':data}
        return render(request,'view_ratings.html',context)
    else:
        return render(request,'student_dashboard.html')

@login_required
def view_menu(request):
    if not request.user.is_staff or request.user.is_superuser:
        fi=open('static/menu/menu.json')
        menu=eval(fi.read())
        if menu:
            for date,date_menu in menu.items():
                menu[date]=json2html.convert(date_menu)
            context={'menu':menu}
            return render(request,"view_menu.html",context)
        else:
            return render(request,"view_menu.html")
    else:
        return render(request,"staff_dashboard.html")
    
@login_required
def calculate_fees(request):
    if request.user.is_staff or request.user.is_superuser:
        user=""
        if request.method == 'POST':
            user=request.POST['user']
        users=list(models.User.objects.filter(is_staff=False).values())
        fees=0
        today=datetime.date.today()
        fivedaysback=today-datetime.timedelta(days=5)
        attendance=list(models.Attendance.objects.filter(user_id=user,date__gte=fivedaysback).values())
        for i in attendance:
            if i['meal_type']=='breakfast':
                fees+=80
            elif i['meal_type']=='lunch':
                fees+=180
            elif i['meal_type']=='dinner':
                fees+=150

        if user=="":
            fees=None
        context={'users':users,'fees':fees,'user':user}
        return render(request,'calculate_fees.html',context)
    else:
        return render(request,'student_dashboard.html')