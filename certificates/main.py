# import easygui
import pandas as pd
from datetime import datetime
from send_email import sendEmailContent 
from html_content import get_html_content
import easygui
import imaplib
 
from dotenv import load_dotenv
import os


def driver_function(excel_file):
    """Reads email addresses from an Excel file and sends emails. Stores unsent emails in 'failed_emails.xlsx'."""
    failed_records = []
    logfile = open("certificates\processlogs.log", "a"); 
    template_path = "certificates\emailtemp.html"
    logfile.write(f"{datetime.now()} : PROCESS STARTED\n")
    try:
        sheet_names = pd.ExcelFile(excel_file).sheet_names  # get sheet names

        for sheet in sheet_names:
            print(sheet)
        # Attempt to read the Excel file
            all_data = pd.read_excel(excel_file, sheet_name=sheet)

            for _, row in all_data.iterrows():
                try:
                    recieverEmail = row['email']
                    subject = "Developer's Day 2026 - Participation Certificate"

                    # Create a list of team members from the file data
                    htmlContent = get_html_content(template_path, row['name'], row['competition'])
                    attachment = f"certificates/certificate.pdf"
                    # Send email and track failures
                    if not sendEmailContent(row['name'], row['competition'],recieverEmail, subject, htmlContent, attachment):
                        failed_records.append(row.to_dict())
                        logfile.write(f"{datetime.now()} : Couldn't send email to {recieverEmail}\n")
                    else:
                        logfile.write(f"{datetime.now()} : Email sent to {recieverEmail}\n")


                except KeyError as e:
                    print(f"[!] Missing column in the Excel file: {e}")
                    logfile.write(f"{datetime.now()} : [!] Missing column in the Excel file: {e}\n")
                    failed_records.append(row.to_dict())  # Log the record even if it fails
                except Exception as e:
                    print(f"[!] Error processing email for {recieverEmail}: {e}")
                    logfile.write(f"{datetime.now()} : [!] Error processing email for {recieverEmail}: {e}\n")
                    failed_records.append(row.to_dict())
        load_dotenv()
        senderEmail = os.getenv("SENDER_EMAIL")
        senderPassword = os.getenv("SENDER_PASSWORD")
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        imap.login(senderEmail, senderPassword)

        imap.select('"[Gmail]/Sent Mail"')

        result, data = imap.search(None, f'SUBJECT "Day 2026 - Participation Certificate"')




        for num in data[0].split():
            imap.store(num, '+X-GM-LABELS', 'Certificates')
            
        imap.close()
        imap.logout()

    except FileNotFoundError:
        print(" Error: The specified Excel file was not found.")
    except pd.errors.EmptyDataError:
        print(" Error: The Excel file is empty or corrupted.")
    except Exception as e:
        print(f" Unexpected error: {e}")

    finally:
        # Save failed records even if script crashes
        if failed_records:
            pd.DataFrame(failed_records).to_excel(f"failed_emails.xlsx", index=False)
            print("[!] Some emails were not sent. Check 'failed_emails.xlsx' for details.")

# Run the function with user-selected Excel file
# file_name = "./workshops-email/records.xlsx"
file_name = easygui.fileopenbox(title="Select CSV file with participant details", filetypes=["*.csv"])
if file_name:
    driver_function(file_name)
else:
    print(" No file selected.")
