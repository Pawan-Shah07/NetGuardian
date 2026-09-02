
import tkinter as tk
from tkinter import messagebox
import sqlite3
import subprocess 
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
import math
import requests
import os
import re
import nmap 
from tkinter import filedialog
import ipaddress
import socket
import concurrent.futures
import platform
from PIL import Image
from io import BytesIO
from tkinter import ttk

#function for login user
def login():
    username = username_entry.get()
    password = password_entry.get()

    if not username or not password:
        messagebox.showerror("Error", "Please enter both username and password.")
        return

    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()

    if user:
        messagebox.showinfo("Success", "Login successful!")
        # Clear the username and password entries
        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)
        open_main_window(username)
    else:
        messagebox.showerror("Error", "Invalid username or password.")

#for login
def toggle_view_password_login():
    # Toggle between password visibility and hidden
    current_state = password_entry["show"]
    if current_state:
        password_entry["show"] = ""
    else:
        password_entry["show"] = "*"

# for register
def toggle_view_password(entry_widget):
    # Toggle between password visibility and hidden for the given entry widget
    current_state = entry_widget["show"]
    if current_state:
        entry_widget["show"] = ""
    else:
        entry_widget["show"] = "*"

#funtion for signup button
def open_register_window():
    register_window = tk.Toplevel(root)
    register_window.title("Register")
    register_window.geometry("300x200")

    tk.Label(register_window, text="Username:").pack()
    new_username_entry = tk.Entry(register_window)
    new_username_entry.pack()

    tk.Label(register_window, text="Password:").pack()
    new_password_entry = tk.Entry(register_window, show="*")
    new_password_entry.pack()

    view_password_checkbox = tk.Checkbutton(register_window, text="View Password", command=lambda: toggle_view_password(new_password_entry))
    view_password_checkbox.pack()

    def submit_registration():
        new_username = new_username_entry.get()
        new_password = new_password_entry.get()

        if not new_username or not new_password:
            messagebox.showerror("Error", "Please enter both username and password.")
            return
            
        # Password policy requirements
        if not (re.search(r"[A-Z]", new_password) and  # At least one uppercase letter
                re.search(r"[a-z]", new_password) and  # At least one lowercase letter
                re.search(r"\d", new_password) and     # At least one digit
                re.search(r"[!@#$%^&*]", new_password) and  # At least one special character
                len(new_password) >= 8):              # Minimum length of 8 characters
            messagebox.showerror("Error", "Password must be at least 8 characters long and contain at least one uppercase letter, one lowercase letter, one digit, and one special character.")
            return

        try:
            cursor.execute('INSERT INTO users VALUES (?, ?)', (new_username, new_password))
            conn.commit()
            messagebox.showinfo("Success", "Registration successful!")
            register_window.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists. Please choose a different username.")

    submit_button = tk.Button(register_window, text="Submit", command=submit_registration)
    submit_button.pack(pady=10)


#validate network adress function
def validate_network_address(network_address_entry):
    network_address = network_address_entry.get().strip()
    if not network_address:
        messagebox.showerror("Error", "Network address cannot be empty.")
        return False
    elif not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d{1,2}$", network_address):
        messagebox.showerror("Error", "Invalid network address format. Example: 192.168.1.0/24")
        return False
    return True
    
   
# Function to enable the output box temporarily for writing
def enable_output_box(output_box):
    output_box.configure(state='normal')
    
# Function to disable the output box after writing
def disable_output_box(output_box):
    output_box.configure(state='disabled')

#Dashboard
def open_main_window(username):
    main_window = tk.Toplevel(root)
    main_window.title(f"NetGuardian")
    main_window.geometry("700x500")

    # Create and place labels
    welcome_label = tk.Label(main_window, text="The Guardian of your Network")
    login_user = tk.Label(main_window, text= f"Hi, {username}")
    welcome_label.pack(pady=20)  # Add vertical gap (20 pixels) below the label
    login_user.place(x=10, y=12) 

    # Left column buttons
    button_width = 18  # Set the width of all buttons

    # Network Address Label and Entry
    network_address_label = tk.Label(main_window, text="Network Address:")
    network_address_label.place(relx=0.34, rely=0.15, anchor='center')  # Place at the center

    network_address_entry = tk.Entry(main_window, width=35)
    network_address_entry.place(relx=0.64, rely=0.15, anchor='center')  

    # Output Box
    output_box = tk.Text(main_window, width=60, height=20, wrap=tk.WORD)
    output_box.place(relx=0.6, rely=0.55, anchor='center')
    output_box.configure(state='disabled')  # Set the state to disabled

    # buttons
    host_discovery_button = tk.Button(main_window, text="Host Discovery", command=lambda: host_discovery_wrapper(network_address_entry, output_box), width=button_width)
    host_discovery_button.place(relx=0.12, rely=0.25, anchor='center') 

    port_scanning_button = tk.Button(main_window, text="Port Scanning", command=lambda: port_scanning_wrapper(network_address_entry, output_box), width=button_width)
    port_scanning_button.place(relx=0.12, rely=0.33, anchor='center') 

    find_vulnerability_button = tk.Button(main_window, text="Find Vulnerability", command=lambda: find_vulnerability_wrapper(network_address_entry, output_box), width=button_width)
    find_vulnerability_button.place(relx=0.12, rely=0.41, anchor='center')

    credential_testing_button = tk.Button(main_window, text="Credential Testing", command=lambda: credential_wrapper(network_address_entry,username), width=button_width)
    credential_testing_button.place(relx=0.12, rely=0.49, anchor='center')

    report_button = tk.Button(main_window, text="Report", command=report_history, width=button_width)
    report_button.place(relx=0.12, rely=0.57, anchor='center') 

    # Log Out button
    logout_button = tk.Button(main_window, text="Log Out", command=main_window.destroy, width=button_width)
    logout_button.place(relx=0.12, rely=0.94, anchor='center')  

    # Report button
    generate_report_button = tk.Button(main_window, text="Generate report", command=lambda: generate_report(network_address_entry, output_box, username), width=18)
    generate_report_button.place(relx=0.82, rely=0.94, anchor='center')  

    main_window.mainloop()

# Function to draw the company logo on the PDF canvas
def draw_company_logo(pdf_canvas, left_margin, top_margin):
    try:
        # Load the company logo image
        logo_path = "../images/logo.png"
        logo_image = Image.open(logo_path)

        # Resize the logo if needed
        max_logo_width = 80
        max_logo_height = 40  
        logo_image.thumbnail((max_logo_width, max_logo_height))

        # Calculate the position to center the logo in the left section of the header
        logo_left = left_margin-40
        logo_top = top_margin

        # Draw the logo on the PDF canvas
        pdf_canvas.drawInlineImage(logo_image, logo_left, logo_top, width=logo_image.width, height=logo_image.height)
    except Exception as e:
        print(f"Error loading logo: {e}")


def host_discovery(network_address_entry, output_box):
    # Get the network address from the entry widget
    network_address = network_address_entry.get()    
    enable_output_box(output_box)
    # Clear the output box before displaying new results
    output_box.delete(1.0, tk.END)
    # Perform host discovery using Nmap
    output_box.insert(tk.END, f"                          HOST DISCOVERY \n\n")
    output_box.insert(tk.END, f"Performing host discovery on network {network_address} ...\n\n")

    try:
        # Run the Nmap command
        nmap_command = f"sudo nmap -sT {network_address} -O | awk '/Nmap scan report for/ {{print \"Active host is\", $NF}} /MAC Address|OS details|Device type/ {{print}}'"
        result = subprocess.run(nmap_command, shell=True, capture_output=True, text=True)

        # Check if the command was successful
        if result.returncode == 0:
            # Display the Nmap output in the output box
            output_box.insert(tk.END, result.stdout)
            
        else:
            # Display any errors in the output box
            output_box.insert(tk.END, f"Error: {result.stderr}")
    except Exception as e:
        output_box.insert(tk.END, f"Error: {e}\n")

    output_box.insert(tk.END, "\nHost discovery completed.")


def host_discovery_wrapper(network_address_entry, output_box):
        if validate_network_address(network_address_entry):
            host_discovery(network_address_entry, output_box)
            #enable_output_box(output_box)
            disable_output_box(output_box)


#port scanning function
def port_scanning(network_address_entry, output_box):
    network_address = network_address_entry.get()    
    enable_output_box(output_box)
    output_box.delete(1.0, tk.END)
    output_box.insert(tk.END, f"                          PORT SCANNING \n\n")
    output_box.insert(tk.END, f"Performing port scanning on network {network_address} ...\n\n")

    try:
        # Run the Nmap command for host discovery
        nmap_command = f"nmap -sn {network_address}"
        result = subprocess.run(nmap_command, shell=True, capture_output=True, text=True)

        # Check if the command was successful
        if result.returncode == 0:
            # Extract the up hosts from the Nmap output using a regular expression
            up_hosts = re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", result.stdout)

            # Iterate over up hosts and perform port scanning, service, and service version detection
            for host in up_hosts:
                output_box.insert(tk.END, f"\n\nScanning ports for {host} ...\n")
                try:
                    # Run the Nmap command for port scanning, service, and service version detection
                    port_scan_command = f"nmap -sV {host}"
                    port_scan_result = subprocess.run(port_scan_command, shell=True, capture_output=True, text=True)

                    # Check if the command was successful
                    if port_scan_result.returncode == 0:
                        # Display the Nmap output in the output box
                        output_box.insert(tk.END, f"Results for {host}:\n")
                        output_box.insert(tk.END, port_scan_result.stdout)
                    else:
                        # Display any errors in the output box
                        output_box.insert(tk.END, f"Error: {port_scan_result.stderr}")
                except Exception as e:
                    output_box.insert(tk.END, f"Error: {e}\n")
        else:
            # Display any errors in the output box
            output_box.insert(tk.END, f"Error: {result.stderr}")
    except Exception as e:
        output_box.insert(tk.END, f"Error: {e}\n")

    output_box.insert(tk.END, "\nPort scanning completed.")


def port_scanning_wrapper(network_address_entry, output_box):
        if validate_network_address(network_address_entry):
            port_scanning(network_address_entry, output_box)
            disable_output_box(output_box)
                        

def extract_service_and_version(output):
    service_version_dict = {}
    lines = output.split('\n')
    for line in lines:
        if 'open' in line:  # assuming 'open' indicates a port is open
            parts = line.split()
            port = parts[0].replace("/tcp", "")  # Remove "\tcp" from the port
            service = parts[2]
            version = ' '.join(parts[3:]) if len(parts) > 3 else "Unknown"
            service_version_dict[port] = {'service': service, 'version': version}
    return service_version_dict
    
    

def extract_vuln_info(data, output_box):
    # Check if 'vulnerabilities' exists in the data
    if 'vulnerabilities' in data:
        cve_items = data['vulnerabilities']
        if not cve_items:
            output_box.insert(tk.END, f"\n")
            output_box.insert(tk.END, f"No Vulnerability found!!\n\n")
        else:
            for item in cve_items:
                cve_id = item['cve']['id']
                source = item['cve']['sourceIdentifier']
                published = item['cve']['published']
                last_modified = item['cve']['lastModified']
                vulnStatus = item['cve']['vulnStatus']

                # Extract descriptions
                descriptions = [desc['value'] for desc in item['cve']['descriptions']]
                base_severity = [severity['baseSeverity'] for severity in item['cve']['metrics']['cvssMetricV2']]
                # Extract base scores
                base_scores = []
                for metric in item['cve']['metrics']['cvssMetricV2']:
                    if 'cvssData' in metric:
                        base_scores.append(metric['cvssData']['baseScore'])
                    else:
                        base_scores.append(None)  # If 'cvssData' is not present, append None

                # Print each description and corresponding base scores
                for description, base_score, severity in zip(descriptions, base_scores, base_severity):
                    output_box.insert(tk.END, f"CVE ID : {cve_id}\n")
                    output_box.insert(tk.END, f"Source Identifier : {source}\n")
                    output_box.insert(tk.END, f"Published Date : {published}\n")
                    output_box.insert(tk.END, f"Last Modified Date : {last_modified}\n")
                    output_box.insert(tk.END, f"Vulnerability Status : {vulnStatus}\n")
                    output_box.insert(tk.END, f"Vulnerability Description : {description}\n")
                    output_box.insert(tk.END, f"Score : {base_score}\n")
                    output_box.insert(tk.END, f"Severity: {severity}\n\n")
    else:
        output_box.insert(tk.END, f"No vulnerabilities information found")



def check_vulnerabilities(keyword, output_box):
    base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    params = {"keywordSearch": keyword}

    try:
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            #output_box.insert(tk.END,f"{data}\n\n")
            extract_vuln_info(data,output_box)
            output_box.insert(tk.END, f"For more information: https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch={keyword}\n\n\n")
        else:
            output_box.insert(tk.END, f"Error accessing NVD API: {response.status_code}\n")
            return False
    except requests.RequestException as e:
        output_box.insert(tk.END, f"An error occurred during the request: {e}\n")
        return False


def find_vulnerability(network_address_entry, output_box):
    network_address = network_address_entry.get()
    enable_output_box(output_box)
    # Clear the output box before displaying new results
    output_box.delete(1.0, tk.END)
    output_box.insert(tk.END, "                         Vulnerability Scanning \n\n")
    output_box.insert(tk.END, f"Performing scanning on network {network_address} ...\n\n")

    try:
        # Run the Nmap command for host discovery
        nmap_command = f"nmap -sn {network_address}"
        result = subprocess.run(nmap_command, shell=True, capture_output=True, text=True, check=False)

        # Check if the command was successful
        if result.returncode == 0:
            # Extract the up hosts from the Nmap output using a regular expression
            up_hosts = re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", result.stdout)

            # Iterate over up hosts and perform port scanning, service, and service version detection
            for host in up_hosts:
                output_box.insert(tk.END, f"\n\nScanning ports for {host} ...\n\n")
                try:
                    # Run the Nmap command for port scanning, service, and service version detection
                    scanner = nmap.PortScanner()
                    scanner.scan(host, arguments='-p 1-1000 -sV')  # Scan ports 1 to 1000
                    result = ""  # Initialize result for each host
                    for host in scanner.all_hosts():
                        for proto in scanner[host].all_protocols():
                            for port in scanner[host][proto]:
                                port_info = scanner[host][proto][port]
                                result += f"{port}/{proto} {port_info['state']}  {port_info['name']}  {port_info['product']} {port_info['version']}\n\n"
                                
                    service_version_info = extract_service_and_version(result)
                    for port, info in service_version_info.items():
                        output_box.insert(tk.END, f"Port: {port}, Service: {info['service']}, Version: {info['version']}\n")
                        # Check for vulnerabilities
                        if info['version'] == 'Unknown':
                            check_vulnerabilities(info['service'], output_box)
                        else:
                            check_vulnerabilities(info['version'], output_box)
                     
                except Exception as e:
                    output_box.insert(tk.END, f"Error: {e}\n")
        else:
            # Display any errors in the output box
            output_box.insert(tk.END, f"Error: {result.stderr}")
    except Exception as e:
        output_box.insert(tk.END, f"Error: {e}\n")
    output_box.insert(tk.END, "\nScanning completed.")
    

def find_vulnerability_wrapper(network_address_entry, output_box):
        if validate_network_address(network_address_entry):
            find_vulnerability(network_address_entry, output_box)
            disable_output_box(output_box)


def scan_network(network_address_entry,username):
    nm = nmap.PortScanner()
    network_address = network_address_entry.get()
    nm.scan(hosts=network_address, arguments='-sn')
    active_hosts = nm.all_hosts()

    #ip_dropdown['values'] = active_hosts
    open_credential_window(network_address_entry, active_hosts, username)

def scan_ports(ip_dropdown,port_dropdown,service_text):
    selected_ip = ip_dropdown.get()
    nm = nmap.PortScanner()
    nm.scan(hosts=selected_ip, arguments='-p 1-1000')

    open_ports = []
    for host in nm.all_hosts():
        for proto in nm[host].all_protocols():
            ports = nm[host][proto].keys()
            open_ports.extend(ports)

    port_dropdown['values'] = sorted(open_ports)

    service_text.delete(1.0, tk.END)  # Clear previous text

def show_services(ip_dropdown,port_dropdown, service_text):
    selected_ip = ip_dropdown.get()
    selected_port = port_dropdown.get()

    nm = nmap.PortScanner()
    nm.scan(hosts=selected_ip, arguments='-sV -p ' + selected_port)

    service_info = nm[selected_ip]['tcp'][int(selected_port)]
    service_name = service_info['name']
    service_text.delete(1.0, tk.END)  # Clear previous text
    service_text.insert(tk.END, service_name)


def brute_force_attack(ip_dropdown, port_dropdown, output_box, service_text):
    selected_ip = ip_dropdown.get()
    selected_port = port_dropdown.get()
    enable_output_box(output_box)
    # Clear the output box before displaying new results
    output_box.delete(1.0, tk.END)
    # Retrieve the text from the service_text widget
    selected_service = service_text.get("1.0", "end-1c")  # Get all text excluding the trailing newline character

    usernames_list = "../credential/usernames.txt"  # Replace with the actual username
    password_list = "../credential/passwords.txt"  # Replace with the path to your password list

    # Execute hydra command for SSH brute force attack
    command = f"hydra -L {usernames_list} -P {password_list} {selected_ip} -s {selected_port} {selected_service}"
    output_box.insert(tk.END, f"Performing brute force attack on {selected_ip} and the port is {selected_port}...\n\n")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            output_box.insert(tk.END, "Brute force attack successful.\n\n")

            # Extract and display usernames and passwords
            matches = re.findall(r"login:\s+(\S+)\s+password:\s+(\S+)", result.stdout)
            if matches:
                output_box.insert(tk.END, "Found credentials:\n")
                for match in matches:
                    brute_username, password = match
                    output_box.insert(tk.END, f"Username: {brute_username}, Password: {password}\n")
            else:
                output_box.insert(tk.END, "No credentials found.\n")
        else:
            output_box.insert(tk.END, f"Error: {result.stderr}\n")
    except Exception as e:
        output_box.insert(tk.END, f"Error: {e}\n")

    output_box.insert(tk.END, "Brute force attack completed.\n")
    disable_output_box(output_box)

def open_credential_window(network_address_entry, active_hosts, username):
    credential_window = tk.Toplevel(root)
    credential_window.title("Credential Testing")
    credential_window.geometry("400x400")
    
    #set for ip dropdown and lable
    ip_dropdown = ttk.Combobox(credential_window, width = 13, state="readonly")
    #ip_dropdown.set(active_hosts[0])  # Set default active host
    ip_dropdown.place(relx=0.27, rely=0.1)
    ip_label = tk.Label(credential_window, text="Active Hosts:")
    ip_label.place(relx=0.02, rely=0.10)
    ip_dropdown.bind("<<ComboboxSelected>>", lambda event: scan_ports(ip_dropdown, port_dropdown, service_text))
    ip_dropdown['values'] = active_hosts


    #setting for port dropdown and label
    port_dropdown = ttk.Combobox(credential_window, width = 9, state="readonly")  # Set the state to readonly
    port_dropdown.set('')  # Initially empty until host selected
    port_dropdown.place(relx=0.7, rely=0.1)
    port_label = tk.Label(credential_window, text="Port:")
    port_label.place(relx=0.6, rely=0.1)
    port_dropdown.bind("<<ComboboxSelected>>", lambda event: show_services(ip_dropdown,port_dropdown, service_text))


    #setting for service lable
    service_label = tk.Label(credential_window, text="service:")
    service_label.place(relx=0.02, rely=0.2)
    service_text = tk.Text(credential_window,height=1, width=14, state="normal")
    service_text.place(relx=0.27, rely=0.2)
    #service_text.configure(state="disable")
    
    # Output Box
    output_box = tk.Text(credential_window, width=40, height=13, wrap=tk.WORD)
    output_box.place(relx=0.5, rely=0.58, anchor='center')
    output_box.configure(state='disabled')  # Set the state to disabled

    # Bruteforce button
    Brute_force = tk.Button(credential_window, text="Bruteforce", command=lambda: brute_force_attack(ip_dropdown, port_dropdown, output_box,service_text), width=12)
    Brute_force.place(relx=0.77, rely=0.22, anchor='center')

    # Generate report button
    credential_report_button = tk.Button(credential_window, text="Generate report", command=lambda: generate_report(network_address_entry, output_box, username), width=12)
    credential_report_button.place(relx=0.78, rely=0.94, anchor='center')

    # back button
    back_button = tk.Button(credential_window, text="Back", command=credential_window.destroy, width=12)
    back_button.place(relx=0.2, rely=0.94, anchor='center')
     

def credential_wrapper(network_address_entry,username):
        if validate_network_address(network_address_entry):
            scan_network(network_address_entry,username)
            #disable_output_box(output_box)


def generate_report(network_address_entry, output_box, username):
    # Get the current date
    current_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Get the network address and output text
    network_address = network_address_entry.get().replace('/', '-')
    report_text = output_box.get("1.0", tk.END)

    # Check if the output box is empty
    if not report_text.strip():
        messagebox.showerror("Error", "Output box is empty. Please perform actions before generating a report.")
        return
    report_folder = '../reports'

    
    try:
        # List all files in the reports folder
        pdf_files = [f for f in os.listdir(report_folder) if f.endswith(".pdf")]
        # Prompt the user for the file name and location
        file_path = filedialog.asksaveasfilename(
            initialdir=report_folder,
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            title="Save Report As"
        )

        if file_path:
            # Create the PDF document
            pdf_canvas = canvas.Canvas(file_path, pagesize=letter)

            # Set margins
            left_margin = 72
            right_margin = letter[0] - 72
            top_margin = letter[1] - 72
            bottom_margin = 72

            # Add metadata to the PDF
            pdf_canvas.setTitle(f"Report - {network_address}")

            # Add header only on the first pages
            pdf_canvas.setFont("Helvetica-Bold", 14)

            # Draw company logo in the left section of the header
            draw_company_logo(pdf_canvas, left_margin, top_margin)

            # Continue with the rest of the header
            pdf_canvas.drawCentredString((left_margin + right_margin) / 2, top_margin - 20, "Report")
            top_margin -= 40

            pdf_canvas.setFont("Helvetica", 12)

            # Add username, network address, and date only on the first page
            pdf_canvas.drawString(left_margin, top_margin, f"User: {username}")
            top_margin -= 15
            pdf_canvas.drawString(left_margin, top_margin, f"Network Address: {network_address}")
            top_margin -= 15
            pdf_canvas.drawString(left_margin, top_margin, f"Date: {current_date}")
            top_margin -= 20

            # Add page number in the right section of the footer on the first page
            pdf_canvas.drawRightString(right_margin, bottom_margin - 20, "Page 1")

            # Split the report text into lines and add them to the PDF
            lines = report_text.split("\n")

            line_spacing = 1.5  # Adjust this value for the desired line spacing

            page_number = 1
            for line in lines:
                # Check if there's enough space for the current line
                if top_margin - bottom_margin <= 0:
                    pdf_canvas.showPage()  # Start a new page
                    page_number += 1
                    top_margin = letter[1] - 25  # Reset the position for the new page

                    # Add metadata to the PDF for subsequent pages
                    pdf_canvas.setTitle(f"Report - {network_address}")

                    # Add header for the new page
                    pdf_canvas.setFont("Helvetica-Bold", 14)
                    top_margin -= 40

                    pdf_canvas.setFont("Helvetica", 12)

                    # Add page number in the right section of the footer for subsequent pages
                    pdf_canvas.drawRightString(right_margin, bottom_margin - 20, f"Page {page_number}")

                # Calculate the width of the line
                line_width = pdf_canvas.stringWidth(line.strip(), "Helvetica", 12)
                # Check if the line exceeds the right margin
                if left_margin + line_width > right_margin:
                    # Split the line into words
                    words = line.split()
                    wrapped_line = ""
                    for word in words:
                        # Check if adding the word exceeds the right margin
                        if pdf_canvas.stringWidth(wrapped_line + word, "Helvetica", 12) <= right_margin - left_margin:
                            wrapped_line += word + " "
                        else:
                            # Draw the wrapped line
                            pdf_canvas.drawString(left_margin, top_margin, wrapped_line.strip())
                            top_margin -= 12 * line_spacing  # Adjusting line spacing
                            wrapped_line = word + " "
                    # Draw the remaining wrapped line
                    pdf_canvas.drawString(left_margin, top_margin, wrapped_line.strip())
                    top_margin -= 12 * line_spacing  # Adjusting line spacing
                else:
                    pdf_canvas.drawString(left_margin, top_margin, line.strip())
                    top_margin -= 12 * line_spacing  # Adjusting line spacing

            pdf_canvas.save()

            messagebox.showinfo("Report", f"Report generated successfully: {file_path}")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate report: {e}")




def report_history():
    report_folder = r"../reports"
    try:
        # List all files in the reports folder
        pdf_files = [f for f in os.listdir(report_folder) if f.endswith(".pdf")]

        if pdf_files:
            file_path = filedialog.askopenfilename(
                initialdir=report_folder,
                title="Select a PDF file",
                filetypes=[("PDF files", "*.pdf")],
                defaultextension=".pdf"
            )

            if file_path:
                # Determine the platform (Windows or Unix-like)
                if platform.system().lower() == 'windows':
                    # On Windows, use the "start" command
                    subprocess.run(["start", "", file_path], shell=True)
                else:
                    # On Unix-like systems, use the "xdg-open" command
                    subprocess.run(["xdg-open", file_path])
            else:
                messagebox.showinfo("No File Selected", "No PDF file selected.")
        else:
            messagebox.showinfo("No PDF Files", f"No PDF files found in {report_folder}")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to list report files: {e}")


root = tk.Tk()
root.title("Login System")
root.geometry("400x300")
#root.iconbitmap(r"../images/icon.ico")


conn = sqlite3.connect('../database/user_credentials.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL
    )
''')
conn.commit()

tk.Label(root, text="Username:").pack()
username_entry = tk.Entry(root)
username_entry.pack()

tk.Label(root, text="Password:").pack()
password_entry = tk.Entry(root, show="*")
password_entry.pack()

view_password_checkbox = tk.Checkbutton(root, text="View Password", command=toggle_view_password_login)
view_password_checkbox.pack()

# Left column buttons
button_width = 6  # Set the width of all buttons

login_button = tk.Button(root, text="Log In", command=login, font=("Arial", 12), activebackground="#45a049",width=button_width)
login_button.place(relx=0.5, rely=0.45, anchor='center') 

register_button = tk.Button(root, text="Sign Up", command=open_register_window, font=("Arial", 12), activebackground="#45a049", width=button_width)
register_button.place(relx=0.5, rely=0.60, anchor='center') 

root.mainloop()

conn.close()
