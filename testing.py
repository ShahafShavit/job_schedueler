from json_handler import *
import random
from os import remove
import openpyxl
def generate_dummy_employee_data(month, num_employees=10): # <<<<< DEPRECATED >>>>>>>
    filename = "employees.json"
    data = []

    # Fetch the number of venues from the venues file
    venues_data = load_data_from_json(f"{config.get_location('data')}venues_{month}.json")
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
    filename = f"{config.get_location('data')}shifts_{month}.json"
    data = []

    # Fetch the employee names from the employees file
    employees_data = load_data_from_json("employees.json")

    for emp_data in employees_data:
        # Generate random number of unavailable dates for each employee
        num_unavailable_dates = random.randint(1, 8)
        unavailable_dates = [f"{random.randint(1, 30)}/{month}" for _ in range(num_unavailable_dates)]

        # Sort the dates
        unavailable_dates = sorted(list(set(unavailable_dates)), key=lambda x: (int(x.split("/")[1]), int(x.split("/")[0])))

        data.append({
            "id": emp_data["id"],
            "unavailable_dates": unavailable_dates
        })

    save_data_to_json(filename, data)

def generate_dummy_venue_data(month):
    filename = f"{config.get_location('data')}venues_{month}.json"
    data = []

    # Fetch the venue names from the employees file
    employees_data = load_data_from_json("employees.json")
    venue_names = list(set(venue for emp in employees_data for venue in emp["allowed_venues"].keys()))

    for venue_name in venue_names:
        # Generate random number of event dates for each venue
        num_event_dates = random.randint(10, 14)
        event_dates = [f"{random.randint(1, 30)}/{month}" for _ in range(num_event_dates)]

        # Sort the dates
        event_dates = sorted(list(set(event_dates)), key=lambda x: (int(x.split("/")[1]), int(x.split("/")[0])))

        data.append({
            "name": venue_name,
            "event_dates": event_dates
        })

    save_data_to_json(filename, data)



def delete_files_for_month(month):
    files_to_delete = [
        f"{config.get_location('data')}venues_{month}.json",
        f"{config.get_location('data')}shifts_{month}.json",
        f"{config.get_location('output')}schedule_{month}.json"
    ]

    for filename in files_to_delete:
        try:
            remove(filename)
            print(f"Deleted {filename}")
        except FileNotFoundError:
            print(f"{filename} not found.")
        except Exception as e:
            print(f"Error deleting {filename}: {e}")

import openpyxl
import random

def generate_dummy_unavailability_in_excel(year, month):
    # Load the Excel file
    filename = f"{config.get_location('calender_export')}Hagashot_{month}_{year}.xlsx"
    wb = openpyxl.load_workbook(filename)

    # For each sheet (employee) in the workbook
    for ws in wb.worksheets:
        print(f"Processing for {ws.title}")  # Debug print

        # For each day of the month
        for day in range(1, 31):  # Assuming 30 days in the month for simplicity
            # Find the column with this day
            for col_num, col_cells in enumerate(ws.iter_cols(min_col=5, max_col=11, min_row=5, max_row=ws.max_row, values_only=True), 5):
                if day in col_cells:
                    print(f"Identified day {day} in column {col_num}")  # Debug print

                    # Find the row of the identified day
                    day_row = col_cells.index(day) + 5

                    # Randomly decide whether to mark this day as unavailable
                    if random.random() < 0.2:
                        print(f"Marking day {day} as unavailable")  # Debug print

                        # Randomly choose one of the two cells below the date cell
                        unavailable_cell_row = day_row + random.randint(1, 2)
                        ws.cell(row=unavailable_cell_row, column=col_num).value = 'No'
                        break

    # Save the modified Excel file
    wb.save(filename)



