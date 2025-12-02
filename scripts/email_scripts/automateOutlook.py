import win32com.client as win32

outlook = win32.Dispatch('outlook.application')
mail = outlook.CreateItem(0)
mail.To = 'info@mydomain.com'
mail.Subject = 'Message subject'
mail.Body = 'Message body'

# To attach a file to the email (optional):
attachment = "D:\MS_TUC\My_files\Thesis\SDN-dataset\Documents\paper_summary.md" # path of the attached doc
mail.Attachments.Add(attachment)

mail.Send()
