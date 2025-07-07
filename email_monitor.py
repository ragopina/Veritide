#!/usr/bin/env python3
"""
LinkedIn Email Monitor - Alternative Approach
Monitor LinkedIn notifications via email parsing

This script monitors your email inbox for LinkedIn comment notifications
and extracts relevant information. This is often more reliable than API access.

Requirements:
- imaplib (built-in)
- email (built-in)
- beautifulsoup4: pip install beautifulsoup4
- python-dotenv: pip install python-dotenv

Setup:
1. Enable LinkedIn email notifications for comments
2. Set up app-specific password for email access (Gmail, Outlook, etc.)
3. Configure email credentials in .env file
"""

import imaplib
import email
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import re
import os
from typing import List, Dict, Optional
from dataclasses import dataclass
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import json

load_dotenv()

@dataclass
class LinkedInNotification:
    """Represents a LinkedIn notification from email"""
    subject: str
    sender: str
    date: str
    comment_author: str
    comment_content: str
    post_excerpt: str
    notification_type: str

class EmailMonitor:
    """
    Email-based LinkedIn notification monitor
    
    Monitors email inbox for LinkedIn comment notifications and parses them
    to identify new comments on your posts.
    """
    
    def __init__(self):
        self.email_host = os.getenv('EMAIL_HOST', 'imap.gmail.com')
        self.email_port = int(os.getenv('EMAIL_PORT', '993'))
        self.email_username = os.getenv('EMAIL_USERNAME')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        
        # File to store processed notification IDs
        self.processed_file = 'processed_notifications.json'
        self.processed_notifications = self.load_processed_notifications()
    
    def load_processed_notifications(self) -> List[str]:
        """Load list of previously processed notification IDs"""
        try:
            if os.path.exists(self.processed_file):
                with open(self.processed_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading processed notifications: {e}")
        return []
    
    def save_processed_notifications(self, notification_ids: List[str]):
        """Save list of processed notification IDs"""
        try:
            with open(self.processed_file, 'w') as f:
                json.dump(notification_ids, f, indent=2)
        except Exception as e:
            print(f"Error saving processed notifications: {e}")
    
    def connect_to_email(self) -> Optional[imaplib.IMAP4_SSL]:
        """Connect to email server"""
        if not self.email_username or not self.email_password:
            print("❌ Email credentials not found!")
            print("\nTo use email monitoring, add these to your .env file:")
            print("EMAIL_HOST=imap.gmail.com")
            print("EMAIL_PORT=993")
            print("EMAIL_USERNAME=your_email@gmail.com")
            print("EMAIL_PASSWORD=your_app_password")
            print("\nFor Gmail, use an app password instead of your regular password.")
            return None
        
        try:
            mail = imaplib.IMAP4_SSL(self.email_host, self.email_port)
            mail.login(self.email_username, self.email_password)
            print("✅ Connected to email server successfully!")
            return mail
        except Exception as e:
            print(f"❌ Failed to connect to email: {e}")
            return None
    
    def get_linkedin_emails(self, days: int = 7) -> List[email.message.Message]:
        """Get LinkedIn notification emails from the past N days"""
        mail = self.connect_to_email()
        if not mail:
            return []
        
        try:
            mail.select('INBOX')
            
            # Calculate date for search
            since_date = (datetime.now() - timedelta(days=days)).strftime("%d-%b-%Y")
            
            # Search for LinkedIn emails
            search_criteria = f'(FROM "noreply@linkedin.com" SINCE {since_date})'
            status, message_ids = mail.search(None, search_criteria)
            
            if status != 'OK':
                print("Failed to search emails")
                return []
            
            emails = []
            for msg_id in message_ids[0].split():
                status, msg_data = mail.fetch(msg_id, '(RFC822)')
                if status == 'OK':
                    raw_email = msg_data[0][1]
                    email_message = email.message_from_bytes(raw_email)
                    emails.append(email_message)
            
            mail.close()
            mail.logout()
            return emails
            
        except Exception as e:
            print(f"Error fetching emails: {e}")
            return []
    
    def parse_linkedin_notification(self, email_msg: email.message.Message) -> Optional[LinkedInNotification]:
        """Parse a LinkedIn notification email"""
        try:
            subject = email_msg['Subject'] or ''
            sender = email_msg['From'] or ''
            date = email_msg['Date'] or ''
            
            # Get email content
            body = self.get_email_body(email_msg)
            if not body:
                return None
            
            # Parse different types of LinkedIn notifications
            if 'commented on your post' in subject or 'commented on your' in body:
                return self.parse_comment_notification(subject, sender, date, body)
            elif 'liked your post' in subject:
                return self.parse_like_notification(subject, sender, date, body)
            elif 'shared your post' in subject:
                return self.parse_share_notification(subject, sender, date, body)
            
            return None
            
        except Exception as e:
            print(f"Error parsing notification: {e}")
            return None
    
    def get_email_body(self, email_msg: email.message.Message) -> str:
        """Extract text content from email"""
        try:
            if email_msg.is_multipart():
                for part in email_msg.walk():
                    if part.get_content_type() == "text/html":
                        return part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    elif part.get_content_type() == "text/plain":
                        return part.get_payload(decode=True).decode('utf-8', errors='ignore')
            else:
                return email_msg.get_payload(decode=True).decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"Error extracting email body: {e}")
        return ""
    
    def parse_comment_notification(self, subject: str, sender: str, date: str, body: str) -> Optional[LinkedInNotification]:
        """Parse a comment notification email"""
        try:
            # Use BeautifulSoup to parse HTML content
            soup = BeautifulSoup(body, 'html.parser')
            
            # Extract comment author (usually in subject)
            author_match = re.search(r'(.+?) commented on', subject)
            comment_author = author_match.group(1) if author_match else "Unknown"
            
            # Try to extract comment content from email body
            comment_content = "Comment content not available"
            
            # Look for comment text in various possible HTML structures
            comment_elements = soup.find_all(['p', 'div', 'span'], string=re.compile(r'.{10,}'))
            for element in comment_elements:
                text = element.get_text().strip()
                if len(text) > 20 and 'unsubscribe' not in text.lower() and 'linkedin' not in text.lower():
                    comment_content = text[:200] + "..." if len(text) > 200 else text
                    break
            
            # Extract post excerpt
            post_excerpt = "Post excerpt not available"
            if 'your post' in subject:
                post_match = re.search(r'your post[:\s]*"?([^"]+)"?', body, re.IGNORECASE)
                if post_match:
                    post_excerpt = post_match.group(1)[:100] + "..."
            
            return LinkedInNotification(
                subject=subject,
                sender=sender,
                date=date,
                comment_author=comment_author,
                comment_content=comment_content,
                post_excerpt=post_excerpt,
                notification_type="comment"
            )
            
        except Exception as e:
            print(f"Error parsing comment notification: {e}")
            return None
    
    def parse_like_notification(self, subject: str, sender: str, date: str, body: str) -> Optional[LinkedInNotification]:
        """Parse a like notification email"""
        try:
            author_match = re.search(r'(.+?) (liked|reacted to)', subject)
            author = author_match.group(1) if author_match else "Unknown"
            
            return LinkedInNotification(
                subject=subject,
                sender=sender,
                date=date,
                comment_author=author,
                comment_content="Liked your post",
                post_excerpt="Post excerpt not available",
                notification_type="like"
            )
        except Exception as e:
            print(f"Error parsing like notification: {e}")
            return None
    
    def parse_share_notification(self, subject: str, sender: str, date: str, body: str) -> Optional[LinkedInNotification]:
        """Parse a share notification email"""
        try:
            author_match = re.search(r'(.+?) shared', subject)
            author = author_match.group(1) if author_match else "Unknown"
            
            return LinkedInNotification(
                subject=subject,
                sender=sender,
                date=date,
                comment_author=author,
                comment_content="Shared your post",
                post_excerpt="Post excerpt not available",
                notification_type="share"
            )
        except Exception as e:
            print(f"Error parsing share notification: {e}")
            return None
    
    def get_new_notifications(self, days: int = 7) -> List[LinkedInNotification]:
        """Get new LinkedIn notifications from email"""
        print(f"📥 Fetching LinkedIn emails from the past {days} days...")
        
        emails = self.get_linkedin_emails(days)
        new_notifications = []
        
        for email_msg in emails:
            # Create a unique ID for this email
            email_id = f"{email_msg['Message-ID']}_{email_msg['Date']}"
            
            # Skip if already processed
            if email_id in self.processed_notifications:
                continue
            
            notification = self.parse_linkedin_notification(email_msg)
            if notification:
                new_notifications.append(notification)
                self.processed_notifications.append(email_id)
        
        # Save updated processed list
        self.save_processed_notifications(self.processed_notifications)
        
        return new_notifications
    
    def display_notifications(self, notifications: List[LinkedInNotification]):
        """Display the notifications in a formatted way"""
        print("\n" + "="*60)
        print("📧 LinkedIn Email Monitor Results")
        print("="*60)
        
        if not notifications:
            print("✅ No new LinkedIn notifications found in your email")
            return
        
        print(f"📊 Found {len(notifications)} new LinkedIn notifications")
        
        # Group by notification type
        comments = [n for n in notifications if n.notification_type == "comment"]
        likes = [n for n in notifications if n.notification_type == "like"]
        shares = [n for n in notifications if n.notification_type == "share"]
        
        if comments:
            print(f"\n💬 NEW COMMENTS ({len(comments)}):")
            print("-" * 40)
            for notification in comments:
                print(f"\n👤 {notification.comment_author}")
                print(f"💭 {notification.comment_content}")
                print(f"📝 Post: {notification.post_excerpt}")
                print(f"🕒 {notification.date}")
        
        if likes:
            print(f"\n❤️ NEW LIKES ({len(likes)}):")
            print("-" * 40)
            for notification in likes:
                print(f"👤 {notification.comment_author} liked your post")
                print(f"🕒 {notification.date}")
        
        if shares:
            print(f"\n🔄 NEW SHARES ({len(shares)}):")
            print("-" * 40)
            for notification in shares:
                print(f"👤 {notification.comment_author} shared your post")
                print(f"🕒 {notification.date}")

def show_email_setup_guide():
    """Show guide for setting up email monitoring"""
    print("\n" + "="*60)
    print("📧 EMAIL MONITORING SETUP GUIDE")
    print("="*60)
    
    print("""
STEP 1: Enable LinkedIn Email Notifications
1. Go to LinkedIn Settings & Privacy
2. Click on "Communications"
3. Click on "Email frequency"
4. Ensure "Comments on your posts and mentions" is enabled
5. Set frequency to "Individual emails" for real-time monitoring

STEP 2: Set Up Email Access (Gmail Example)
1. Enable 2-factor authentication on your Google account
2. Generate an "App Password":
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
3. Use this app password in your .env file

STEP 3: Configure .env File
Add these lines to your .env file:
EMAIL_HOST=imap.gmail.com
EMAIL_PORT=993
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password

For other email providers:
- Outlook: EMAIL_HOST=outlook.office365.com
- Yahoo: EMAIL_HOST=imap.mail.yahoo.com
- Other: Check your provider's IMAP settings

STEP 4: Run the Monitor
python email_monitor.py

This approach is more reliable than API access and doesn't violate ToS!
""")

def main():
    """Main function to run the email monitor"""
    print("📧 LinkedIn Email Monitor - Comment Notification Tracker")
    print("Monitoring email for LinkedIn notifications...\n")
    
    monitor = EmailMonitor()
    
    # Check if email credentials are configured
    if not monitor.email_username or not monitor.email_password:
        show_email_setup_guide()
        return
    
    try:
        # Get new notifications
        notifications = monitor.get_new_notifications(days=7)
        
        # Display results
        monitor.display_notifications(notifications)
        
        print(f"\n📝 Processed notifications saved to: {monitor.processed_file}")
        print("💡 Run this script regularly to monitor for new notifications!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        show_email_setup_guide()

if __name__ == "__main__":
    main()