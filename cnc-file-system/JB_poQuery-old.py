import os
import shutil
import pyodbc

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

# Test function with an example
def main():
    job_data = get_latest_job_data()
    if job_data:
        customer_name = job_data["CustomerName"]
        active_folder, closed_folder = ensure_customer_folder(customer_name)
        print(f"Active folder path: {active_folder}")
        print(f"Closed folder path: {closed_folder}")

if __name__ == "__main__":
    main()
