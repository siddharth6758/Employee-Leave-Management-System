from django.db import models
from model_utils.models import TimeStampedModel
from django.contrib.auth.models import User

class Department(TimeStampedModel):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"
    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"


class Employee(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_manager = models.BooleanField(default=False)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="manager")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} : {self.department.name if self.department else '--'}"

    class Meta:
        verbose_name = "Employee"
        verbose_name_plural = "Employees"

class Delegation(TimeStampedModel):
    manager = models.ForeignKey(User,on_delete=models.CASCADE,related_name='delegations_given_by')
    delegate = models.ForeignKey(User,on_delete=models.CASCADE,related_name='delegations_received_by')
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    class Meta:
        verbose_name = "ManagerDelegation"
        verbose_name_plural = "ManagerDelegations"

    def __str__(self):
        return f"{self.manager} delegates to {self.delegate}"