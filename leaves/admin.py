from django.contrib import admin
from leaves.models import LeaveBalance, LeaveRequest

class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ["employee", "leave_type", "balance"]

class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ["employee", "leave_type", "status", "start_date", "end_date"]
    search_fields = ["employee__username", "leave_type"]

    def delete_model(self, request, obj):
        obj.delete()

    #for multiple delete
    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.delete()

admin.site.register(LeaveBalance, LeaveBalanceAdmin)
admin.site.register(LeaveRequest, LeaveRequestAdmin)