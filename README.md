# django-slack-logger
 
 Django errors logs into Slack channel

# Installation

Add **django-slack-logger** to your INSTALLED_APPS setting like this:

```
INSTALLED_APPS = [
    ...
    'django_slack_logger',
]
```
 Add **Slack Webhook URL** in settings.py file
```
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
```
By default you will get full error logs in your slack channel, if you want short log details you can set 
```
SLACK_SHORT_MESSAGE = True
```
You can also set specific error level you want to receive for that you can set
```
SLACK_ERROR_LEVEL = ["ERROR", "DEBUG", "INFO"] 
```
by default ``["ERROR", "CRITICAL"]`` for all error level you set ``"*"`` or  ``["*"]``

If you want to receive logs in email you can set `SLACK_WITH_EMAIL=True`  ( you need to configuration Django email  variables into settings.py with `ADMINS` ) by default it is False

```
	EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_PORT = 587
    EMAIL_HOST_USER = 'your@gmail.com'
    EMAIL_HOST_PASSWORD = 'password'
    EMAIL_USE_TLS = True
    ADMINS = [('Your Name', 'your@gmail.com'),]
```
## Creating Slack App

   Goto: https://api.slack.com/apps?new_app=1 to create app


![](https://a.slack-edge.com/80588/img/api/articles/bolt/config_create_app.png)


	 After creating app, In `Add features and functionality` tab click on `Incoming Webhooks` and make it turn on
 
  
![Slack-Incomming-Webhooks](https://i.ibb.co/4SmHmdx/Slack-Incomming-Webhooks.png)


	 Click on `Add New Webhook to Workspace` in new page select channel to post to as an app
 
 ![Slack-Activate-Webhooks](https://i.ibb.co/ZGhW5FL/Slack-Activate-Webhooks.png)
![Slack-Channel-to-Post](https://i.ibb.co/9cFD2j2/Slack-Channel-to-Post.png) 
 
	 Copy `Webhook URL` and add to `SLACK_WEBHOOK_URL`
 


![Slack-Webhooks-Copy](https://i.ibb.co/sgGzD9P/Slack-Webhooks-Copy.png)

	 Error notification 
![](https://i.ibb.co/60myDdV/Slack-OUTPUT.png)

