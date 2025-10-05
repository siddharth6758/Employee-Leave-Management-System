# Employee-Leave-Management-System
This project is a robust and feature-rich Leave Management System built with Django. It provides a comprehensive platform for employees to request time off and for managers to approve, reject, and track leave across their teams and departments. The system is designed to be scalable and maintainable, featuring automated mail-notifications, reporting, and employee/manager-based access control.

## Key Features

*   **Employee Dashboard**: A central hub for employees to view their current leave balances (Sick, Casual, Earned), apply for new leave, and view the status and history of all their past requests.
  <img width="1279" height="506" alt="image" src="https://github.com/user-attachments/assets/d5495758-6503-4fb9-a062-866b4685bd7e" />


*   **Manager & Delegate Views**:
    *   **Manager Dashboard**: Managers get a special view of all pending leave requests from their direct subordinates.
    *   **Delegation**: Managers can delegate their approval responsibilities to another employee for a specific period, ensuring no request is left pending.
    *   **AJAX Actions**: Approve or reject leave requests directly from the dashboard without a page reload for a smooth, modern user experience.
  <img width="1178" height="679" alt="image" src="https://github.com/user-attachments/assets/ae594e94-d232-42bf-a70f-fc82495898a0" />


*   **Advanced Form Validation**:
    *   Leave request forms prevent applications with overlapping dates.
    *   Checks for sufficient leave balance before allowing a request to be submitted.
    *   Enforces business logic, such as allowing back-dated leave only for "Sick" leave types.

*   **Automated Leave Balance Management**:
    *   Leave balances are automatically deducted from an employee's account.
    *   If an approved leave request is deleted, the leave days are automatically credited back to the employee's balance. This logic is handled atomically to prevent race conditions and ensure data integrity.

*   **Comprehensive Reporting**:
    *   A powerful reporting page that allows viewing all leave requests across the company.
    *   Filter reports to view a flat list of all leaves or a grouped view organized by department.
    *   Export the current report view to a CSV file for offline analysis.
  <img width="1162" height="473" alt="image" src="https://github.com/user-attachments/assets/1c28f3f4-3b78-4028-8b5f-a841ca47a8fd" />


*   **Automated Email Notifications**:
    *   The system uses Django Signals to send emails automatically.
    *   When an employee submits a request, their manager receives an email notification.
    *   When a manager approves or rejects a request, the employee receives an email with the status update.
    *   When a manager applies for a delegate, the delegate recieves an email notification

*   **Data Population Command**:
    *   Includes a custom Django management command (`enter_sample_data`) to bulk-load user, employee, department, and leave balance data from a CSV file, making it easy to set up a new instance with test data.
    ```
    python manage.py enter_sample_data .\sample_data.csv
    ```

## Installation Instructions

Follow these steps to set up the project locally for development.

### Prerequisites
*   Python 3.8+
*   pip & venv
*   Git

### Setup
1.  **Clone the Repository**
    ```
    git clone  https://github.com/siddharth6758/Employee-Leave-Management-System.git
    cd Employee-Leave-Management-System
    ```

2.  **Create and Activate a Virtual Environment**
    *   On macOS/Linux:
        ```
        python3 -m venv env
        source env/bin/activate
        ```
    *   On Windows:
        ```
        python -m venv env
        .\env\Scripts\activate
        ```

3.  **Install Dependencies**
    Install the dependencies:
    ```
    pip install -r requirements.txt
    ```

4.  **Apply Database Migrations**
    Run the following command to create the necessary database tables:
    ```
    python manage.py migrate
    ```

5.  **Create a Superuser**
    Create an admin account to access the Django admin site:
    ```
    python manage.py createsuperuser
    ```

6.  **Populate with Sample Data (Optional)**
    Use the management command to load the sample data from `sample_data.csv`:
    ```
    python manage.py enter_sample_data .\sample_data.csv
    ```

7.  **Run the Development Server**
    ```
    python manage.py runserver
    ```

    The application will now be running at `http://127.0.0.1:8000/`. You can log in with the credentials created in the CSV file or with your superuser account.
