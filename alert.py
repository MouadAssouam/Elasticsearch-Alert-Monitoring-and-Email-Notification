import time
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Elasticsearch connection settings
ELASTIC_HOST = "https://elasticsearch:9200"  # Replace with your Elasticsearch host
ELASTIC_USERNAME = "elastic"  # Replace with your username
ELASTIC_PASSWORD = "changeme"  # Replace with your password
INDEX_NAME = ".internal.alerts-security.alerts-default-000001"

# Email settings
SMTP_SERVER = "smtp.gmail.com" # Replace with your SMTP server
SMTP_PORT = 587 # Replace with your SMTP port
EMAIL_USER = "email@mail.com" # Replace with your email address
EMAIL_PASS = "changeme" # Replace with your email password
EMAIL_TO = "email@mail.com" # Replace with the recipient email address

# Initialize Elasticsearch client
es = Elasticsearch(
    [ELASTIC_HOST],
    http_auth=(ELASTIC_USERNAME, ELASTIC_PASSWORD),
    ca_certs="C:/path/to/certs/ca.cert.pem"
)

# Track last timestamp
last_timestamp = None

def convert_to_gmt_plus_1(utc_timestamp):
    """
    Convert UTC timestamp to GMT+1.
    """
    try:
        utc_time = datetime.strptime(utc_timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
        gmt_plus_1_time = utc_time + timedelta(hours=1)
        return gmt_plus_1_time.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print(f"Error converting timestamp: {e}")
        return utc_timestamp  # Fallback to original timestamp

def send_email(subject, body):
    """
    Send an email notification with the given subject and body.
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = EMAIL_TO
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, EMAIL_TO, msg.as_string())
        
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

def monitor_index():
    """
    Monitor the Elasticsearch index for new documents and send alerts via email.
    """
    global last_timestamp
    try:
        if last_timestamp:
            query = {
                "query": {
                    "range": {
                        "@timestamp": {
                            "gt": last_timestamp
                        }
                    }
                },
                "sort": [
                    {"@timestamp": "asc"}
                ],
                "_source": ["kibana.alert.rule.name", "host.name", "@timestamp"]
            }
        else:
            query = {
                "size": 1,
                "sort": [
                    {"@timestamp": "asc"}
                ],
                "_source": ["kibana.alert.rule.name", "host.name", "@timestamp"]
            }

        search_response = es.search(
            index=INDEX_NAME,
            body=query
        )
        alerts = search_response['hits']['hits']
        
        if not alerts:
            print("No new documents found.")
            return
        
        alert_details = []
        max_timestamp = last_timestamp if last_timestamp else None

        for alert in alerts:
            source = alert["_source"]
            rule_name = source.get("kibana.alert.rule.name", "N/A")
            
            # Check for host.name in multiple ways
            host_name = "N/A"
            if "host.name" in source:
                host_name = source["host.name"]
            elif "host" in source and isinstance(source["host"], dict):
                host_name = source["host"].get("name", "N/A")
            
            # Log missing host.name
            if host_name == "N/A":
                print(f"Host name missing for alert: {alert['_id']}")
                print(source)
            
            timestamp = source.get("@timestamp", "N/A")
            local_time = convert_to_gmt_plus_1(timestamp) if timestamp != "N/A" else "N/A"
            alert_details.append(f"Rule: {rule_name}, Host: {host_name}, Time: {local_time}")
            
            if timestamp != "N/A" and (max_timestamp is None or timestamp > max_timestamp):
                max_timestamp = timestamp

        alert_message = "\n".join(alert_details)

        # Limit email size for too many alerts
        if len(alert_details) > 10:
            alert_message = "\n".join(alert_details[:10]) + f"\n...and {len(alert_details) - 10} more alerts."

        send_email(
            subject="New Alerts Detected",
            body=f"New alerts have been added to the index {INDEX_NAME}:\n\n{alert_message}"
        )

        if max_timestamp:
            last_timestamp = max_timestamp

    except Exception as e:
        print(f"Error monitoring index: {e}")

if __name__ == "__main__":
    try:
        initial_query = {
            "size": 1,
            "sort": [
                {"@timestamp": "desc"}
            ],
            "_source": ["@timestamp"]
        }
        initial_response = es.search(
            index=INDEX_NAME,
            body=initial_query
        )
        if initial_response['hits']['hits']:
            last_timestamp = initial_response['hits']['hits'][0]['_source']['@timestamp']
            print(f"Initialized with last timestamp: {last_timestamp}")
        else:
            last_timestamp = None
            print("No documents found in the index.")
    except Exception as e:
        print(f"Error initializing last timestamp: {e}")
    
    while True:
        monitor_index()
        time.sleep(10)
readme okay here
