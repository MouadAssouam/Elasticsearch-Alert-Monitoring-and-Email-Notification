# Elasticsearch Alert Monitoring and Email Notification

This Python script monitors a specified Elasticsearch index for new alerts, checks for new documents, and sends email notifications when new alerts are detected. It supports timestamp conversion to GMT+1 and handles missing fields like `host.name` in alert data.

## Features

- **Elasticsearch Integration**: The script connects to an Elasticsearch instance to query for new alert documents.
- **Email Notifications**: Sends an email via SMTP whenever new alerts are found in the specified Elasticsearch index.
- **GMT+1 Time Conversion**: Converts timestamps from UTC to GMT+1 for easier interpretation of time.
- **Handles Missing Fields**: It checks and logs missing fields, like `host.name`, in the alerts.
- **Customizable Alert Criteria**: Queries alerts based on the timestamp and sends email notifications for new alerts.

## Requirements

- Python 3.6+
- Install the following Python libraries:
  - `elasticsearch` for interacting with Elasticsearch.
  - `smtplib` for sending emails (part of Python’s standard library).
  - `email` for constructing email messages (also part of Python’s standard library).

Install dependencies using `pip`:

```bash
pip install elasticsearch
```

## Configuration

### Elasticsearch Settings

The script connects to an Elasticsearch instance. You'll need to modify the following variables with your Elasticsearch instance's details:

- `ELASTIC_HOST`: The URL of your Elasticsearch instance (e.g., `https://elasticsearch:9200`).
- `ELASTIC_USERNAME`: The username for authentication (e.g., `elastic`).
- `ELASTIC_PASSWORD`: The password for authentication (e.g., `changeme`).
- `INDEX_NAME`: The name of the index to monitor for new alerts (e.g., `.internal.alerts-security.alerts-default-000001`).

### Email Settings

The script sends email notifications using SMTP. Modify these variables with your email settings:

- `SMTP_SERVER`: The SMTP server address (e.g., `smtp.gmail.com` for Gmail).
- `SMTP_PORT`: The port used by the SMTP server (typically `587` for Gmail).
- `EMAIL_USER`: Your email address (e.g., `email@mail.com`).
- `EMAIL_PASS`: The password for your email account.
- `EMAIL_TO`: The recipient email address to which alerts will be sent.

### Certificate for Elasticsearch

If your Elasticsearch server uses a self-signed certificate or requires SSL/TLS, you can specify the path to the CA certificate using:

- `ca_certs="C:/path/to/certs/ca.cert.pem"`

### Time Conversion

The script converts UTC timestamps in Elasticsearch to GMT+1 using the function `convert_to_gmt_plus_1()`.

### Last Timestamp

The script tracks the last timestamp in the index and only fetches alerts with a timestamp greater than this value. This ensures that it only checks for new alerts since the last time it was run.

## How to Use

1. **Install Dependencies**: Make sure Python 3.6+ is installed, and then install the required packages:

   ```bash
   pip install elasticsearch
   ```

2. **Edit Configuration**: Open the script and modify the following variables with your own values:
   - Elasticsearch connection settings (`ELASTIC_HOST`, `ELASTIC_USERNAME`, `ELASTIC_PASSWORD`, `INDEX_NAME`).
   - Email settings (`SMTP_SERVER`, `SMTP_PORT`, `EMAIL_USER`, `EMAIL_PASS`, `EMAIL_TO`).
   - Path to the certificate file for Elasticsearch (`ca_certs`).

3. **Run the Script**: Once everything is configured, simply run the script:

   ```bash
   python monitor_alerts.py
   ```

4. **Monitoring**: The script will continuously monitor the specified Elasticsearch index for new alerts. Every 10 seconds, it will check for new documents in the index and send an email if new alerts are detected.

## Example Output

When a new alert is detected, you will receive an email similar to the following:

### Email Subject:
```
New Alerts Detected
```

### Email Body:
```
New alerts have been added to the index .internal.alerts-security.alerts-default-000001:

Rule: rule-name-1, Host: host-name-1, Time: 2024-12-09 15:20:01
Rule: rule-name-2, Host: host-name-2, Time: 2024-12-09 15:30:45
...
```

If there are more than 10 new alerts, the email will show a summary, indicating the number of additional alerts.

## Customization

- **Alert Criteria**: The script fetches alerts based on a timestamp greater than the `last_timestamp`. You can modify the query to change the filtering criteria based on different fields or alert types.
- **Email Customization**: You can modify the email body formatting or add additional information to the email message as needed.
- **Time Conversion**: The `convert_to_gmt_plus_1()` function can be modified to convert to other time zones if necessary.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
