def send_password_reset_email(email: str, reset_link: str):
    # temp email service
    with open("emails.log", "a") as f:
        f.write(f"To: {email} | Link: {reset_link}\n")
    print(f"📨 Email sent to {email} with link: {reset_link}")
