from django.contrib import admin

from .models import User, Organization, Department, UsersDepartments, QuickAccess,  StorageOrganization, Log, AIMessage, AITutorial

# Register your models here.

admin.site.register(User)
admin.site.register(Organization)
admin.site.register(Department)
admin.site.register(UsersDepartments)
admin.site.register(QuickAccess)
admin.site.register(StorageOrganization)
admin.site.register(AIMessage)
admin.site.register(AITutorial)
admin.site.register(Log)