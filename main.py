import excel_handler
from json_handler import *
from random import choice
import testing
import reports
import ics_handler




# <<<<<<<<<<<<<<<<<<<<<<<<<<<<< EMPLOYEE AND EMPLOYEES CLASSES >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

class Employee:
    def __init__(self, id, allowed_venues):
        self.id = id
        self.allowed_venues = allowed_venues  # Dictionary with venue names as keys and weights as values
        self.unavailable_dates = {}  # Dictionary with dates as keys and list of booleans as values
        self.shift_count = 0

    def increment_shift(self):
        self.shift_count += 1

    def set_unavailability(self, date, shifts):
        """Set unavailability for specific shifts on a given date."""
        self.unavailable_dates[date] = shifts

class Employees:
    def __init__(self, month):
        self.month = month
        self.employees = self.load_employee_data()

    def load_employee_data(self):
        employees_data = load_data_from_json("employees.json")
        shifts_data = load_data_from_json(f"{config.get_location('data')}shifts_{self.month}.json")

        employees = []
        for data in employees_data:
            employee = Employee(data["id"], data["allowed_venues"])
            shift = next((s for s in shifts_data if s["id"] == employee.id), None)
            if shift:
                employee.unavailable_dates = shift["unavailable_dates"]
            employees.append(employee)

        return employees

    def save_employee_data(self):
        data = [{"id": emp.id, "allowed_venues": emp.allowed_venues} for emp in self.employees]
        save_data_to_json("employees.json", data)

        shifts_data = [{"id": emp.id, "unavailable_dates": emp.unavailable_dates} for emp in self.employees]
        save_data_to_json(f"{config.get_location('data')}shifts_{self.month}.json", shifts_data)


    def add_or_update_employee(self, employee_id, allowed_venues, unavailable_dates):
        for emp in self.employees:
            if emp.id == employee_id:
                emp.unavailable_dates = unavailable_dates  # Now a dictionary
                emp.allowed_venues = allowed_venues
                return
        self.employees.append(Employee(employee_id, allowed_venues))
        self.save_employee_data()

    def display_all_employees(self):
        print("Available employees:")
        for emp in self.employees:
            print(f"ID: {emp.id}")
        return [emp.id for emp in self.employees]

    def manually_input_employee_unavailability(self):
        available_employee_ids = self.display_all_employees()
        employee_id = input("Enter the employee ID: ")

        while employee_id not in available_employee_ids:
            print("Invalid employee ID. Please choose from the list above.")
            employee_id = input("Enter the employee ID: ")

        date = input("Enter the unavailable date for the employee (format: DD/MM): ")
        morning_unavailable = input("Is the employee unavailable in the morning? (yes/no) ").lower() == 'yes'
        evening_unavailable = input("Is the employee unavailable in the evening? (yes/no) ").lower() == 'yes'

        for emp in self.employees:
            if emp.id == employee_id:
                emp.set_unavailability(date, [morning_unavailable, evening_unavailable])
                break
        else:
            print(f"No employee found with ID {employee_id}")

        self.save_employee_data()


# <<<<<<<<<<<<<<<<<<<<<<<<<<<<< VENUE CLASS >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

class Venue:
    def __init__(self, name, event_dates):
        self.name = name
        self.event_dates = event_dates  # This is now a dictionary with dates as keys and shifts as values

    @classmethod
    def load_all_from_file(cls, month):
        venues_data = load_data_from_json(f"{config.get_location('data')}venues_{month}.json")
        return [cls(data["name"], data["event_dates"]) for data in venues_data]

    @classmethod
    def save_all_to_file(cls, month, venues):
        data = [{"name": venue.name, "event_dates": venue.event_dates} for venue in venues]
        save_data_to_json(f"{config.get_location('data')}venues_{month}.json", data)

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

    @classmethod
    def display_all_venues(cls, month):
        venues = cls.load_all_from_file(month)
        print("Available venues:")
        for venue in venues:
            print(venue.name)
        return [venue.name for venue in venues]

    @classmethod
    def manually_input_venue_dates(cls, month):
        available_venues = cls.display_all_venues(month)
        venue_name = input("Enter the venue name: ")

        while venue_name not in available_venues:
            print("Invalid venue name. Please choose from the list above.")
            venue_name = input("Enter the venue name: ")

        event_dates = {}
        num_dates = int(input("How many dates do you want to add? "))
        for _ in range(num_dates):
            date = input("Enter the date (format: DD/MM): ")
            morning_event = input("Is there a morning event on this date? (yes/no) ").lower() == 'yes'
            evening_event = input("Is there an evening event on this date? (yes/no) ").lower() == 'yes'
            event_dates[date] = [morning_event, evening_event]

        # Load existing venue data
        venues = cls.load_all_from_file(month)
        for venue in venues:
            if venue.name == venue_name:
                venue.event_dates.update(event_dates)
                break
        else:
            venues.append(cls(venue_name, event_dates))

        cls.save_all_to_file(month, venues)

    @classmethod
    def add_popup_event(cls, month, venue_name, event_date):
        venues = cls.load_all_from_file(month)
        morning_event = False  # Assuming no morning events for now
        evening_event = True   # Assuming all events are in the evening for now
        for venue in venues:
            if venue.name == venue_name:
                if event_date not in venue.event_dates:
                    venue.event_dates[event_date] = [morning_event, evening_event]
                break
        else:
            venues.append(cls(venue_name, {event_date: [morning_event, evening_event]}))
        cls.save_all_to_file(month, venues)



# <<<<<<<<<<<<<<<<<<<<<<<<<<<<< SCHEDULE CLASS >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
class Schedule:
    def __init__(self, month):
        self.month = month
        self.temp_unavailable = {}
        if self.schedule_exists():
            print("Schedule exists, no need to generate.")
            self.load_from_file()
        else:
            self.schedule_data = {}

    def schedule_exists(self):
        return path.exists(f"output/schedule_{self.month}.json")

    def load_from_file(self):
        self.schedule_data = load_data_from_json(f"output/schedule_{self.month}.json")

    def add_to_schedule(self, venue_name, date, shift_name, employee_id):
        if venue_name not in self.schedule_data:
            self.schedule_data[venue_name] = {}
        if date not in self.schedule_data[venue_name]:
            self.schedule_data[venue_name][date] = {}
        self.schedule_data[venue_name][date][shift_name] = employee_id

    def get_available_employees(self, date, shift, venue_name, employees):
        default_unavailability = [False] * config.get_default('default_shifts_per_day')

        return [employee for employee in employees if
                not employee.unavailable_dates.get(date, default_unavailability)[shift] and

                venue_name in employee.allowed_venues]

    def assign_employee_to_date(self, date, shift, available_employees):
        if not available_employees:
            return config.get_default('default_empty_shift')

        # Sort employees by shift count
        available_employees.sort(key=lambda x: x.shift_count)

        # If multiple employees have the same shift count, choose randomly among them
        min_shifts = available_employees[0].shift_count
        candidates = [emp for emp in available_employees if emp.shift_count == min_shifts]
        chosen_employee = choice(candidates)

        chosen_employee.shift_count += 1
        return chosen_employee

    def generate_schedule_for_venue(self, venue, employees):
        shifts_per_day = config.get_default('default_shifts_per_day')
        shift_names = config.get_default('default_shift_names')

        for date, shifts in venue.event_dates.items():
            for shift, is_event in enumerate(shifts):
                if is_event:
                    available_employees = self.get_available_employees(date, shift, venue.name, employees)
                    chosen_employee = self.assign_employee_to_date(date, shift, available_employees)

                    # Check if chosen_employee is an Employee object
                    if isinstance(chosen_employee, Employee):
                        # Ensure the unavailable_dates entry for the given date has the correct number of shifts
                        if date not in chosen_employee.unavailable_dates:
                            chosen_employee.unavailable_dates[date] = [False] * shifts_per_day

                        # Set the current shift as unavailable for the chosen employee
                        chosen_employee.unavailable_dates[date][shift] = True

                        # If there's a next shift, set it as unavailable for the chosen employee
                        if shift + 1 < shifts_per_day:
                            chosen_employee.unavailable_dates[date][shift + 1] = True

                        employee_id = chosen_employee.id
                    else:
                        employee_id = chosen_employee  # This is the default "EMPTY" value

                    # Use shift names from the config instead of shift numbers
                    self.add_to_schedule(venue.name, date, shift_names[shift], employee_id)

    def save_to_file(self):
        save_data_to_json(f"output/schedule_{self.month}.json", self.schedule_data)

    def sort_schedule_by_date(self):
        # Sort the dates for each venue
        for venue, dates in self.schedule_data.items():
            if venue != "shifts":
                sorted_dates = dict(sorted(dates.items(), key=lambda item: list(map(int, item[0].split("/")))))
                self.schedule_data[venue] = sorted_dates
        self.save_to_file()

    def manually_add_popup_event(self, employees_obj):
        # Get the list of available venues
        available_venues = Venue.display_all_venues(self.month)

        # Prompt the user for the venue name and validate it
        venue_name = input("Enter the venue name for the pop-up event: ")
        while venue_name not in available_venues:
            print("Invalid venue name. Please choose from the list above.")
            venue_name = input("Enter the venue name for the pop-up event: ")

        event_date = input("Enter the date for the pop-up event (format: DD/MM): ")

        shifts_per_day = config.get_default('default_shifts_per_day')
        for shift in range(shifts_per_day):
            # Get the list of available employees for the given venue and date
            available_employees = self.get_available_employees(event_date, shift, venue_name, employees_obj.employees)

            # Display the list of available employees
            print(f"\nAvailable employees for {venue_name} on {event_date} for shift {shift + 1}:")
            for emp in available_employees:
                print(emp.id)

            # Update the schedule_data with the list of available employees
            if venue_name not in self.schedule_data:
                self.schedule_data[venue_name] = {}
            if event_date not in self.schedule_data[venue_name]:
                self.schedule_data[venue_name][event_date] = {}
            self.schedule_data[venue_name][event_date][shift] = [emp.id for emp in available_employees]

        # Save the updated schedule_data to the schedule.json file
        self.save_to_file()

        # Update the venues_*.json file
        Venue.add_popup_event(self.month, venue_name, event_date)


# <<<<<<<<<<<<<<<<<<<<<<<<<<< MISC FUNCTIONS >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def fix_shift_imbalances(month):
    schedule_data = load_data_from_json(f"{config.get_location('output')}schedule_{month}.json")
    employees_data = load_data_from_json("employees.json")
    shifts_data = load_data_from_json(f"{config.get_location('data')}shifts_{month}.json")

    # Calculate the average number of shifts per employee
    total_shifts = sum([len(dates) for _, dates in schedule_data.items()])
    avg_shifts = total_shifts / len(employees_data)

    # Identify employees with too many or too few shifts
    overworked = []
    underworked = []
    for emp in employees_data:
        emp_shifts = sum([1 for _, worker in schedule_data.items() if worker == emp["id"]])
        if emp_shifts > avg_shifts:
            overworked.append((emp["id"], emp_shifts))
        elif emp_shifts < avg_shifts:
            underworked.append((emp["id"], emp_shifts))

    overworked.sort(key=lambda x: x[1], reverse=True)
    underworked.sort(key=lambda x: x[1])

    # Create a dictionary for quick lookup of unavailable dates
    unavailable_dates = {shift["id"]: shift["unavailable_dates"] for shift in shifts_data}

    for over_id, _ in overworked:
        for venue, dates in schedule_data.items():
            for date, worker in dates.items():
                if worker == over_id:
                    # Check if there's an underworked employee who can take this shift
                    for under_id, _ in underworked:
                        if date not in unavailable_dates.get(under_id, []) and venue in [emp["allowed_venues"] for emp in employees_data if emp["id"] == under_id][0]:
                            # Reassign the shift
                            schedule_data[venue][date] = under_id
                            break

    # Save the modified schedule
    save_data_to_json(f"{config.get_location('output')}schedule_{month}.json", schedule_data)



def main():
    month = "9"
    employee_manager = Employees(month)
    venues = Venue.load_all_from_file(month)
    monthly_schedule = Schedule(month)

    # If the schedule doesn't exist, generate it
    if not monthly_schedule.schedule_exists():
        print("Monthly schedule not yet created, creating schedule.")
        for venue in venues:
            monthly_schedule.generate_schedule_for_venue(venue, employee_manager.employees)
        monthly_schedule.save_to_file()

    # reports.generate_all_reports(month)
    ics_handler.generate_ics(monthly_schedule,month)
    # monthly_schedule.manually_add_popup_event(employee_manager)

# TODO: 1. Add venue event generation friday double-event
# TODO: 2. fix circular error for file dependencies when trying to generate testing data. generate some default data.