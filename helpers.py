import boto3
import email
import logging
from os import remove
from time import time
from hashlib import sha256
from datetime import datetime
from yaml import load, Loader
from uuid import uuid5, NAMESPACE_X500
from os.path import join, dirname, abspath, exists
from logging.handlers import RotatingFileHandler

_root_path = dirname(abspath(__file__))
_logs_folder_path = join(_root_path, 'logs')
_templates_folder_path = join(_root_path, 'templates')
_resources_folder_path = join(_root_path, 'resources')

logging.Formatter(logging.BASIC_FORMAT)
logger = logging.getLogger('ServiceLogger')
logger.setLevel(logging.DEBUG)
logger.addHandler(
    RotatingFileHandler(
        filename='%s/runtime.log' % _logs_folder_path,
        maxBytes=818200,
        backupCount=5
    )
)

def stamp(): return datetime.now().isoformat()
def gen_id(): return sha256(uuid5(NAMESPACE_X500, time().hex()).bytes).hexdigest()

def file_remove(path, **kwargs):
    logger.info(f"{kwargs.get('request').client.host} | {stamp()} | file_remove | params({path}")
    msg = f"{kwargs.get('request').client.host} | {stamp()} | file_remove | exists({exists(path)})"
    try:
        if exists(path):
            remove(path)
            logger.info(f"{msg} | removed({True if not exists(path) else False})")
        else:
            logger.info(f"{msg} | removed({True if exists(path) else False})")
    except Exception as e:
        logger.error(f"{msg} | removed({exists(path)}) | error({str(e)})")
    return


class _Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(_Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class _Config(metaclass=_Singleton):
    @property
    def __templates(self): return _templates_folder_path
    @__templates.getter
    def template_folder_path(self): return self.__templates
    @property
    def __resources(self): return _resources_folder_path
    @__resources.getter
    def resources_folder_path(self): return self.__resources

    def get_resource(self, resource):
        logger.info(f"{stamp()} | get_resource | params({resource})")
        try:
            with open(join(self.resources_folder_path, resource)) as fp:
                data = load(fp, Loader)
                logger.info(f"{stamp()} | get_resource | returns({data})")
                return data
        except Exception as e:
            logger.error(f"{stamp()} | get_resource | error({str(e)}) | returns(False)")
            return False


config = _Config()

class SesMailSender(object, metaclass=_Singleton):
    ses_client = None

    def __init__(self):
        props = config.get_resource("properties.yml")
        self.ses_client = boto3.client(
            props.get("config").get("service"),
            region_name=props.get("config").get("region"),
            aws_access_key_id=props.get("config").get("access-key"),
            aws_secret_access_key=props.get("config").get("secret-key")
        )

    def send_mail(self, path, to, **kwargs):
        logger.info(f"{kwargs.get('request').client.host} | {stamp()} | send_mail | params({path}, {to})")
        try:
            logger.info(f"{kwargs.get('request').client.host} | {stamp()} | send_mail::open | params({path}, 'r')")
            with open(path, 'r') as eml_file:
                msg = email.message_from_file(eml_file)
                logger.info(
                    f"{kwargs.get('request').client.host} | {stamp()} | send_mail::open::email.message_from_file | " +
                    f"params({eml_file}) | returns({msg})"
                )
            del(msg['From'])
            msg['From'] = "noreply@mss.avanan.net"
            logger.info(f"{kwargs.get('request').client.host} | {stamp()} | send_mail::del['From'] | returns({msg})")
            for key in msg.keys().copy():
                if 'X-CLOUD-SEC-AV' in key:
                    del(msg[key])
                    logger.info(
                        f"{kwargs.get('request').client.host} | {stamp()} | send_mail::del['{key}'] | returns({msg})"
                    )
            params = {
                "RawMessage": {'Data': msg.as_string()},
                "Source": "Distributor@avtestqa.com",
                "Destinations": [to]
            }
            logger.info(
                f"{kwargs.get('request').client.host} | {stamp()} | send_mail::ses_client.send_raw_email | " +
                f"params({params})")
            response = self.ses_client.send_raw_email(**params)
            logger.info(
                f"{kwargs.get('request').client.host} | {stamp()} | send_mail | returns(True, {response})"
            )
            return True, response
        except Exception as e:
            logger.error(
                f"{kwargs.get('request').client.host} | {stamp()} | send_mail | error({str(e)}) | returns(False, None)"
            )
            return False, None


ses = SesMailSender()
