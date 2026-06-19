# import easygui
import pandas as pd
from datetime import datetime
from send_email import sendEmailContent, sendRescheduleEmail, sendPortal
from html_content import get_html_content
from gen_img import generate
import easygui
import imaplib
 
from dotenv import load_dotenv
import os


def driver_function(excel_file):
    """Reads email addresses from an Excel file and sends emails. Stores unsent emails in 'failed_emails.xlsx'."""
    failed_records = []
    logfile = open("processlogs.log", "a"); 
    template_path = easygui.fileopenbox(title="Select HTML Template", filetypes=["*.html"])
    logfile.write(f"{datetime.now()} : PROCESS STARTED\n")
    try:
        
        # Attempt to read the Excel file
        all_data = pd.read_excel(excel_file)

        for _, row in all_data.iterrows(): 
            try:
                recieverEmail = row['leader_email']
                # recieverEmail = row['email']
                members_raw = row.get('members_email', '')
                if pd.isna(members_raw):
                    members = []
                else:
                    members = [email.strip() for email in str(members_raw).split(',') if email.strip()]
                # subject = f"Developers Day 2026 Rescheduled - Team {row['team_name']}"
                # subject = f"Developers Day 2026 Rescheduled"
                # subject = f"UNCLEAR Payment Receipt - Team {row['team_name']}"
                # subject = f"Developers Day 2026 - {row['module_name']} Module Dissolved"
                # subject = f"Developers Day 2026 Hackathon - Team {row['team_name']}"
                # subject = f"Developers Day 2026 - Laptop Requirement Reminder"
                # subject = "Brand Ambassador Code - Developer's Day 2026"
                # subject = f"Developers Day 2026 Event Info - Team {row['team_name']}"
                # subject = f"Developers Day 2026 - Participant Portal"
                # subject = f"Developers Day 2026 - {row['module_name']} Refund Update"
                # subject = f"Developers Day 2026 - Closing Ceremony"
                # subject = f"Developers Day 2026 - {row['module_name']} Prize Money Distribution"
                subject = f"Developers Day 2026 - Update Regarding Winnings"
                

                # Create a list of team members from the file data
                htmlContent = get_html_content(template_path, row.to_dict())

                # Generate image for the participant
                # generate(row["name"], row["position"], row["team"])

                # Send email and track failures
                # if not sendEmailContent(recieverEmail, subject, htmlContent, row["name"]):
                #     failed_records.append(row.to_dict())
                #     logfile.write(f"{datetime.now()} : Couldn't send email to {recieverEmail}\n")
                # else:
                #     logfile.write(f"{datetime.now()} : Email sent to {recieverEmail}\n")
                if not sendRescheduleEmail(recieverEmail, subject, htmlContent, members):
                # if not sendPortal(recieverEmail, subject, htmlContent):
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

        # result, data = imap.search(None, 'SUBJECT "UNCLEAR Payment Receipt - Team"')
        # result, data = imap.search(None, 'SUBJECT "Module Dissolved"')
        # result, data = imap.search(None, 'SUBJECT "Developers Day 2026 Hackathon - Team"')
        # result, data = imap.search(None, 'SUBJECT "Developers Day 2026 - Laptop Requirement Reminder"')
        # result, data = imap.search(None, 'SUBJECT "Developers Day 2026 Event Info - Team"')
        # result, data = imap.search(None, 'SUBJECT "Developers Day 2026 - Participant Portal"')
        # result, data = imap.search(None, 'SUBJECT "Refund Update"')
        # result, data = imap.search(None, 'SUBJECT "Developers Day 2026 - Closing Ceremony"')
        # result, data = imap.search(None, f'SUBJECT "Prize Money Distribution"')
        result, data = imap.search(None, f'SUBJECT "Update Regarding Winnings"')





        for num in data[0].split():
            # imap.store(num, '+X-GM-LABELS', 'UnclearScreenshot')
            # imap.store(num, '+X-GM-LABELS', 'DissolvedCompetitions')
            # imap.store(num, '+X-GM-LABELS', 'WAgroups')
            # imap.store(num, '+X-GM-LABELS', 'Laptops')
            # imap.store(num, '+X-GM-LABELS', 'EventInfo')
            # imap.store(num, '+X-GM-LABELS', 'ParticipantPortal')
            # imap.store(num, '+X-GM-LABELS', 'Refunds')
            # imap.store(num, '+X-GM-LABELS', 'ClosingCeremony')
            imap.store(num, '+X-GM-LABELS', 'PrizeMoney')
            



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
file_name = easygui.fileopenbox(title="Select Excel File", filetypes=["*.xlsx"])
if file_name:
    driver_function(file_name)
else:
    print("No file selected.")
