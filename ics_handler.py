from ics import Calendar, Event, Attendee
from json_handler import load_data_from_json,makedirs,config


def generate_ics(schedule, month):
    employees_data = load_data_from_json("employees.json")
    employee_email_map = {employee['id']: employee['email'] for employee in employees_data}
    # Create a new calendar
    cal = Calendar()

    for venue, dates in schedule.schedule_data.items():
        for date, worker in dates.items():
            # Split the date string
            day, month = date.split("/")
            # Construct a new date string in the YYYY-MM-DD format
            formatted_date = f"2023-{month.zfill(2)}-{day.zfill(2)}"  # Assuming the year is 2023
            event = Event()
            event.name = f"Shift for {worker} in {venue}"
            event.begin = f"{formatted_date} {config.get_default('default_time_start')}"
            event.end = f"{formatted_date} {config.get_default('default_time_end')}"
            event.location = venue
            event.description = f"Shift for {worker} at {venue} on {date}"
            worker_email = employee_email_map.get(worker)
            if worker_email:
                # Create Attendee object for worker
                worker_attendee = Attendee(email=worker_email, common_name=worker_email, role="REQ-PARTICIPANT"
                                           )
                event.attendees.add(worker_attendee)

                # Create Attendee object for default email
                default_attendee = Attendee(email=config.get_default('default_email'), common_name=config.get_default('default_email'),
                                            role="NON-PARTICIPANT")
                event.attendees.add(default_attendee)

            # Add the event to the calendar
            cal.events.add(event)

    # Ensure the directory exists
    makedirs(config.get_location('ics_export'), exist_ok=True)
    # Save the calendar to a file
    with open(f"{config.get_location('ics_export')}schedule_{month}.ics", "w") as ics_file:
        ics_file.write(cal.serialize())