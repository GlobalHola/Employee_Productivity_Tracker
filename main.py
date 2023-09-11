### Freelancer Activity Tracker
### Provided Free via Global Hola

import datetime
from pynput import mouse, keyboard
import schedule
import time
from tkinter import Tk, Label, Button, Entry, StringVar, font, PhotoImage
import requests
import psutil
import json
import pygetwindow as gw
import webbrowser
from urllib.parse import urlparse
import re
import threading
import logging
import random
import os
from cryptography.fernet import Fernet

# Activity Monitoring
global mouse_clicks
global key_presses
global start_timestamp
global time_start
global time_stop
global zero_interaction_periods
global previous_time_start

mouse_clicks = 0
key_presses = 0
start_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
zero_interaction_periods = 0
time_start = None
previous_time_start = None


def is_valid_url(url):

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.info(str(timestamp) + ": " + "Checking is valid URL")
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def is_valid_email(email):

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.info(str(timestamp) + ": " + "Checking is valid Email")
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email))

def on_click(x, y, button, pressed):

    global mouse_clicks
    if pressed:
        mouse_clicks += 1


def on_key_press(key):
    global key_presses
    key_presses += 1

def get_active_window_title():

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.info(str(timestamp) + ": " + "Getting active window title...")
    window = gw.getActiveWindow()
    if window:
        return window.title
    else:
        return "No active window"

def get_open_programs():

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.info(str(timestamp) + ": " + "Getting active programs in list")
    target_apps = \
        [
        'word',
        'slack',
        'excel',
        'chrome',
        'firefox',
        'outlook',
        'powerpoint',
        'photoshop',
        'onenote',
        'microsoft edge',
        'teams',  # Microsoft Teams
        'skype',
        'adobe reader',
        'acrobat',  # Adobe Acrobat
        'illustrator',
        'premiere',  # Adobe Premiere Pro
        'vscode',  # Visual Studio Code
        'eclipse',
        'pycharm',
        'zoom',
        'trello',
        'asana',
        'spotify',  # Often used in a work context for background music
        'discord',
        'notion',
        'evernote',
        'calendar',  # Google Calendar
        'drive',  # Google Drive
        'sheets',  # Google Sheets
        'docs',  # Google Docs
        'thunderbird',  # Mozilla Thunderbird email client
        'postman',  # API development and testing tool
        'intellij',  # IntelliJ IDEA (for Java development)
        'jira',  # Project management
        'confluence',  # Documentation
        'canva',  # Graphics design
        'indesign',  # Adobe InDesign
        'lightroom',  # Adobe Lightroom
        'autocad',  # CAD software
        'safari',  # Apple's web browser
        'opera',  # Web browser
        'brave',  # Web browser
        'todoist',  # Task management
        'things',  # Task management for Mac
        'vim',  # Text editor
        'emacs',  # Text editor
        'sublime',  # Sublime Text editor
        'atom',  # Text editor
        'sqlserver',  # Microsoft SQL Server
        'mysqlworkbench',  # MySQL Workbench
        'tableau',  # Data visualization
        'airtable',  # Spreadsheet-database hybrid
        'filezilla',  # FTP client
        'dropbox'
        ] #extend the list as needed

    procs = [proc.info for proc in psutil.process_iter(attrs=['pid', 'name']) if proc.info['name']]

    open_apps = []
    for proc in procs:
        for app in target_apps:
            if app in proc['name'].lower():
                open_apps.append(proc['name'])

    return list(set(open_apps))  # Remove duplicates


def save_to_json(email, mouse_clicks, key_presses, current_project, time_start):

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.info(str(timestamp) + ": " + "Placing data in JSON file.")

    time_start_text = time_start.strftime("%Y-%m-%d %H:%M")

    elapsed_time = datetime.datetime.now() - time_start
    minutes_tracked = int(elapsed_time.total_seconds() / 60)

    data = \
        {
        'email': email,
        'mouse_clicks': mouse_clicks,
        'key_presses': key_presses,
        'current_project': current_project,
        'open_programs': get_open_programs(),
        'active_window_title': get_active_window_title(),
        'date': time_start.strftime("%Y-%m-%d"),
        'time_started': time_start_text,
        'time_stopped': datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        'minutes_tracked' : minutes_tracked
        }

    return data


def send_to_webhook(data, webhook_url):

    global mouse_clicks
    global key_presses
    global zero_interaction_periods
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.info(str(timestamp) + ": " + "Sending data to webhook: " + webhook_url)

    if(len(webhook_url) > 5):

        response = requests.post(webhook_url, json=data)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.info(str(timestamp) + ": " + "Data sent: " + str(data))
        logging.info(str(timestamp) + ": " + "Webhook response: " + str(response))

        mouse_clicks = 0
        key_presses = 0
        return response.status_code
    else:
        mouse_clicks = 0
        key_presses = 0

    # Close Program if this is the 4th period of inactivity
    if mouse_clicks == 0 and key_presses == 0:
        zero_interaction_periods += 1
        if zero_interaction_periods >= 4:
            app.stop_monitoring()
            app.on_closing()
    else:
        zero_interaction_periods = 0

    mouse_clicks = 0
    key_presses = 0


# GUI
class MonitoringApp:

    def __init__(self, master):

        self.schedule_thread = None
        self.monitoring_thread = None
        self.mouse_listener = None
        self.keyboard_listener = None

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.info(str(timestamp) + ": " + "Starting App.")
        self.master = master
        master.title("Global Hola: Productivity Tracking App")


        # Set window size and make it non-resizable
        master.geometry("550x550")
        master.resizable(False, False)

        # Styling
        title_font = font.Font(family="Helvetica", size=14, weight="bold")
        label_font = font.Font(family="Helvetica", size=12)

        # Title
        self.title_label = Label(master, text="Productivity Tracking App", font=title_font, anchor='w', justify='left')
        self.title_label.pack(fill='x', padx=10, pady=15)


        # Email Entry
        self.label = Label(master, text="Please Enter Your Work Email:", font=label_font, anchor='w', justify='left')
        self.label.pack(fill='x', padx=10, pady=5)
        self.email_entry = Entry(master)
        self.email_entry.pack(fill='x', padx=10, pady=5)

        # Webhook Entry
        self.label = Label(master, text="Please Enter Your Employer's Webhook:", font=label_font, anchor='w', justify='left')
        self.label.pack(fill='x', padx=10, pady=5)
        self.webhook_entry = Entry(master)
        self.webhook_entry.pack(fill='x', padx=10, pady=5)

        # Current Project Entry
        self.project_label = Label(master, text="Current Project:", font=label_font, anchor='w', justify='left')
        self.project_label.pack(fill='x', padx=10, pady=5)
        self.project_entry = Entry(master)
        self.project_entry.pack(fill='x', padx=10, pady=5)

        # Status Message
        self.status_var = StringVar()
        self.status_var.set("Status: Not Tracking")
        self.status_label = Label(master, textvariable=self.status_var, font=label_font, anchor='w', justify='left')
        self.status_label.pack(fill='x', padx=10, pady=15)

        # Time tracking
        self.initial_start_time = None
        self.start_time = None
        self.start_time_text = None
        self.tracked_minutes = 0
        self.time_label = Label(master, text="Time Tracked: 0 minutes", anchor='w', justify='left')
        self.time_label.pack(fill='x', padx=10, pady=10)

        # Load the company logo
        self.company_logo = PhotoImage(file="C:/Users/Nick/Downloads/Transparent Logo (small) (1).png")
        self.logo_label = Label(master, image=self.company_logo, cursor="hand2", anchor='w', justify='left')
        self.logo_label.pack(fill='x', padx=10, pady=10)
        self.logo_label.bind("<Button-1>", self.open_web_link)

        # Link Label
        self.link_label = Label(master,
                                text="This app was developed by Global Hola Outsourcing. " + "Talents to grow your business.",
                                cursor="hand2", wraplength=450, anchor='w',
                                justify='left')  # wraplength wraps the text if it's too long
        self.link_label.pack(fill='x', padx=10, pady=10)
        self.link_label.bind("<Button-1>", self.open_web_link)  # Bind the function to handle link click

        # App Info
        self.data_tracked_info = Label(master,
                                       text="This app records and sends activity like typing, clicks, and your active desktop programs.",
                                       anchor='w', justify='left')
        self.data_tracked_info.pack(fill='x', padx=10, pady=10)

        # Buttons
        self.start_button = Button(master, text="Start Monitoring", command=self.start_monitoring, bg="green", anchor='center', justify='left')
        self.start_button.pack(fill='x', padx=10, pady=8)

        self.stop_button = Button(master, text="Stop Monitoring", command=self.stop_monitoring, bg="red", anchor='center', justify='left')
        self.stop_button.pack(fill='x', padx=10, pady=8)
        self.stop_button.pack_forget()

        # Hide the Stop Monitoring button and Show the Start Monitoring button
        self.is_tracking = False  # New flag to determine if tracking is active
        self.load_config()

        # Initializing a flag to check whether the application is running or not
        self.is_running = True

        # Handle window close event
        master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_config(self):
        if os.path.exists('config.json'):
            with open('config.json', 'r') as config_file:
                config_data = json.load(config_file)
                self.email_entry.insert(0, config_data.get("email", ""))
                self.webhook_entry.insert(0, config_data.get("webhook_url", ""))

    def save_config(self):
        config_data = \
            {
            "email": self.email_entry.get(),
            "webhook_url": self.webhook_entry.get()
            }
        with open('config.json', 'w') as config_file:
            json.dump(config_data, config_file)

    def trigger_random_time(self):

        global start_timestamp
        start_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        random_seconds = random.randint(60, 900)  # Randomly choose a number of seconds between 1 and 15 minutes
        threading.Thread(target=self.sleep_and_execute, args=(random_seconds,)).start()

    def sleep_and_execute(self, sleep_duration):

        time.sleep(sleep_duration)
        self.job()

    def open_web_link(self, event):
        webbrowser.open_new_tab("https://globalhola.com?utm_source=activity_tracker_app")

    def start_monitoring(self):

        if self.is_tracking:
            # Already tracking, return immediately without scheduling another job
            return

        self.initial_start_time = datetime.datetime.now()
        self.email = self.email_entry.get()
        self.webhook_url = self.webhook_entry.get()

        valid_url = is_valid_url(self.webhook_url)
        valid_email = is_valid_email(self.email)

        if(self.email == "" or self.webhook_entry == ""):
            self.status_var.set("Error: Must enter email & employer webhook.")
        elif(valid_url == False):
            self.status_var.set("Error: Not a valid webhook.")
        elif (valid_email == False):
            self.status_var.set("Error: Not a valid email.")
        else:

            self.is_tracking = True
            self.update_time_tracked()

            self.mouse_listener = mouse.Listener(on_click=on_click)
            self.keyboard_listener = keyboard.Listener(on_press=on_key_press)

            self.mouse_listener.start()
            self.keyboard_listener.start()
            self.status_var.set("Status: Monitoring started.")
            self.monitoring_thread = threading.Thread(target=self.monitoring_loop)
            self.monitoring_thread.start()

            # Hide the Start Monitoring button and Show the Stop Monitoring button
            self.start_button.pack_forget()
            self.stop_button.pack(fill='x', padx=10, pady=8)
            self.save_config()
            # Start the schedule loop in a separate thread
            self.schedule_thread = threading.Thread(target=self.run_schedule)
            self.schedule_thread.start()

    def monitoring_loop(self):
        while self.is_tracking:
            for i in range(600):  # 600 seconds is 10 minutes
                if not self.is_tracking:
                    break
                time.sleep(1)
            if self.is_tracking:
                self.job()

    def run_schedule(self):
        while self.is_tracking and self.is_running:
            schedule.run_pending()
            time.sleep(1)

    def stop_monitoring(self):
        if self.is_tracking:
            self.mouse_listener.stop()
            self.keyboard_listener.stop()
            self.job()

            self.status_var.set("Status: Monitoring stopped.")
            if hasattr(self, 'time_update_job'):
                self.master.after_cancel(self.time_update_job)  # Stop updating time tracked
            self.is_tracking = False
            # Hide the Stop Monitoring button and Show the Start Monitoring button
            self.stop_button.pack_forget()
            self.start_button.pack(fill='x', padx=10, pady=8)
            update_mouse_and_keystrokes()
        else:
            pass
            # Not Tracking

    def job(self):

        global time_start

        if time_start is None:
            time_start = datetime.datetime.now()

        current_project = self.project_entry.get()
        data = save_to_json(self.email, mouse_clicks, key_presses, current_project, time_start)

        # Update time_start to the current time for the next job
        time_start = datetime.datetime.now()

        # Create a new thread to send data to the webhook
        threading.Thread(target=send_to_webhook, args=(data, self.webhook_url)).start()

        update_mouse_and_keystrokes()

    def on_closing(self):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        logging.info(str(timestamp) + ": " + "Closing app.")
        self.save_config()

        # Stop listeners and any other cleanup you need
        # Setting the flag to False to stop the schedule thread
        self.is_running = False

        if self.is_tracking:
            self.stop_monitoring()

        # If any threads are active, we stop them here
        if hasattr(self, 'monitoring_thread') and self.monitoring_thread != None:
            self.is_tracking = False
            self.monitoring_thread.join()  # Wait for the monitoring_thread to finish

        if hasattr(self, 'schedule_thread') and self.schedule_thread != None:
            self.is_running = False
            self.schedule_thread.join()  # Wait for the schedule_thread to finish

        self.master.destroy()

    def update_time_tracked(self):
        if self.is_tracking:
            elapsed_time = datetime.datetime.now() - self.initial_start_time
            self.tracked_minutes = int(elapsed_time.total_seconds() / 60)
            self.time_label.config(text=f"Time Tracked: {self.tracked_minutes} minutes")
            self.time_update_job = self.master.after(60000, self.update_time_tracked)  # Update every minute

def update_mouse_and_keystrokes():

    global mouse_clicks, key_presses
    mouse_clicks = 0
    key_presses = 0

logging.basicConfig(filename='activity_tracker.log', level=logging.INFO)
timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
logging.info(str(timestamp) + ": " + "Starting Program...")
root = Tk()
root.iconbitmap("C:/Users/Nick/Downloads/Global Hola Site Icon.ico") # Change this for your company icon
app = MonitoringApp(root)
root.mainloop()
exit()
