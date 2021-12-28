import boto3
import helpers

class AbstractSender(object):

    def send_mail(self, mails):
        pass

    def send_wd_mail(self, mails):
        pass


class SesMailSender(AbstractSender):
    ses_client = None

    def __init__(self):
        data = helpers.config.get_resource("properties.json")
        self.ses_client = boto3.client(
            data['service'],
            region_name=data['region'],
            aws_access_key_id=data['access-key'],
            aws_secret_access_key=data['secret-key']
        )

    def send_mail(self, eml):
        ...