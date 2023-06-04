from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Location(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name
    
# To create custom user with location access

from django.contrib.auth.models import AbstractUser



class Project(models.Model):
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    authorized_users = models.ManyToManyField(User, related_name='authorized_projects', blank=True)
    name = models.CharField(max_length=200)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    totalamount = models.IntegerField(null=True, blank=True)
    payments_todate = models.IntegerField(null=True,blank=True)
    description = models.TextField(null=True,blank = True)
    updated = models.DateTimeField(auto_now = True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated','-created']

    def __str__(self):
        return self.name


class Remark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project,related_name='project_content_type', on_delete=models.CASCADE)
    body = models.TextField()
    updated = models.DateTimeField(auto_now = True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-updated','-created']
        
    def __str__(self):
        return self.body[0:50]


