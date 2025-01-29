import os
import shutil
import pyodbc
import subprocess

# Define the base directory
BASE_DIR = r"G:\\cnc-file-system\\files"

# SQL Server connection details
CONNECTION_STRING = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=SERVER2\\JBSQL;"
    "Database=PRODUCTIONsql;"
    "Trusted_Connection=yes;"
)

def get_latest_job_data():
    """
    Query the SQL Server database to retrieve the most recently updated job data.
    """
    try:
        with pyodbc.connect(CONNECTION_STRING) as conn:
            cursor = conn.cursor()
            query = """
                SELECT 
                    j.Last_Updated, 
                    j.Part_Number, 
                    j.Customer_PO, 
                    j.Status, 
                    j.Last_Updated_By, 
                    c.Name
                FROM 
                    dbo.Job j
                INNER JOIN 
                    dbo.Customer c
                ON 
                    j.Customer = c.Customer
                ORDER BY j.Last_Updated DESC;
            """
            cursor.execute(query)
            row = cursor.fetchone()
            if row:
                return {
                    "Last_Updated": row.Last_Updated,
                    "Part_Number": row.Part_Number,
                    "Customer_PO": row.Customer_PO,
                    "Status": row.Status,
                    "Last_Updated_By": row.Last_Updated_By,
                    "CustomerName": row.Name,
                }
            else:
                print("No job data found.")
                return None
    except pyodbc.Error as e:
        print(f"Error querying the database: {e}")
        return None

def ensure_customer_folder(customer_name):
    """
    Ensures the customer folder and its subfolders ('Active', 'Closed') exist.
    If missing, creates them.
    """
    # Construct the path for the customer folder
    customer_folder = os.path.join(BASE_DIR, customer_name)

    # Check if the customer folder exists
    if not os.path.exists(customer_folder):
        print(f"Creating customer folder: {customer_folder}")
        os.makedirs(customer_folder)

    # Define paths for Active and Closed subfolders
    active_folder = os.path.join(customer_folder, "Active")
    closed_folder = os.path.join(customer_folder, "Closed")

    # Create Active and Closed subfolders if they do not exist
    for folder in [active_folder, closed_folder]:
        if not os.path.exists(folder):
            print(f"Creating subfolder: {folder}")
            os.makedirs(folder)

    return active_folder, closed_folder

def ensure_part_folder(active_folder, closed_folder, part_number):
    """
    Checks if the part folder exists in 'Active' or 'Closed' subfolders. 
    If found in 'Closed', move it to 'Active'. If not found, create it in 'Active'.
    """
    part_folder_in_active = os.path.join(active_folder, part_number)
    part_folder_in_closed = os.path.join(closed_folder, part_number)

    # Check if the part folder exists in Active
    if os.path.exists(part_folder_in_active):
        print(f"Part folder already exists in 'Active': {part_folder_in_active}")
        return

    # Check if the part folder exists in Closed
    if os.path.exists(part_folder_in_closed):
        print(f"Part folder found in 'Closed'. Moving to 'Active': {part_folder_in_closed}")
        shutil.move(part_folder_in_closed, part_folder_in_active)
        return

    # Create the part folder in Active if it doesn't exist
    print(f"Creating part folder in 'Active': {part_folder_in_active}")
    os.makedirs(part_folder_in_active)
    trigger_browser_automation(part_number)  # Trigger browser automation

def trigger_browser_automation(part_number):
    """
    Calls the browser automation script with the part number as an argument.
    """
    try:
        subprocess.run(['python', 'browser_automation.js', part_number], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error triggering browser automation: {e}")

# Test function with an example
def main():
    job_data = get_latest_job_data()
    if job_data:
        customer_name = job_data["CustomerName"]
        part_number = job_data["Part_Number"]
        active_folder, closed_folder = ensure_customer_folder(customer_name)
        ensure_part_folder(active_folder, closed_folder, part_number)

if __name__ == "__main__":
    main()