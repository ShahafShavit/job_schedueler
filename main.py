import json
import random

# <<<<<<<<<<<<<<<<<<<<<<<<<<<<< GENERAL CLASSES AND METHODS >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def load_data_from_json(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def save_data_to_json(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)


class Employee:
    def __init__(self, id, unavailable_dates):
        self.id = id
        self.unavailable_dates = unavailable_dates
        self.shift_count = 0

class Venue:
    def __init__(self, name, event_dates):
        self.name = name
        self.event_dates = event_dates

class Schedule:
    def __init__(self, month):
        self.month = month
        self.schedule_data = {}

    def add_to_schedule(self, venue_name, date, employee_id):
        if venue_name not in self.schedule_data:
            self.schedule_data[venue_name] = {}
        self.schedule_data[venue_name][date] = employee_id

    def get_schedule_for_venue(self, venue_name):
        return self.schedule_data.get(venue_name, {})


def add_employee_data(month, employee_id, unavailable_dates):
    filename = f"employees_{month}.json"

    # Load existing data
    data = load_data_from_json(filename)

    # Check if employee already exists
    for emp in data:
        if emp["id"] == employee_id:
            print(f"Employee with ID {employee_id} already exists. Updating data.")
            emp["unavailable_dates"] = unavailable_dates
            break
    else:
        # If employee doesn't exist, add new entry
        data.append({
            "id": employee_id,
            "unavailable_dates": unavailable_dates
        })

    # Save updated data
    save_data_to_json(filename, data)


def add_venue_data(month, venue_name, event_dates):
    filename = f"venues_{month}.json"

    # Load existing data
    data = load_data_from_json(filename)

    # Check if venue already exists
    for venue in data:
        if venue["name"] == venue_name:
            print(f"Venue {venue_name} already exists. Updating data.")
            venue["event_dates"] = event_dates
            break
    else:
        # If venue doesn't exist, add new entry
        data.append({
            "name": venue_name,
            "event_dates": event_dates
        })

    # Save updated data
    save_data_to_json(filename, data)


# <<<<<<<<<<<<<<<<<<< TESTING AND SORTING >>>>>>>>>>>>>>>>>>>>>>>>>


def generate_dummy_employee_data(month, num_employees=10):
    filename = f"employees_{month}.json"
    data = []

    for i in range(1, num_employees + 1):
        # Generate random number of unavailable dates for each employee
        num_unavailable_dates = random.randint(1, 8)
        unavailable_dates = [f"{random.randint(1, 30)}/{month}" for _ in range(num_unavailable_dates)]

        data.append({
            "id": f"#E{i}",
            "unavailable_dates": list(set(unavailable_dates))  # Remove duplicates
        })

    save_data_to_json(filename, data)


def generate_dummy_venue_data(month, num_venues=5):
    filename = f"venues_{month}.json"
    data = []

    for i in range(1, num_venues + 1):
        # Generate random number of event dates for each venue
        num_event_dates = random.randint(10, 14)
        event_dates = [f"{random.randint(1, 30)}/{month}" for _ in range(num_event_dates)]

        data.append({
            "name": f"Venue {chr(64 + i)}",  # This will give names like Venue A, Venue B, etc.
            "event_dates": list(set(event_dates))  # Remove duplicates
        })

    save_data_to_json(filename, data)

def test_schedule(month):
    schedule_data = load_data_from_json(f"schedule_{month}.json")
    employees_data = load_data_from_json(f"employees_{month}.json")

    employee_unavailable_dates = {emp["id"]: emp["unavailable_dates"] for emp in employees_data}

    for venue, dates in schedule_data.items():
        if venue != "shifts":
            for date, employee_id in dates.items():
                if date in employee_unavailable_dates[employee_id]:
                    print(f"Error: {employee_id} was assigned on {date} at {venue} but they are unavailable.")
                    return False
    print("Employees assigned without errors.")
    return True


def sort_schedule_by_date(month):
    schedule_data = load_data_from_json(f"schedule_{month}.json")

    # Sort the dates for each venue
    for venue, dates in schedule_data.items():
        if venue != "shifts":
            sorted_dates = dict(sorted(dates.items(), key=lambda item: list(map(int, item[0].split("/")))))
            schedule_data[venue] = sorted_dates

    save_data_to_json(f"schedule_{month}.json", schedule_data)

# <<<<<<<<<<<<<<<<<<<<<<<<<<< MISC FUNCTIONS >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def get_available_employees(date, employees):
    return [employee for employee in employees if date not in employee.unavailable_dates]

def assign_employee_to_date(date, available_employees):
    available_employees.sort(key=lambda x: x.shift_count)
    chosen_employee = available_employees[0]
    chosen_employee.shift_count += 1
    return chosen_employee

def generate_schedule_for_venue(venue, employees):
    venue_schedule = {}
    for date in venue.event_dates:
        available_employees = get_available_employees(date, employees)
        if available_employees:
            chosen_employee = assign_employee_to_date(date, available_employees)
            venue_schedule[date] = chosen_employee.id
    return venue_schedule

def calculate_shifts_for_employees(schedule_data, employees):
    shifts = {}
    for venue_schedule in schedule_data.values():
        for employee_id in venue_schedule.values():
            shifts[employee_id] = shifts.get(employee_id, 0) + 1
    return shifts

def show_assignments(month, specific_date=None):
    schedule_data = load_data_from_json(f"schedule_{month}.json")

    # Create a dictionary to group assignments by date
    grouped_by_date = {}

    for venue, dates in schedule_data.items():
        if venue != "shifts":
            for date, employee_id in dates.items():
                if date not in grouped_by_date:
                    grouped_by_date[date] = []
                grouped_by_date[date].append((venue, employee_id))

    if specific_date:
        assignments = grouped_by_date.get(specific_date, [])
        print(f"On {specific_date}: {assignments}")
    else:
        for date, assignments in sorted(grouped_by_date.items(), key=lambda x: list(map(int, x[0].split("/")))):
            print(f"{date}- {assignments}")


def main():
    # Load employees and venues for a specific month
    month = "09"
    employees_data = load_data_from_json(f"employees_{month}.json")
    venues_data = load_data_from_json(f"venues_{month}.json")

    employees = [Employee(data["id"], data["unavailable_dates"]) for data in employees_data]
    venues = [Venue(data["name"], data["event_dates"]) for data in venues_data]

    # Create a schedule for the month
    monthly_schedule = Schedule(month)

    for venue in venues:
        venue_schedule = generate_schedule_for_venue(venue, employees)
        for date, emp_id in venue_schedule.items():
            monthly_schedule.add_to_schedule(venue.name, date, emp_id)
    # Calculate shifts for each employee
    shifts = calculate_shifts_for_employees(monthly_schedule.schedule_data, employees)

    # Save the schedule to JSON
    schedule_to_save = monthly_schedule.schedule_data
    schedule_to_save["shifts"] = shifts
    save_data_to_json(f"schedule_{month}.json", schedule_to_save)

def test():
    generate_dummy_employee_data("09",8)
    generate_dummy_venue_data("09",3)

show_assignments("09")