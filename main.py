from testing import *

# <<<<<<<<<<<<<<<<<<<<<<<<<<<<< EMPLOYEE AND EMPLOYEES CLASSES >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

class Employee:
    def __init__(self, id, allowed_venues):
        self.id = id
        self.allowed_venues = allowed_venues
        self.unavailable_dates = []  # This will be populated from the shifts file
        self.shift_count = 0

    def increment_shift(self):
        self.shift_count += 1

class Employees:
    def __init__(self, month):
        self.month = month
        self.employees = self.load_from_file()

    def load_from_file(self):
        employees_data = load_data_from_json("employees.json")
        shifts_data = load_data_from_json(f"shifts_{self.month}.json")

        employees = []
        for data in employees_data:
            employee = Employee(data["id"], data["allowed_venues"])
            shift = next((s for s in shifts_data if s["id"] == employee.id), None)
            if shift:
                employee.unavailable_dates = shift["unavailable_dates"]
            employees.append(employee)

        return employees

    def save_to_file(self):
        data = [{"id": emp.id, "allowed_venues": emp.allowed_venues} for emp in self.employees]
        save_data_to_json("employees.json", data)

        shifts_data = [{"id": emp.id, "unavailable_dates": emp.unavailable_dates} for emp in self.employees]
        save_data_to_json(f"shifts_{self.month}.json", shifts_data)

    def load_shifts(self):
        shifts_data = load_data_from_json(f"shifts_{self.month}.json")
        for shift in shifts_data:
            employee = next((e for e in self.employees if e.id == shift["id"]), None)
            if employee:
                employee.unavailable_dates = shift["unavailable_dates"]

    def save_shifts(self):
        data = [{"id": emp.id, "unavailable_dates": emp.unavailable_dates} for emp in self.employees]
        save_data_to_json(f"shifts_{self.month}.json", data)
    def add_or_update_employee(self, employee_id, unavailable_dates):
        for emp in self.employees:
            if emp.id == employee_id:
                emp.unavailable_dates = unavailable_dates
                return
        self.employees.append(Employee(employee_id, unavailable_dates))
        self.save_to_file()



# <<<<<<<<<<<<<<<<<<<<<<<<<<<<< VENUE CLASS >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

class Venue:
    def __init__(self, name, event_dates):
        self.name = name
        self.event_dates = event_dates

    @classmethod
    def load_all_from_file(cls, month):
        venues_data = load_data_from_json(f"venues_{month}.json")
        return [cls(data["name"], data["event_dates"]) for data in venues_data]
    @classmethod
    def save_all_to_file(cls, month, venues):
        data = [{"name": venue.name, "event_dates": venue.event_dates} for venue in venues]
        save_data_to_json(f"venues_{month}.json", data)

    @classmethod
    def add_or_update_venue(cls, month, venue_name, event_dates):
        venues = cls.load_all_from_file(month)
        for venue in venues:
            if venue.name == venue_name:
                venue.event_dates = event_dates
                break
        else:
            venues.append(cls(venue_name, event_dates))
        cls.save_all_to_file(month, venues)


# <<<<<<<<<<<<<<<<<<<<<<<<<<<<< SCHEDULE CLASS >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
class Schedule:
    def __init__(self, month):
        self.month = month
        self.schedule_data = {}
        self.temp_unavailable = {}

    def add_to_schedule(self, venue_name, date, employee_id):
        if venue_name not in self.schedule_data:
            self.schedule_data[venue_name] = {}
        self.schedule_data[venue_name][date] = employee_id
        if date not in self.temp_unavailable:
            self.temp_unavailable[date] = []
        self.temp_unavailable[date].append(employee_id)

    def get_available_employees(self, date, venue_name, employees):
        # Exclude employees who worked the previous day
        previous_day = f"{int(date.split('/')[0]) - 1}/{date.split('/')[1]}"
        recently_worked = self.temp_unavailable.get(previous_day, [])

        return [employee for employee in employees if
                date not in employee.unavailable_dates and
                employee.id not in self.temp_unavailable.get(date, []) and
                employee.id not in recently_worked and
                venue_name in employee.allowed_venues]

    def assign_employee_to_date(self, date, available_employees):
        # Sort employees by shift count
        available_employees.sort(key=lambda x: x.shift_count)

        # If multiple employees have the same shift count, choose randomly among them
        min_shifts = available_employees[0].shift_count
        candidates = [emp for emp in available_employees if emp.shift_count == min_shifts]
        chosen_employee = random.choice(candidates)

        chosen_employee.shift_count += 1
        return chosen_employee

    def generate_schedule_for_venue(self, venue, employees):
        for date in venue.event_dates:
            available_employees = self.get_available_employees(date, venue.name, employees)  # Pass the venue name
            if available_employees:
                chosen_employee = self.assign_employee_to_date(date, available_employees)
                self.add_to_schedule(venue.name, date, chosen_employee.id)

    def save_to_file(self):
        save_data_to_json(f"schedule_{self.month}.json", self.schedule_data)

    def sort_schedule_by_date(self):
        # Sort the dates for each venue
        for venue, dates in self.schedule_data.items():
            if venue != "shifts":
                sorted_dates = dict(sorted(dates.items(), key=lambda item: list(map(int, item[0].split("/")))))
                self.schedule_data[venue] = sorted_dates
        self.save_to_file()




# <<<<<<<<<<<<<<<<<<<<<<<<<<< MISC FUNCTIONS >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>


def generate_report(month):
    schedule_data = load_data_from_json(f"schedule_{month}.json")

    # Create a dictionary to group assignments by date
    grouped_by_date = {}

    # Create a dictionary to count shifts for each employee
    shifts_count = {}

    for venue, dates in schedule_data.items():
        if venue != "shifts":
            for date, employee_id in dates.items():
                if date not in grouped_by_date:
                    grouped_by_date[date] = []
                grouped_by_date[date].append((venue, employee_id))

                # Count shifts for each employee
                shifts_count[employee_id] = shifts_count.get(employee_id, 0) + 1

    # Display assignments for each date
    for date, assignments in sorted(grouped_by_date.items(), key=lambda x: list(map(int, x[0].split("/")))):
        print(f"{date}- {assignments}")

    # Display the number of shifts each employee received
    print("\nShifts count for each employee:")
    for employee_id, count in shifts_count.items():
        print(f"{employee_id}: {count} shifts")


def main():
    month = "09"
    employee_manager = Employees(month)
    employee_manager.load_shifts()
    venues = Venue.load_all_from_file(month)

    monthly_schedule = Schedule(month)
    for venue in venues:
        monthly_schedule.generate_schedule_for_venue(venue, employee_manager.employees)

    monthly_schedule.save_to_file()


def test(month):
    generate_dummy_venue_data(month,num_venues=4)
    generate_dummy_shift_data(month)


test("09")
main()
test_schedule("09")
generate_report("09")

