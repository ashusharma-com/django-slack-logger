import requests
import json
import time
import math
from copy import copy
from django.conf import settings
from django.utils.log import AdminEmailHandler, DEFAULT_LOGGING
from django.utils import timezone
from django.views.debug import ExceptionReporter

LOGGING = DEFAULT_LOGGING


class SlackExceptionHandler(AdminEmailHandler):


    def validate_settings(self):
        if hasattr(settings, 'SLACK_WEBHOOK_URL'):
            if settings.SLACK_WEBHOOK_URL is None:
                raise LookupError("You must define settings.SLACK_WEBHOOK_URL")
        else:
            raise ValueError("You must set settings.SLACK_WEBHOOK_URL.")

        if hasattr(settings, 'SLACK_ERROR_LEVEL'):
            self.SLACK_ERROR_LEVEL = settings.SLACK_ERROR_LEVEL

        if hasattr(settings, 'SLACK_SHORT_MESSAGE'):
            self.SLACK_SHORT_MESSAGE = settings.SLACK_SHORT_MESSAGE


    def __init__(self, include_html=False, email_backend=None, reporter_class=None):
        self.SLACK_ERROR_LEVEL = ["ERROR", "CRITICAL"]
        self.SLACK_SHORT_MESSAGE = False
        self.validate_settings()
        super().__init__()

    def emit(self, record, *args, **kwargs):
        try:
            request = record.request
            subject = '%s (%s IP): %s' % (
                record.levelname,
                ('internal' if request.META.get('REMOTE_ADDR') in settings.INTERNAL_IPS
                else 'EXTERNAL'),
                record.getMessage()
            )
        except Exception:
            subject = '%s: %s' % (
                record.levelname,
                record.getMessage()
            )
            request = None
        subject = self.format_subject(subject)

        no_exc_record = copy(record)
        no_exc_record.exc_info = None
        no_exc_record.exc_text = None

        if record.exc_info:
            exc_info = record.exc_info
        else:
            exc_info = (None, record.getMessage(), None)

        reporter = ExceptionReporter(request, is_email=True, *exc_info)
        message = "%s\n\n%s" % (self.format(no_exc_record), reporter.get_traceback_text())
        html_message = reporter.get_traceback_html() if self.include_html else None

        if hasattr(settings, 'SLACK_WITH_EMAIL') and settings.SLACK_WITH_EMAIL == True:
            self.send_mail(subject, message, fail_silently=True, html_message=html_message)

        color = ""
        if record.levelname == "CRITICAL":
            color = '#563d7c'
        if record.levelname == "ERROR":
            color = '#ff0018'
        if record.levelname == "WARNING":
            color = '#ffbd00'
        if record.levelname == "INFO":
            color = '#0078f0'
        if record.levelname == "DEBUG":
            color = '#d6d8da'

        attachments =  [
            {
                'title': subject,
                'color': color,
                'fields': [
                    {
                        "title": "Level",
                        "value": record.levelname,
                        "short": True,
                    },
                    {
                        "title": "Datetime",
                        "value": str(timezone.now()),
                        "short": True,
                    },
                    {
                        "title": "Method",
                        "value": request.method if request else 'No Request',
                        "short": True,
                    },
                    {
                        "title": "Path",
                        "value": request.path if request else 'No Request',
                        "short": True,
                    },
                    {
                        "title": "User",
                        "value": ( (request.user.username + ' (' + str(request.user.pk) + ')'
                                    if request.user.is_authenticated else 'Anonymous' )
                                    if request else 'No Request' ),
                        "short": True,
                    },
                    {
                        "title": "Status Code",
                        "value": record.status_code if hasattr(record, "status_code") else 'No Request',
                        "short": True,
                    },
                    {
                        "title": "UA",
                        "value": ( request.META['HTTP_USER_AGENT']
                                    if request and request.META else 'No Request' ),
                        "short": False,
                    },
                    {
                        "title": 'GET Params',
                        "value": json.dumps(request.GET) if request else 'No Request',
                        "short": False,
                    },
                    {
                        "title": "POST Data",
                        "value": json.dumps(request.POST) if request else 'No Request',
                        "short": False,
                    },
                ],
            },
        ]


        if not self.SLACK_SHORT_MESSAGE:
            split = 7900
            parts = range( math.ceil( len( message.encode('utf8') ) / split ) )

            for part in parts:
                start = 0     if part == 0 else split * part
                end   = split if part == 0 else split * part + split

                detail_text = '\r\n\r\n\r\n\r\n\r\n\r\n\r\n' + message[start:end]

                attachments.append({
                    'color': color,
                    'title': 'Details (Part {})'.format(part + 1),
                    'text': detail_text,
                    'ts': time.time(),
                })

        main_text = 'Error at ' + time.strftime("%A, %d %b %Y %H:%M:%S +0000", time.gmtime())

        data = {
          'payload': json.dumps({'main_text': main_text,'attachments': attachments}),
        }

        if record.levelname in self.SLACK_ERROR_LEVEL or ( self.SLACK_ERROR_LEVEL == "*" or self.SLACK_ERROR_LEVEL == ["*"]) :
            webhook_url = settings.SLACK_WEBHOOK_URL
            r = requests.post(webhook_url, data=data)



LOGGING['handlers']['slack_logger'] = {
  'level': 'INFO',
  'class': 'django_slack_logger.logger.SlackExceptionHandler',
}

LOGGING['loggers']['django'] = {
  'handlers': ['console', 'slack_logger'],
  'level': 'INFO',
}
