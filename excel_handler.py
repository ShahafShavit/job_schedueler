from json_handler import *

from openpyxl.styles import Font,Alignment
from openpyxl import Workbook

def column_auto_width(ws):
    for column in ws.columns:
        max_length = 0
        column = [cell for cell in column]
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(cell.value)
            except:
                pass
        adjusted_width = (max_length + 2)
        ws.column_dimensions[column[0].column_letter].width = adjusted_width
    # Create an alignment object with horizontal alignment set to "center"
    center_aligned = Alignment(horizontal="center")

    # Loop through all the cells in the worksheet and apply the alignment
    for row in ws.iter_rows():
        for cell in row:
            cell.alignment = center_aligned


def report_work_by_date_to_excel(month, wb):
    schedule_data = load_data_from_json(f"{config.get_location('output')}schedule_{month}.json")
    ws = wb.create_sheet(title="Work By Date")

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

    # Add headers
    ws.append(["Date", "Venue", "Employee ID"])

    # Write data to the worksheet
    for date, assignments in sorted(grouped_by_date.items(), key=lambda x: list(map(int, x[0].split("/")))):
        row_data = [date]
        for venue, employee_id in assignments:
            row_data.extend([venue, employee_id])
        ws.append(row_data)

    ws.append([])  # Add an empty row for separation

    # Write the number of shifts each employee received
    ws.append(["Shifts count:"])
    for employee_id, count in shifts_count.items():
        ws.append([employee_id, f"{count} shifts"])
    column_auto_width(ws)

def report_venue_dates_with_workers_to_excel(month, wb):
    schedule_data = load_data_from_json(f"{config.get_location('output')}schedule_{month}.json")
    ws = wb.create_sheet(title="Venue Dates With Workers")

    for venue, dates in schedule_data.items():
        ws.append([f"Venue: {venue}"])
        for date, worker in dates.items():
            ws.append([date, worker])
        ws.append(["------"])
    column_auto_width(ws)


def report_worker_shifts_to_excel(month, wb):
    schedule_data = load_data_from_json(f"{config.get_location('output')}schedule_{month}.json")

    worker_shifts = {}
    for venue, dates in schedule_data.items():
        for date, worker in dates.items():
            if worker not in worker_shifts:
                worker_shifts[worker] = []
            worker_shifts[worker].append((date, venue))

    # Add a new worksheet to the provided workbook
    ws = wb.create_sheet(title="Worker Shifts")

    # Add headers
    ws['A1'] = 'Worker'
    ws['B1'] = 'Date'
    ws['C1'] = 'Venue'
    ws['A1'].font = ws['B1'].font = ws['C1'].font = Font(bold=True)

    row = 2
    for worker, shifts in worker_shifts.items():
        for date, venue in sorted(shifts, key=lambda x: list(map(int, x[0].split("/")))):
            ws[f'A{row}'] = worker
            ws[f'B{row}'] = date
            ws[f'C{row}'] = venue
            row += 1
    column_auto_width(ws)

def generate_excel_reports(month):
    wb = Workbook()
    wb.remove(wb.active)  # Remove the default sheet

    report_worker_shifts_to_excel(month, wb)
    report_work_by_date_to_excel(month, wb)
    report_venue_dates_with_workers_to_excel(month, wb)

    # Ensure the directory exists
    makedirs(config.get_location('excel_reports'), exist_ok=True)

    # Save the workbook to a file
    wb.save(f"{config.get_location('excel_reports')}reports_{month}.xlsx")

