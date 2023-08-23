from json_handler import *
import random

def generate_dummy_employee_data(month, num_employees=10):
    filename = "employees.json"
    data = []

    # Fetch the number of venues from the venues file
    venues_data = load_data_from_json(f"venues_{month}.json")
    num_venues = len(venues_data)
    venue_names = [venue["name"] for venue in venues_data]

    for i in range(1, num_employees + 1):
        # Randomly assign 1 to 3 venues to each employee
        allowed_venues = random.sample(venue_names, random.randint(1, 3))

        data.append({
            "id": f"#E{i}",
            "allowed_venues": allowed_venues
        })

    save_data_to_json(filename, data)


def generate_dummy_shift_data(month):
    filename = f"shifts_{month}.json"
    data = []

    # Fetch the number of employees from the employees file
    employees_data = load_data_from_json("employees.json")
    num_employees = len(employees_data)

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
    employees_data = load_data_from_json("employees.json")
    shifts_data = load_data_from_json(f"shifts_{month}.json")

    employee_unavailable_dates = {shift["id"]: shift["unavailable_dates"] for shift in shifts_data}
    employee_allowed_venues = {emp["id"]: emp["allowed_venues"] for emp in employees_data}

    for venue, dates in schedule_data.items():
        if venue != "shifts":
            for date, employee_id in dates.items():
                if date in employee_unavailable_dates.get(employee_id, []):
                    print(f"Error: {employee_id} was assigned on {date} at {venue} but they are unavailable.")
                    return False
                if venue not in employee_allowed_venues.get(employee_id, []):
                    print(f"Error: {employee_id} was assigned to {venue} but they are not allowed to work there.")
                    return False

    print("Employees assigned without errors.")
    return True
