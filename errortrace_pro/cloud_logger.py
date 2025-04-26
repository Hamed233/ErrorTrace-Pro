"""
Cloud logging module for ErrorTrace Pro
"""
import os
import json
import logging
import uuid
import datetime
import platform
import socket
import sys
import traceback
from urllib.parse import urlparse
import http.client
import ssl
import base64

logger = logging.getLogger(__name__)

class CloudLogger:
    """
    Log exceptions to cloud services
    
    Currently supports:
    - Generic HTTP endpoint
    - Google Cloud Logging
    - AWS CloudWatch
    - Azure Application Insights
    """
    
    def __init__(self, provider=None, api_key=None, project_id=None):
        """
        Initialize the cloud logger
        
        Args:
            provider (str): Cloud provider ('gcp', 'aws', 'azure', 'http')
            api_key (str): API key for the cloud provider
            project_id (str): Project ID for the cloud provider
        """
        self.provider = provider or os.getenv("ERRORTRACE_PROVIDER", "http")
        self.api_key = api_key or os.getenv("ERRORTRACE_API_KEY")
        self.project_id = project_id or os.getenv("ERRORTRACE_PROJECT_ID")
        
        # Get endpoint from environment if needed
        self.endpoint = os.getenv("ERRORTRACE_ENDPOINT")
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate cloud logger configuration"""
        if self.provider not in ["gcp", "aws", "azure", "http"]:
            logger.warning(f"Unsupported cloud provider: {self.provider}. Falling back to 'http'")
            self.provider = "http"
            
        if self.provider != "http" and not self.api_key:
            logger.warning(f"No API key provided for {self.provider}. Cloud logging may not work.")
            
        if self.provider == "gcp" and not self.project_id:
            logger.warning("No project ID provided for GCP. Cloud logging may not work.")
            
        if self.provider == "http" and not self.endpoint:
            logger.warning("No HTTP endpoint provided. Cloud logging will be disabled.")
    
    def log_exception(self, exc_type, exc_value, traceback_str, context=None, visual_traceback=None):
        """
        Log an exception to the configured cloud service
        
        Args:
            exc_type (type): Exception type
            exc_value (Exception): Exception value
            traceback_str (list): Traceback string lines
            context (dict): Additional context information
            visual_traceback (str): Visual representation of the traceback
            
        Returns:
            bool: True if logging was successful, False otherwise
        """
        if not self.api_key and self.provider != "http":
            logger.warning("No API key provided. Skipping cloud logging.")
            return False
            
        if self.provider == "http" and not self.endpoint:
            logger.warning("No HTTP endpoint provided. Skipping cloud logging.")
            return False
        
        # Prepare the error data
        error_data = self._prepare_error_data(exc_type, exc_value, traceback_str, context, visual_traceback)
        
        # Log to the appropriate provider
        if self.provider == "gcp":
            return self._log_to_gcp(error_data)
        elif self.provider == "aws":
            return self._log_to_aws(error_data)
        elif self.provider == "azure":
            return self._log_to_azure(error_data)
        else:  # http
            return self._log_to_http(error_data)
    
    def _prepare_error_data(self, exc_type, exc_value, traceback_str, context=None, visual_traceback=None):
        """
        Prepare the error data for logging
        
        Args:
            exc_type (type): Exception type
            exc_value (Exception): Exception value
            traceback_str (list): Traceback string lines
            context (dict): Additional context information
            visual_traceback (str): Visual representation of the traceback
            
        Returns:
            dict: Formatted error data
        """
        # Generate a unique error ID
        error_id = str(uuid.uuid4())
        
        # Get basic system information
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        
        # Create the error data structure
        error_data = {
            "error_id": error_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "exception": {
                "type": exc_type.__name__,
                "message": str(exc_value),
                "module": exc_type.__module__
            },
            "traceback": traceback_str if isinstance(traceback_str, list) else traceback_str.split("\n"),
            "system": {
                "hostname": hostname,
                "ip_address": ip_address,
                "python_version": platform.python_version(),
                "platform": platform.platform(),
                "system": platform.system(),
                "processor": platform.processor()
            }
        }
        
        # Add the visual traceback if provided
        if visual_traceback:
            error_data["visual_traceback"] = visual_traceback
            
        # Add any additional context
        if context:
            error_data["context"] = context
            
        return error_data
    
    def _log_to_http(self, error_data):
        """
        Log error to a generic HTTP endpoint
        
        Args:
            error_data (dict): Error data to log
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.endpoint:
            return False
            
        try:
            # Parse the endpoint URL
            url = urlparse(self.endpoint)
            
            # Determine whether to use HTTPS
            use_https = url.scheme == "https"
            
            # Create the appropriate connection
            if use_https:
                conn = http.client.HTTPSConnection(url.netloc)
            else:
                conn = http.client.HTTPConnection(url.netloc)
                
            # Prepare headers
            headers = {
                "Content-Type": "application/json"
            }
            
            # Add authorization if API key is provided
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
                
            # Send the request
            conn.request(
                "POST",
                url.path or "/",
                body=json.dumps(error_data),
                headers=headers
            )
            
            # Get the response
            response = conn.getresponse()
            
            # Check if it was successful
            success = 200 <= response.status < 300
            
            if not success:
                logger.warning(f"Failed to log to HTTP endpoint: {response.status} {response.reason}")
                
            conn.close()
            return success
            
        except Exception as e:
            logger.error(f"Error logging to HTTP endpoint: {e}")
            return False
    
    def _log_to_gcp(self, error_data):
        """
        Log error to Google Cloud Logging
        
        Args:
            error_data (dict): Error data to log
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.api_key or not self.project_id:
            return False
            
        try:
            # GCP Cloud Logging API endpoint
            endpoint = f"logging.googleapis.com"
            
            # Create HTTPS connection
            conn = http.client.HTTPSConnection(endpoint)
            
            # Format the data for Cloud Logging
            log_entry = {
                "entries": [{
                    "logName": f"projects/{self.project_id}/logs/errortrace-pro",
                    "severity": "ERROR",
                    "jsonPayload": error_data
                }]
            }
            
            # Prepare headers
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # Send the request
            conn.request(
                "POST",
                f"/v2/entries:write",
                body=json.dumps(log_entry),
                headers=headers
            )
            
            # Get the response
            response = conn.getresponse()
            
            # Check if it was successful
            success = 200 <= response.status < 300
            
            if not success:
                logger.warning(f"Failed to log to GCP: {response.status} {response.reason}")
                
            conn.close()
            return success
            
        except Exception as e:
            logger.error(f"Error logging to GCP: {e}")
            return False
    
    def _log_to_aws(self, error_data):
        """
        Log error to AWS CloudWatch
        
        Args:
            error_data (dict): Error data to log
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.api_key:
            return False
            
        try:
            # AWS CloudWatch Logs endpoint
            endpoint = "logs.amazonaws.com"
            
            # Create HTTPS connection
            conn = http.client.HTTPSConnection(endpoint)
            
            # Format the data for CloudWatch
            log_event = {
                "logGroupName": "errortrace-pro",
                "logStreamName": f"errors-{datetime.datetime.now().strftime('%Y-%m-%d')}",
                "logEvents": [
                    {
                        "timestamp": int(datetime.datetime.now().timestamp() * 1000),
                        "message": json.dumps(error_data)
                    }
                ]
            }
            
            # Prepare headers
            headers = {
                "Content-Type": "application/json",
                "X-Amz-Target": "Logs_20140328.PutLogEvents",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # Send the request
            conn.request(
                "POST",
                "/",
                body=json.dumps(log_event),
                headers=headers
            )
            
            # Get the response
            response = conn.getresponse()
            
            # Check if it was successful
            success = 200 <= response.status < 300
            
            if not success:
                logger.warning(f"Failed to log to AWS: {response.status} {response.reason}")
                
            conn.close()
            return success
            
        except Exception as e:
            logger.error(f"Error logging to AWS: {e}")
            return False
    
    def _log_to_azure(self, error_data):
        """
        Log error to Azure Application Insights
        
        Args:
            error_data (dict): Error data to log
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.api_key:
            return False
            
        try:
            # Azure Application Insights endpoint
            endpoint = "dc.services.visualstudio.com"
            
            # Create HTTPS connection
            conn = http.client.HTTPSConnection(endpoint)
            
            # Format the data for Application Insights
            app_insights_data = {
                "name": "Microsoft.ApplicationInsights.Exception",
                "time": datetime.datetime.now().isoformat(),
                "iKey": self.api_key,
                "data": {
                    "baseType": "ExceptionData",
                    "baseData": {
                        "ver": 2,
                        "exceptions": [
                            {
                                "typeName": error_data["exception"]["type"],
                                "message": error_data["exception"]["message"],
                                "hasFullStack": True,
                                "stack": "\n".join(error_data["traceback"]) if isinstance(error_data["traceback"], list) else error_data["traceback"]
                            }
                        ],
                        "properties": {
                            "error_id": error_data["error_id"],
                            "python_version": error_data["system"]["python_version"],
                            "platform": error_data["system"]["platform"]
                        }
                    }
                }
            }
            
            # Prepare headers
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            # Send the request
            conn.request(
                "POST",
                f"/v2/track",
                body=json.dumps(app_insights_data),
                headers=headers
            )
            
            # Get the response
            response = conn.getresponse()
            
            # Check if it was successful
            success = 200 <= response.status < 300
            
            if not success:
                logger.warning(f"Failed to log to Azure: {response.status} {response.reason}")
                
            conn.close()
            return success
            
        except Exception as e:
            logger.error(f"Error logging to Azure: {e}")
            return False
