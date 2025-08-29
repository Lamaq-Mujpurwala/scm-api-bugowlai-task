import os
import json
from typing import Dict, Any, Optional
import httpx
from abc import ABC, abstractmethod

class NotificationProvider(ABC):
    """Abstract base class for notification providers"""
    
    @abstractmethod
    async def send_notification(self, message: str, recipient: str) -> Dict[str, Any]:
        pass

class SlackService(NotificationProvider):
    """Slack notification service"""
    
    def __init__(self):
        self.webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        self.channel = os.getenv("SLACK_CHANNEL", "#general")
        
    async def send_notification(self, message: str, recipient: str = None) -> Dict[str, Any]:
        """Send notification to Slack channel"""
        if not self.webhook_url:
            raise ValueError("Slack webhook URL not configured")
            
        payload = {
            "channel": self.channel,
            "text": f"🚨 Content Moderation Alert\n\n{message}",
            "username": "SCM Bot",
            "icon_emoji": ":warning:"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.webhook_url,
                json=payload
            )
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "provider": "slack",
                    "message": "Notification sent successfully"
                }
            else:
                return {
                    "status": "failed",
                    "provider": "slack",
                    "error": f"Slack API error: {response.status_code}"
                }

class EmailService(NotificationProvider):
    """Email notification service using BrevoMail"""
    
    def __init__(self):
        self.api_key = os.getenv("BREVO_API_KEY")
        self.sender_email = os.getenv("SENDER_EMAIL")
        self.base_url = "https://api.brevo.com/v3"
        
    async def send_notification(self, message: str, recipient: str) -> Dict[str, Any]:
        """Send email notification using BrevoMail"""
        if not self.api_key:
            raise ValueError("BrevoMail API key not configured")
            
        if not self.sender_email:
            raise ValueError("Sender email not configured")
            
        payload = {
            "sender": {
                "name": "SCM Content Moderation",
                "email": self.sender_email
            },
            "to": [
                {
                    "email": recipient,
                    "name": recipient.split("@")[0]
                }
            ],
            "subject": "Content Moderation Alert",
            "htmlContent": f"""
            <html>
                <body>
                    <h2>🚨 Content Moderation Alert</h2>
                    <p>{message}</p>
                    <hr>
                    <p><small>This is an automated message from the SCM Content Moderation System.</small></p>
                </body>
            </html>
            """
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/smtp/email",
                headers={
                    "api-key": self.api_key,
                    "Content-Type": "application/json"
                },
                json=payload
            )
            
            if response.status_code == 201:
                return {
                    "status": "success",
                    "provider": "email",
                    "message": "Email sent successfully"
                }
            else:
                return {
                    "status": "failed",
                    "provider": "email",
                    "error": f"BrevoMail API error: {response.status_code} - {response.text}"
                }

class NotificationService:
    """Main notification service that manages different providers"""
    
    def __init__(self):
        self.providers = {}
        
        # Initialize available providers
        if os.getenv("SLACK_WEBHOOK_URL"):
            self.providers["slack"] = SlackService()
            
        if os.getenv("BREVO_API_KEY"):
            self.providers["email"] = EmailService()
    
    async def send_notification(
        self, 
        message: str, 
        recipient: str = None, 
        channels: list = None
    ) -> Dict[str, Any]:
        """Send notification through specified channels"""
        if not channels:
            channels = list(self.providers.keys())
            
        results = {}
        
        for channel in channels:
            if channel in self.providers:
                try:
                    if channel == "email" and recipient:
                        result = await self.providers[channel].send_notification(message, recipient)
                    else:
                        result = await self.providers[channel].send_notification(message)
                    results[channel] = result
                except Exception as e:
                    results[channel] = {
                        "status": "failed",
                        "provider": channel,
                        "error": str(e)
                    }
            else:
                results[channel] = {
                    "status": "failed",
                    "provider": channel,
                    "error": "Provider not configured"
                }
        
        return results
    
    async def send_moderation_alert(
        self, 
        user_email: str, 
        classification: str, 
        content_type: str,
        confidence: float,
        reasoning: str,
        channels: list = None
    ) -> Dict[str, Any]:
        """Send specific moderation alert"""
        message = f"""
        **Content Moderation Alert**
        
        **User:** {user_email}
        **Content Type:** {content_type}
        **Classification:** {classification.upper()}
        **Confidence:** {confidence:.2f}
        **Reasoning:** {reasoning}
        
        **Action Required:** Review this content and take appropriate action.
        """
        
        return await self.send_notification(message, user_email, channels)
