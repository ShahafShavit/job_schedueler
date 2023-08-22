class Employee:
    def __init__(self, id, unavailable_dates):
        self.id = id
        self.unavailable_dates = unavailable_dates
        self.shift_count = 0

def get_available_employees(date, employees):
    return [employee for employee in employees if date not in employee.unavailable_dates]

def assign_employee_to_date(date, available_employees):
    # Sort employees by shift count and pick the one with the least shifts
    available_employees.sort(key=lambda x: x.shift_count)
    chosen_employee = available_employees[0]
    chosen_employee.shift_count += 1
    return chosen_employee

def generate_schedule(event_dates, employees):
    schedule = {}
    for date in event_dates:
        available_employees = get_available_employees(date, employees)
        if available_employees:
            chosen_employee = assign_employee_to_date(date, available_employees)
            schedule[date] = chosen_employee.id
    return schedule

# Example usage:
event_dates = ["6/9", "12/9", ...]
employee1 = Employee("#1", ["12/9", "17/9", ...])
employee2 = ...
employees = [employee1, employee2, ...]

schedule = generate_schedule(event_dates, employees)
print(schedule)
