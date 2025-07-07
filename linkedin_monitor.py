#!/usr/bin/env python3
"""
LinkedIn Post Monitor - Check for New Comments on Recent Posts

IMPORTANT NOTES:
1. LinkedIn API access is now heavily restricted and requires business approval
2. Personal post/comment access through official API is extremely limited
3. This code provides a framework that would work with proper API credentials
4. Alternative approaches using LinkedIn's notification system may be more practical

Requirements:
- requests library: pip install requests
- python-dotenv: pip install python-dotenv

Setup:
1. Create a .env file with your LinkedIn API credentials (if available)
2. Follow LinkedIn's developer setup process for API access
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class Comment:
    """Represents a LinkedIn comment"""
    comment_id: str
    author_name: str
    author_id: str
    content: str
    created_at: str
    post_id: str

@dataclass
class Post:
    """Represents a LinkedIn post"""
    post_id: str
    content: str
    created_at: str
    author_name: str
    comments_count: int
    likes_count: int
    shares_count: int

class LinkedInAPIError(Exception):
    """Custom exception for LinkedIn API errors"""
    pass

class LinkedInMonitor:
    """
    LinkedIn Post Monitor
    
    Monitors your LinkedIn posts from the past 7 days for new comments.
    
    NOTE: Due to LinkedIn's API restrictions, this requires:
    1. Approved LinkedIn Developer Account
    2. Marketing API access (usually for businesses)
    3. Proper authentication tokens
    """
    
    def __init__(self):
        self.access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
        self.client_id = os.getenv('LINKEDIN_CLIENT_ID')
        self.client_secret = os.getenv('LINKEDIN_CLIENT_SECRET')
        self.base_url = "https://api.linkedin.com/v2"
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        
        # File to store previous comment state
        self.state_file = 'linkedin_comments_state.json'
        self.previous_comments = self.load_previous_state()
        
    def load_previous_state(self) -> Dict[str, List[str]]:
        """Load previously seen comments from file"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading previous state: {e}")
        return {}
    
    def save_current_state(self, current_comments: Dict[str, List[str]]):
        """Save current comment state to file"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(current_comments, f, indent=2)
        except Exception as e:
            print(f"Error saving state: {e}")
    
    def check_api_credentials(self) -> bool:
        """Check if API credentials are available and valid"""
        if not self.access_token:
            print("❌ LinkedIn API credentials not found!")
            print("\nTo use this script, you need:")
            print("1. LinkedIn Developer Account (developer.linkedin.com)")
            print("2. Create an app and get approval for API access")
            print("3. Obtain access token through OAuth flow")
            print("4. Add credentials to .env file:")
            print("   LINKEDIN_ACCESS_TOKEN=your_token_here")
            print("   LINKEDIN_CLIENT_ID=your_client_id")
            print("   LINKEDIN_CLIENT_SECRET=your_client_secret")
            return False
        
        # Test API connection
        try:
            response = self.make_api_request('/people/~')
            if response:
                print("✅ LinkedIn API connection successful!")
                return True
        except Exception as e:
            print(f"❌ API connection failed: {e}")
        
        return False
    
    def make_api_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make a request to LinkedIn API with error handling"""
        if not self.access_token:
            raise LinkedInAPIError("No access token available")
        
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.get(url, headers=self.headers, params=params)
            
            # Handle rate limiting
            if response.status_code == 429:
                print("⚠️ Rate limit reached. Waiting 60 seconds...")
                time.sleep(60)
                return self.make_api_request(endpoint, params)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return None
    
    def get_user_profile(self) -> Optional[Dict]:
        """Get current user's profile information"""
        return self.make_api_request('/people/~')
    
    def get_recent_posts(self, days: int = 7) -> List[Post]:
        """
        Get user's posts from the past N days
        
        NOTE: This endpoint may not be available for personal accounts
        LinkedIn API primarily serves business/marketing use cases
        """
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Convert to LinkedIn's timestamp format (milliseconds)
        start_timestamp = int(start_date.timestamp() * 1000)
        end_timestamp = int(end_date.timestamp() * 1000)
        
        params = {
            'q': 'author',
            'author': 'urn:li:person:YOUR_PERSON_ID',  # Would need to get this from profile
            'start': 0,
            'count': 50
        }
        
        posts_data = self.make_api_request('/shares', params)
        
        if not posts_data:
            return []
        
        posts = []
        for post_data in posts_data.get('elements', []):
            try:
                post = Post(
                    post_id=post_data.get('id', ''),
                    content=post_data.get('text', {}).get('text', ''),
                    created_at=post_data.get('created', {}).get('time', ''),
                    author_name=post_data.get('author', ''),
                    comments_count=post_data.get('totalSocialActivityCounts', {}).get('numComments', 0),
                    likes_count=post_data.get('totalSocialActivityCounts', {}).get('numLikes', 0),
                    shares_count=post_data.get('totalSocialActivityCounts', {}).get('numShares', 0)
                )
                posts.append(post)
            except Exception as e:
                print(f"Error parsing post data: {e}")
                continue
        
        return posts
    
    def get_post_comments(self, post_id: str) -> List[Comment]:
        """Get comments for a specific post"""
        params = {
            'q': 'post',
            'post': post_id,
            'start': 0,
            'count': 100
        }
        
        comments_data = self.make_api_request('/socialActions/{post_id}/comments', params)
        
        if not comments_data:
            return []
        
        comments = []
        for comment_data in comments_data.get('elements', []):
            try:
                comment = Comment(
                    comment_id=comment_data.get('id', ''),
                    author_name=comment_data.get('actor', {}).get('name', 'Unknown'),
                    author_id=comment_data.get('actor', {}).get('id', ''),
                    content=comment_data.get('message', {}).get('text', ''),
                    created_at=comment_data.get('created', {}).get('time', ''),
                    post_id=post_id
                )
                comments.append(comment)
            except Exception as e:
                print(f"Error parsing comment data: {e}")
                continue
        
        return comments
    
    def find_new_comments(self, posts: List[Post]) -> List[Comment]:
        """Find new comments by comparing with previous state"""
        new_comments = []
        current_state = {}
        
        for post in posts:
            post_comments = self.get_post_comments(post.post_id)
            current_comment_ids = [comment.comment_id for comment in post_comments]
            current_state[post.post_id] = current_comment_ids
            
            # Compare with previous state
            previous_comment_ids = self.previous_comments.get(post.post_id, [])
            
            for comment in post_comments:
                if comment.comment_id not in previous_comment_ids:
                    new_comments.append(comment)
        
        # Save current state for next run
        self.save_current_state(current_state)
        self.previous_comments = current_state
        
        return new_comments
    
    def format_output(self, posts: List[Post], new_comments: List[Comment]):
        """Format and display the monitoring results"""
        print("\n" + "="*60)
        print("🔍 LinkedIn Post Monitor Results")
        print("="*60)
        
        if not posts:
            print("❌ No posts found from the past 7 days")
            print("\nPossible reasons:")
            print("- No posts were made in the past 7 days")
            print("- API access limitations")
            print("- Authentication issues")
            return
        
        print(f"📊 Found {len(posts)} posts from the past 7 days")
        print(f"💬 Found {len(new_comments)} new comments")
        
        if new_comments:
            print("\n🆕 NEW COMMENTS:")
            print("-" * 40)
            
            # Group comments by post
            comments_by_post = {}
            for comment in new_comments:
                if comment.post_id not in comments_by_post:
                    comments_by_post[comment.post_id] = []
                comments_by_post[comment.post_id].append(comment)
            
            for post_id, comments in comments_by_post.items():
                # Find the corresponding post
                post = next((p for p in posts if p.post_id == post_id), None)
                
                print(f"\n📝 Post: {post.content[:100]}..." if post else f"\n📝 Post ID: {post_id}")
                print(f"   Created: {post.created_at if post else 'Unknown'}")
                
                for comment in comments:
                    print(f"\n   💬 New Comment:")
                    print(f"      👤 Author: {comment.author_name}")
                    print(f"      💭 Content: {comment.content}")
                    print(f"      🕒 Time: {comment.created_at}")
        else:
            print("\n✅ No new comments found on your recent posts")
        
        # Summary of all posts
        print(f"\n📈 POST SUMMARY:")
        print("-" * 40)
        for post in posts:
            print(f"\n📝 {post.content[:80]}...")
            print(f"   💬 {post.comments_count} comments | ❤️ {post.likes_count} likes | 🔄 {post.shares_count} shares")
            print(f"   🕒 {post.created_at}")

def show_alternative_approaches():
    """Show alternative approaches since API access is limited"""
    print("\n" + "="*60)
    print("🔄 ALTERNATIVE APPROACHES")
    print("="*60)
    
    print("""
Since LinkedIn API access is highly restricted, consider these alternatives:

1. 📱 LINKEDIN MOBILE/WEB NOTIFICATIONS:
   - Enable email notifications for comments
   - Use LinkedIn mobile app push notifications
   - Check LinkedIn notification bell regularly

2. 🤖 BROWSER AUTOMATION (Use Carefully):
   - Tools like Selenium could automate checking
   - ⚠️ May violate LinkedIn Terms of Service
   - Risk of account suspension

3. 📧 EMAIL MONITORING:
   - LinkedIn sends email notifications for comments
   - Parse emails automatically with email monitoring tools
   - More reliable and ToS-compliant

4. 📊 LINKEDIN ANALYTICS:
   - Use LinkedIn's built-in post analytics
   - Available in LinkedIn Creator Mode
   - Shows engagement metrics and trends

5. 🔔 MANUAL CHECKING:
   - Set reminders to check posts manually
   - Use LinkedIn's activity feed
   - Most reliable method currently available

RECOMMENDED: Enable LinkedIn email notifications and monitor your email inbox.
This is the most reliable and ToS-compliant approach.
""")

def main():
    """Main function to run the LinkedIn monitor"""
    print("🔗 LinkedIn Post Monitor - New Comment Checker")
    print("Checking posts from the past 7 days for new comments...\n")
    
    monitor = LinkedInMonitor()
    
    # Check API credentials first
    if not monitor.check_api_credentials():
        show_alternative_approaches()
        return
    
    try:
        # Get user profile for verification
        profile = monitor.get_user_profile()
        if profile:
            name = profile.get('localizedFirstName', '') + ' ' + profile.get('localizedLastName', '')
            print(f"👤 Monitoring posts for: {name}")
        
        # Get recent posts
        print("📥 Fetching recent posts...")
        posts = monitor.get_recent_posts(days=7)
        
        # Find new comments
        print("🔍 Checking for new comments...")
        new_comments = monitor.find_new_comments(posts)
        
        # Display results
        monitor.format_output(posts, new_comments)
        
    except LinkedInAPIError as e:
        print(f"❌ LinkedIn API Error: {e}")
        show_alternative_approaches()
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        show_alternative_approaches()

if __name__ == "__main__":
    main()