import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

st.set_page_config(page_title="Email Service", page_icon="📧", layout="wide")

# Initialize session state
if 'email_sent' not in st.session_state:
    st.session_state.email_sent = False

st.title("📧 Email Service")
st.markdown("---")

# Sidebar for SMTP configuration
with st.sidebar:
    st.header("⚙️ SMTP Configuration")

    smtp_provider = st.selectbox(
        "Email Provider",
        ["Gmail", "Outlook", "Yahoo", "Custom"]
    )

    # Pre-fill SMTP settings based on provider
    smtp_defaults = {
        "Gmail": ("smtp.gmail.com", 587),
        "Outlook": ("smtp-mail.outlook.com", 587),
        "Yahoo": ("smtp.mail.yahoo.com", 587),
        "Custom": ("", 587)
    }

    default_host, default_port = smtp_defaults[smtp_provider]

    smtp_host = st.text_input("SMTP Server", value=default_host)
    smtp_port = st.number_input("SMTP Port", value=default_port, min_value=1, max_value=65535)
    sender_email = st.text_input("Your Email Address")
    sender_password = st.text_input("Password/App Password", type="password")

    st.info("💡 **Tip:** For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833)")

# Main email form
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("✉️ Compose Email")

    recipient_email = st.text_input("To (Recipient Email)", placeholder="recipient@example.com")
    cc_email = st.text_input("CC (Optional)", placeholder="cc@example.com")
    bcc_email = st.text_input("BCC (Optional)", placeholder="bcc@example.com")
    subject = st.text_input("Subject", placeholder="Enter email subject")

    email_body = st.text_area("Message Body", height=300, placeholder="Type your message here...")

    # File attachment
    uploaded_files = st.file_uploader("Attach Files (Optional)", accept_multiple_files=True)

    if uploaded_files:
        st.write(f"📎 {len(uploaded_files)} file(s) attached:")
        for file in uploaded_files:
            st.write(f"- {file.name} ({file.size / 1024:.2f} KB)")

with col2:
    st.subheader("📝 Email Preview")
    st.markdown(f"**From:** {sender_email if sender_email else '_Not set_'}")
    st.markdown(f"**To:** {recipient_email if recipient_email else '_Not set_'}")
    if cc_email:
        st.markdown(f"**CC:** {cc_email}")
    if bcc_email:
        st.markdown(f"**BCC:** {bcc_email}")
    st.markdown(f"**Subject:** {subject if subject else '_No subject_'}")
    st.markdown("---")
    st.markdown("**Message:**")
    st.text_area("", value=email_body if email_body else "Empty message", height=200, disabled=True,
                 label_visibility="collapsed")

st.markdown("---")

# Send button
col1, col2, col3 = st.columns([1, 1, 3])

with col1:
    send_button = st.button("📤 Send Email", type="primary", use_container_width=True)

with col2:
    if st.button("🗑️ Clear Form", use_container_width=True):
        st.rerun()

# Email sending logic
if send_button:
    # Validation
    if not all([smtp_host, sender_email, sender_password, recipient_email, subject]):
        st.error(
            "⚠️ Please fill in all required fields (SMTP settings, sender email, password, recipient, and subject)")
    else:
        try:
            with st.spinner("Sending email..."):
                # Create message
                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = recipient_email
                msg['Subject'] = subject

                if cc_email:
                    msg['Cc'] = cc_email
                if bcc_email:
                    msg['Bcc'] = bcc_email

                # Attach body
                msg.attach(MIMEText(email_body, 'plain'))

                # Attach files
                if uploaded_files:
                    for uploaded_file in uploaded_files:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(uploaded_file.read())
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', f'attachment; filename={uploaded_file.name}')
                        msg.attach(part)

                # Prepare recipient list
                recipients = [recipient_email]
                if cc_email:
                    recipients.extend([e.strip() for e in cc_email.split(',')])
                if bcc_email:
                    recipients.extend([e.strip() for e in bcc_email.split(',')])

                # Send email
                server = smtplib.SMTP(smtp_host, smtp_port)
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
                server.quit()

                st.success("✅ Email sent successfully!")
                st.balloons()
                st.session_state.email_sent = True

        except smtplib.SMTPAuthenticationError:
            st.error("❌ Authentication failed. Please check your email and password/app password.")
        except smtplib.SMTPException as e:
            st.error(f"❌ SMTP error occurred: {str(e)}")
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")

# Footer
st.markdown("---")
st.markdown("*Secure email sending powered by Python SMTPLIB*")