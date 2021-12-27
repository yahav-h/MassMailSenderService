import base64
from os.path import join, dirname, abspath
from datetime import datetime
from time import time
from uuid import uuid5, NAMESPACE_X500
from hashlib import sha256
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_EXCEPTION
from subprocess import PIPE, Popen
import shlex

class _Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(_Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class _Config(metaclass=_Singleton):
    _root_path = dirname(abspath(__file__))
    _templates_folder_path = join(_root_path, 'templates')
    _resources_folder_path = join(_root_path, 'resources')
    @property
    def __templates(self): return self._templates_folder_path
    @__templates.getter
    def template_folder_path(self): return self.__templates
    @property
    def __resources(self): return self._resources_folder_path
    @__resources.getter
    def resources_folder_path(self): return self.__resources
    def get_resource(self, resource): return join(self.template_folder_path, resource)


config = _Config()

def stamp(): return datetime.now().isoformat()
def gen_id(): return sha256(uuid5(NAMESPACE_X500, time().hex()).bytes).hexdigest()

def build_eml(to, subject, filename, message_id, base64str):
    with open(join(config.template_folder_path, "template.eml"), 'r') as fout:
        data = fout.read()
        data = data.replace('{{to}}', to)\
            .replace('{{subject}}', subject+'-'+message_id)\
            .replace('{{message_id}}', message_id)\
            .replace('{{filename}}', filename)\
            .replace('{{base64string}}', base64str)
        with open(f'{config.template_folder_path}/{message_id}.eml', 'w') as fin:
            fin.write(data)
            fin.close()
        fout.close()
    return message_id

def sendmail_proc(subject, message_id):
    cmd = 'echo -e "Subject:'+str(subject)+'-'+str(message_id)+'" | /usr/sbin/sendmail -vt < ./templates/'+str(message_id)+'.eml'
    cmd = shlex.split(cmd)
    try:
        proc = Popen(
            cmd, start_new_session=True, shell=True, stderr=PIPE, stdout=PIPE, stdin=PIPE
        )
        proc.communicate()
        return True
    except:
        return False

def sendmail(form_data, task_id):
    x_batch_size = int(form_data._dict["X-BATCH-SIZE"])
    x_target_inbox = form_data._dict["X-TARGET-INBOX"]
    x_file = form_data._dict["X-FILE"]
    x_thread_subject = form_data._dict["X-THREAD-SUBJECT"]
    b64str = base64.b64encode(x_file.file.read()).decode()
    build_eml(
        filename=x_file.filename, subject=x_thread_subject, message_id=task_id, to=x_target_inbox, base64str=b64str
    )
    with ThreadPoolExecutor(max_workers=x_batch_size) as executor:
        fs = []
        for i in range(0, x_batch_size):
            subject = x_thread_subject+'-'+task_id
            fs.append(executor.submit(sendmail_proc, subject, task_id))
        states = []
        for f in fs:
            states.append(wait(fs=[f], timeout=666, return_when=FIRST_EXCEPTION))
        if all([state.done for state in states]):
            futures = [s.done.pop() for s in states]
            if all([f._state == 'FINISHED' for f in futures]):
                results = [f.result() for f in futures]
                print(results)
            print("Done sending emails")
        else:
            print("not Done")