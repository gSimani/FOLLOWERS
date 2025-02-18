"""
Vercel serverless function entry point
"""
from social_automation.wsgi import application

# Vercel serverless function handler
app = application 