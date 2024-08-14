# YouTube_First_Comment_Bot : FirstInLine

## SMTP Server Setup

To enable email notifications, configure your SMTP server by following these steps:

1. **Choose an SMTP Service**:
    - Example: Gmail, SendGrid, etc.

2. **Set Environment Variables**:
    - Set up the following environment variables in your system:
        ```bash
        export SMTP_SERVER='smtp.gmail.com'
        export SMTP_PORT=587
        export SMTP_USERNAME='your_email@gmail.com'
        export SMTP_PASSWORD='your_app_password'
        export SENDER_EMAIL='your_email@gmail.com'
        export RECIPIENT_EMAIL='recipient_email@example.com'
        ```

3. **Configure Flask**:
    - Ensure your Flask app is running with HTTPS if deploying publicly:
        ```bash
        python server.py
        ```

4. **Test the Setup**:
    - Run the server and trigger an email notification to verify the SMTP setup.
