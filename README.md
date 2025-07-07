# LinkedIn Post Monitor

A comprehensive solution to monitor your LinkedIn posts from the past 7 days and detect new comments. Due to LinkedIn's API restrictions, this project offers both API-based and email-based monitoring approaches.

## ⚠️ Important: LinkedIn API Limitations

**LinkedIn has significantly restricted their API access as of 2024:**

- Personal access to posts and comments is extremely limited
- Official API primarily serves business/marketing use cases
- Requires business verification and extensive approval process
- Rate limits are very strict (100 connection requests/week, 80 profile views/day, etc.)

**Recommended Approach: Email Monitoring** 📧

The email monitoring approach is more reliable, doesn't violate terms of service, and works immediately without API approval.

## 🚀 Quick Start (Email Monitoring - Recommended)

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up LinkedIn email notifications:**
   - Go to LinkedIn Settings & Privacy
   - Communications → Email frequency
   - Enable "Comments on your posts and mentions"
   - Set frequency to "Individual emails"

3. **Configure email access:**
   ```bash
   cp .env.example .env
   # Edit .env with your email credentials
   ```

4. **Run the email monitor:**
   ```bash
   python email_monitor.py
   ```

## 📁 Project Structure

```
linkedin-monitor/
├── linkedin_monitor.py      # API-based monitoring (requires LinkedIn API access)
├── email_monitor.py         # Email-based monitoring (recommended)
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── README.md               # This file
└── .gitignore             # Git ignore file
```

## 🔧 Setup Instructions

### Option 1: Email Monitoring (Recommended)

#### Step 1: Enable LinkedIn Notifications
1. Go to [LinkedIn Settings & Privacy](https://www.linkedin.com/settings/)
2. Navigate to Communications → Email frequency
3. Enable "Comments on your posts and mentions"
4. Set frequency to "Individual emails" for real-time monitoring

#### Step 2: Configure Email Access

**For Gmail:**
1. Enable 2-factor authentication
2. Generate an App Password:
   - Google Account settings → Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
3. Use this app password (not your regular password)

**For Other Email Providers:**
- Outlook: `imap.outlook.com` or `outlook.office365.com`
- Yahoo: `imap.mail.yahoo.com`
- Check your provider's IMAP settings

#### Step 3: Configure Environment Variables
```bash
# Copy the example file
cp .env.example .env

# Edit .env file with your credentials
EMAIL_HOST=imap.gmail.com
EMAIL_PORT=993
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
```

#### Step 4: Run the Monitor
```bash
python email_monitor.py
```

### Option 2: API Monitoring (Advanced - Requires LinkedIn API Access)

#### Prerequisites
- LinkedIn Developer Account
- Approved LinkedIn Marketing API access
- Business verification (usually required)

#### Step 1: LinkedIn Developer Setup
1. Go to [LinkedIn Developer Portal](https://developer.linkedin.com/)
2. Create an app
3. Request Marketing API access
4. Complete business verification process
5. Obtain OAuth access token

#### Step 2: Configure API Credentials
```bash
# Edit .env file
LINKEDIN_ACCESS_TOKEN=your_access_token
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret
```

#### Step 3: Run API Monitor
```bash
python linkedin_monitor.py
```

## 📊 Features

### Email Monitor Features
- ✅ Parses LinkedIn notification emails
- ✅ Detects new comments, likes, and shares
- ✅ Tracks processed notifications to avoid duplicates
- ✅ Works with Gmail, Outlook, Yahoo, and other IMAP providers
- ✅ No API restrictions or rate limits
- ✅ Terms of Service compliant

### API Monitor Features
- 🔒 Fetches posts directly from LinkedIn API
- 🔒 Real-time comment detection
- 🔒 Detailed post analytics
- 🔒 Rate limiting and error handling
- ⚠️ Requires extensive API approval process

## 📈 Output Examples

### Email Monitor Output
```
📧 LinkedIn Email Monitor Results
============================================================
📊 Found 3 new LinkedIn notifications

💬 NEW COMMENTS (2):
----------------------------------------

👤 John Doe
💭 Great insights! Thanks for sharing this perspective on AI trends.
📝 Post: The future of artificial intelligence in business...
🕒 Mon, 08 Jan 2024 14:30:22 +0000

👤 Jane Smith
💭 I completely agree with your points about remote work.
📝 Post: Remote work productivity has increased by 40%...
🕒 Mon, 08 Jan 2024 16:45:18 +0000

❤️ NEW LIKES (1):
----------------------------------------
👤 Mike Johnson liked your post
🕒 Mon, 08 Jan 2024 12:15:33 +0000
```

### API Monitor Output
```
🔍 LinkedIn Post Monitor Results
============================================================
📊 Found 5 posts from the past 7 days
💬 Found 2 new comments

🆕 NEW COMMENTS:
----------------------------------------

📝 Post: The future of artificial intelligence in business applications...
   Created: 2024-01-08T10:30:00Z

   💬 New Comment:
      👤 Author: John Doe
      💭 Content: Great insights! Thanks for sharing.
      🕒 Time: 2024-01-08T14:30:22Z

📈 POST SUMMARY:
----------------------------------------

📝 The future of artificial intelligence in business applications...
   💬 5 comments | ❤️ 23 likes | 🔄 7 shares
   🕒 2024-01-08T10:30:00Z
```

## 🔄 Alternative Approaches

If both solutions don't work for your use case, consider these alternatives:

1. **LinkedIn Native Notifications**
   - Enable push notifications on mobile app
   - Use LinkedIn's notification bell on web

2. **Browser Automation** (Use with caution)
   - Tools like Selenium can automate checking
   - ⚠️ May violate LinkedIn Terms of Service
   - Risk of account suspension

3. **Manual Monitoring**
   - Set calendar reminders
   - Use LinkedIn's activity feed
   - Most reliable but requires manual effort

## 🛠️ Customization

### Adjusting Time Range
Both scripts can be customized to check different time periods:

```python
# Check last 3 days instead of 7
notifications = monitor.get_new_notifications(days=3)
```

### Adding More Email Providers
Extend the email monitor for other providers:

```python
# Add to your .env file
EMAIL_HOST=your.provider.com
EMAIL_PORT=993  # or 143 for non-SSL
```

### Filtering Notifications
Add custom filtering logic:

```python
# Example: Only show comments with certain keywords
filtered_comments = [
    n for n in notifications 
    if n.notification_type == "comment" and "urgent" in n.comment_content.lower()
]
```

## 🚨 Troubleshooting

### Email Monitor Issues

**"Failed to connect to email"**
- Check email credentials in .env file
- Ensure you're using app password for Gmail
- Verify IMAP is enabled for your email account
- Check firewall/network restrictions

**"No LinkedIn emails found"**
- Verify LinkedIn email notifications are enabled
- Check if emails are in spam folder
- Ensure you've posted content in the past 7 days
- LinkedIn might batch notifications

### API Monitor Issues

**"LinkedIn API credentials not found"**
- Check .env file configuration
- Verify all required credentials are set
- Ensure access token is valid and not expired

**"API connection failed"**
- LinkedIn API access may not be approved
- Rate limits might be exceeded
- Check LinkedIn Developer Console for app status

## 📝 Rate Limits & Best Practices

### LinkedIn API Limits (2024)
- Connection requests: 100/week
- Messages: 100-150/week  
- Profile visits: 80-100/day
- Searches: 300-6000/month
- Comments: ~30/day (recent reports)

### Email Monitoring Best Practices
- Run the script every few hours, not continuously
- Don't delete LinkedIn notification emails
- Keep processed notifications file for tracking
- Monitor your email quota with your provider

## 🔐 Security Notes

- Never commit `.env` file to version control
- Use app passwords instead of main email passwords
- Regularly rotate API tokens if using API approach
- Consider using environment variables in production

## 📜 Legal Disclaimer

This tool is for personal use only. Users are responsible for:
- Complying with LinkedIn's Terms of Service
- Respecting rate limits and usage policies
- Ensuring proper handling of personal data
- Understanding their email provider's terms

The email monitoring approach is generally more compliant as it uses standard email protocols and doesn't directly interact with LinkedIn's platform.

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review LinkedIn's current API policies
3. Verify your email provider's IMAP settings
4. Create an issue with detailed error messages

---

**Note**: LinkedIn frequently updates their API policies and email notification formats. This tool may need updates to remain compatible with future changes.
