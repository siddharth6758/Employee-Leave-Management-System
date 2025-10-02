from django.contrib import admin
from employee.models import Employee, Department, Delegation
# Register your models here.

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ["user", "department", "manager", "is_manager"]
    search_fields = ["user__username", "department__name", "manager__username"]

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ["name"]

class DelegationAdmin(admin.ModelAdmin):
    list_display = ["manager", "delegate", "start_date", "end_date"]
    search_fields = ["manager__username", "delegate__username"]

admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Delegation, DelegationAdmin)