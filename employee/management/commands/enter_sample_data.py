import csv
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from leaves.models import LeaveBalance
from employee.models import Employee, Department

class Command(BaseCommand):
    help = 'Loads user, employee, department, and leave balance data from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file containing the data to load.')

    @transaction.atomic
    def handle(self, *args, **options):
        csv_file_path = options['csv_file']

        self.stdout.write(f"Starting to process {csv_file_path}...")

        users_to_process = []
        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                users_to_process.append(row)

        # create users, departments, employees, and leave balances
        for row in users_to_process:
            username = row['username'].strip()
            email = row['email'].strip()
            password = row['password']
            is_manager_val = row['is_manager'].strip().lower() == 'true'
            department_name = row['department'].strip().lower()

            # get or create department
            department, _ = Department.objects.get_or_create(name__iexact=department_name, defaults={'name': department_name})

            # create user if it doesn't exist
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'email': email}
            )
            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(f"Created user: {username}")

            # create or update employee
            employee, emp_created = Employee.objects.get_or_create(
                user=user,
                defaults={'is_manager': is_manager_val, 'department': department}
            )
            if not emp_created: # if employee already exists, update their details
                employee.is_manager = is_manager_val
                employee.department = department
                employee.save()

            # create or update leave balances
            balances = {
                'sick': float(row['sick_leave']),
                'casual': float(row['casual_leave']),
                'earned': float(row['earned_leave']),
            }
            for leave_type, balance_val in balances.items():
                LeaveBalance.objects.update_or_create(
                    employee=user,
                    leave_type=leave_type,
                    defaults={'balance': balance_val}
                )

        # assign managers
        for row in users_to_process:
            username = row['username'].strip()
            manager_username = row['manager'].strip()

            if manager_username:
                try:
                    reportee_employee = Employee.objects.get(user__username=username)
                    manager_user = User.objects.get(username=manager_username)
                    reportee_employee.manager = manager_user
                    reportee_employee.save()
                except (Employee.DoesNotExist, User.DoesNotExist) as e:
                    self.stdout.write(self.style.ERROR(f"Could not assign manager for {username}. Error: {e}"))

        self.stdout.write(self.style.SUCCESS('Data loading process complete.'))