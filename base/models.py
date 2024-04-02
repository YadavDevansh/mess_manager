from django.db import models
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin,BaseUserManager
from datetime import datetime

# Create your models here.

class CustomAccountManager(BaseUserManager):
    def create_superuser(self,username,first_name,last_name,bits_id,hostel,password,**other_fields):
        other_fields.setdefault('is_staff',True)
        other_fields.setdefault('is_superuser',True)
        return self.create_user(username,first_name,last_name,bits_id,hostel,password,**other_fields)

    def create_user(self,username,first_name,last_name,bits_id,hostel,password,**other_fields):
        user=self.model(username=username,first_name=first_name,last_name=last_name,hostel=hostel,bits_id=bits_id,**other_fields)
        user.set_password(password)
        user.is_active = True
        user.save()
        return user
    

class User(PermissionsMixin,AbstractBaseUser):
    objects=CustomAccountManager()
    username=models.CharField(max_length=50,unique=True,primary_key=True)
    first_name=models.CharField(max_length=50)
    last_name=models.CharField(max_length=50)
    bits_id=models.CharField(max_length=50)
    hostel=models.CharField(max_length=2)
    is_staff=models.BooleanField(default=False)
    is_active=models.BooleanField(default=True)
    USERNAME_FIELD='username'
    REQUIRED_FIELDS=['bits_id','is_staff','first_name','last_name','hostel']

    
    def __str__(self):
        return self.username

class MenuItem(models.Model):
    item_id=models.IntegerField(unique=True,primary_key=True)
    name=models.CharField(max_length=100)
    date=models.DateField()
    meal_type=models.CharField(max_length=10)
    def __str__(self):
        return self.name


class Rating(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    item=models.ForeignKey(MenuItem,on_delete=models.CASCADE)
    rating=models.FloatField(null=False)
    
    def __str__(self):
        x=str(self.rating)
        return x

class Complaint(models.Model):
    complaint_id=models.IntegerField(unique=True,primary_key=True)
    student=models.CharField(max_length=50)
    date_time=models.DateField()
    title=models.TextField()
    description=models.TextField()
    file_url=models.TextField()
    
    def __str__(self):
        x=str(self.complaint_id)
        return x

class Attendance(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    date=models.DateField(default=datetime.now)
    meal_type=models.CharField(max_length=10)

class LastAttendance(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    date=models.DateField(default=datetime.now)
    meal_type=models.CharField(max_length=10)