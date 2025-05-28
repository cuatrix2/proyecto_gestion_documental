from django.db import models

class Organization(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    company_name = models.CharField(max_length=255)
    identification = models.CharField(max_length=100)

    def __str__(self):
        return self.company_name

class User(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    job_title = models.CharField(max_length=100)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    role = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
class Department(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    department_name = models.CharField(max_length=255)
    owner = models.CharField(max_length=255)
    description = models.TextField()
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    def __str__(self):
        return self.department_name
    
class UsersDepartments(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

class QuickAccess(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    id_folder = models.CharField(max_length=100)
    id_user = models.ForeignKey(User, on_delete=models.CASCADE)

class Log(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    url = models.URLField()
    log = models.TextField()

class StorageOrganization(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    available_storage = models.FloatField()
    storage_used = models.FloatField()
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

class AITutorial(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
class AIMessage(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    role = models.CharField(max_length=50)
    ai_tutorial = models.ForeignKey(AITutorial, on_delete=models.CASCADE)
