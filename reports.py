
from json_handler import *
import re

def remove_color_codes(text):
    # Regular expression pattern to match ANSI escape codes
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    END = '\033[0m'


def save_report_to_file(content, filename):
    # Ensure the directory exists
    if not path.exists("output/reports"):
        makedirs("output/reports")
    clean_content = remove_color_codes(content)

    with open(f"output/reports/{filename}", 'w') as file:
        file.write(clean_content)
def report_work_by_date(month):
    schedule_data = load_data_from_json(f"output/schedule_{month}.json")

    # Create a dictionary to group assignments by date
    grouped_by_date = {}
    # Create a dictionary to count shifts for each employee
    shifts_count = {}


    for venue, dates in schedule_data.items():
        for date, employee_id in dates.items():
            if date not in grouped_by_date:
                grouped_by_date[date] = []
            grouped_by_date[date].append((venue, employee_id))

            # Count shifts for each employee
            shifts_count[employee_id] = shifts_count.get(employee_id, 0) + 1


    # Build the report content as a string
    report_content = ""

    # Display assignments for each date
    for date, assignments in sorted(grouped_by_date.items(), key=lambda x: list(map(int, x[0].split("/")))):
        report_content += f"{date}- {assignments}\n"

    # Display the number of shifts each employee received
    report_content += "\nShifts count for each employee:\n"
    for employee_id, count in shifts_count.items():
        report_content += f"{employee_id}: {count} shifts\n"

    # Print the report content
    print(report_content)

    # Save the report content to a .txt file
    save_report_to_file(report_content, f"work_by_date_{month}.txt")


def report_venue_dates_with_workers(month):
    schedule_data = load_data_from_json(f"output/schedule_{month}.json")

    report_content = ""
    for venue, dates in schedule_data.items():
        report_content += f"Venue: {venue}\n"
        for date, worker in dates.items():
            report_content += f"{date}: {worker}\n"
        report_content += "------\n"

    print(report_content)
    save_report_to_file(report_content, f"venue_dates_with_workers_{month}.txt")

def report_worker_shifts(month):
    schedule_data = load_data_from_json(f"output/schedule_{month}.json")

    worker_shifts = {}
    for venue, dates in schedule_data.items():
        for date, worker in dates.items():
            if worker not in worker_shifts:
                worker_shifts[worker] = []
            worker_shifts[worker].append((date, venue))

    report_content = ""
    for worker, shifts in worker_shifts.items():
        sorted_shifts = sorted(shifts, key=lambda x: list(map(int, x[0].split("/"))))
        report_content += f"Worker: {worker}\n"
        for date, venue in sorted_shifts:
            report_content += f"{date} at {venue}\n"
        report_content += "------\n"

    print(report_content)
    save_report_to_file(report_content, f"worker_shifts_{month}.txt")

def report_errors(month):
    schedule_data = load_data_from_json(f"output/schedule_{month}.json")
    employees_data = load_data_from_json("employees.json")
    shifts_data = load_data_from_json(f"data/shifts_{month}.json")
    venues_data = load_data_from_json(f"data/venues_{month}.json")

    employee_unavailable_dates = {shift["id"]: shift["unavailable_dates"] for shift in shifts_data}
    employee_allowed_venues = {emp["id"]: emp["allowed_venues"] for emp in employees_data}

    report_content = ""
    all_is_well = True  # Assume everything is correct initially

    # Check for unassigned dates
    for venue in venues_data:
        venue_name = venue["name"]
        for date in venue["event_dates"]:
            if date not in schedule_data.get(venue_name, {}):
                print(f"{Colors.RED}Error: No employee assigned on {date} at {venue_name}.")
                all_is_well = False

    for venue, dates in schedule_data.items():
        if venue != "shifts":
            for date, employee_id in dates.items():
                if employee_id == "EMPTY":
                    print(f"{Colors.RED}Warning: No employee was available on {Colors.END}{date} {Colors.RED}at{Colors.END} {venue}.")
                    all_is_well = False
                elif date in employee_unavailable_dates.get(employee_id, []):
                    print(f"{Colors.RED}Error: {employee_id} was assigned on {Colors.END}{date}{Colors.RED} at {Colors.END}{venue}{Colors.RED} but they are unavailable.")
                    all_is_well = False
                elif venue not in employee_allowed_venues.get(employee_id, []):
                    print(f"{Colors.RED}Error: {employee_id} was assigned to {Colors.END}{venue}{Colors.RED} but they are not allowed to work there.")
                    all_is_well = False

    if all_is_well:
        report_content += f"{Colors.GREEN}Employees assigned without errors.{Colors.END}\n"
    else:
        report_content += f"{Colors.RED}There were errors in the assignment.{Colors.END}\n"
    print(report_content)
    save_report_to_file(report_content, f"errors_{month}.txt")

    return all_is_well
