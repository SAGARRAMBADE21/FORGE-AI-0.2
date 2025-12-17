"""
External API Generator Agent
Generates integration code for external APIs (Stripe, SendGrid, etc.).
"""

from typing import Dict, Any, List


class ExternalAPIGeneratorAgent:
    """Generates external API integrations."""
    
    def __init__(self, framework: str):
        self.framework = framework
    
    def generate(self, services: List[str]) -> Dict[str, str]:
        """Generate external API integration code."""
        
        integrations = {}
        
        for service in services:
            if "stripe" in service.lower():
                integrations.update(self._generate_stripe_integration())
            elif "sendgrid" in service.lower() or "email" in service.lower():
                integrations.update(self._generate_email_integration())
            elif "aws" in service.lower() or "s3" in service.lower():
                integrations.update(self._generate_s3_integration())
        
        return integrations
    
    def _generate_stripe_integration(self) -> Dict[str, str]:
        """Generate Stripe payment integration."""
        
        if self.framework == "fastapi":
            code = '''"""Stripe payment integration."""

import stripe
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.core.config import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

router = APIRouter(prefix="/payments", tags=["payments"])


class PaymentRequest(BaseModel):
    amount: int
    currency: str = "usd"
    description: str


@router.post("/create-payment-intent")
async def create_payment_intent(payment: PaymentRequest):
    """Create Stripe payment intent."""
    try:
        intent = stripe.PaymentIntent.create(
            amount=payment.amount,
            currency=payment.currency,
            description=payment.description
        )
        return {"client_secret": intent.client_secret}
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))
'''
            return {"app/api/routes/payments.py": code}
        
        else:  # Express
            code = '''const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
const express = require('express');
const router = express.Router();

router.post('/create-payment-intent', async (req, res) => {
  try {
    const { amount, currency, description } = req.body;
    
    const paymentIntent = await stripe.paymentIntents.create({
      amount,
      currency: currency || 'usd',
      description
    });
    
    res.json({ clientSecret: paymentIntent.client_secret });
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

module.exports = router;
'''
            return {"src/routes/payments.js": code}
    
    def _generate_email_integration(self) -> Dict[str, str]:
        """Generate email service integration."""
        
        if self.framework == "fastapi":
            code = '''"""Email service integration."""

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from app.core.config import settings


class EmailService:
    """Email service using SendGrid."""
    
    def __init__(self):
        self.client = SendGridAPIClient(settings.SENDGRID_API_KEY)
    
    def send_email(self, to_email: str, subject: str, content: str):
        """Send email."""
        message = Mail(
            from_email=settings.FROM_EMAIL,
            to_emails=to_email,
            subject=subject,
            html_content=content
        )
        
        try:
            response = self.client.send(message)
            return {"status": "sent", "status_code": response.status_code}
        except Exception as e:
            raise Exception(f"Email sending failed: {str(e)}")


email_service = EmailService()
'''
            return {"app/services/email_service.py": code}
        
        else:  # Express
            code = '''const sgMail = require('@sendgrid/mail');
sgMail.setApiKey(process.env.SENDGRID_API_KEY);

class EmailService {
  async sendEmail(to, subject, html) {
    const msg = {
      to,
      from: process.env.FROM_EMAIL,
      subject,
      html
    };
    
    try {
      await sgMail.send(msg);
      return { status: 'sent' };
    } catch (error) {
      throw new Error(`Email sending failed: ${error.message}`);
    }
  }
}

module.exports = new EmailService();
'''
            return {"src/services/emailService.js": code}
    
    def _generate_s3_integration(self) -> Dict[str, str]:
        """Generate AWS S3 integration."""
        
        if self.framework == "fastapi":
            code = '''"""AWS S3 file storage integration."""

import boto3
from botocore.exceptions import ClientError
from app.core.config import settings


class S3Service:
    """AWS S3 storage service."""
    
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket_name = settings.S3_BUCKET_NAME
    
    def upload_file(self, file_data: bytes, file_name: str) -> str:
        """Upload file to S3."""
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_name,
                Body=file_data
            )
            
            url = f"https://{self.bucket_name}.s3.amazonaws.com/{file_name}"
            return url
        except ClientError as e:
            raise Exception(f"S3 upload failed: {str(e)}")
    
    def get_file_url(self, file_name: str, expiration: int = 3600) -> str:
        """Generate presigned URL for file."""
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': file_name},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            raise Exception(f"URL generation failed: {str(e)}")


s3_service = S3Service()
'''
            return {"app/services/s3_service.py": code}
        
        else:  # Express
            code = '''const AWS = require('aws-sdk');

const s3 = new AWS.S3({
  accessKeyId: process.env.AWS_ACCESS_KEY_ID,
  secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
  region: process.env.AWS_REGION
});

class S3Service {
  async uploadFile(fileData, fileName) {
    const params = {
      Bucket: process.env.S3_BUCKET_NAME,
      Key: fileName,
      Body: fileData
    };
    
    try {
      await s3.upload(params).promise();
      return `https://${process.env.S3_BUCKET_NAME}.s3.amazonaws.com/${fileName}`;
    } catch (error) {
      throw new Error(`S3 upload failed: ${error.message}`);
    }
  }
  
  async getFileUrl(fileName, expiration = 3600) {
    const params = {
      Bucket: process.env.S3_BUCKET_NAME,
      Key: fileName,
      Expires: expiration
    };
    
    return s3.getSignedUrl('getObject', params);
  }
}

module.exports = new S3Service();
'''
            return {"src/services/s3Service.js": code}
