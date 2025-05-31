from django.db import models
from django.contrib.auth.models import User


class Organization(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

class Department(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=False, blank=False)
    

class Folder(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    deparment = models.ForeignKey(Department, on_delete=models.CASCADE, null=False, blank=False)
    
    


class Document(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    url = models.URLField(null= True, blank= True)
    text = models.TextField(null= True, blank= True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=False, blank=False)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, null=False, blank=False)
    
 

