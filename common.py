from datetime import datetime
from time import time
from uuid import uuid5, NAMESPACE_X500
from hashlib import sha256
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_EXCEPTION
from os.path import join
import base64
import helpers
import mail_sender

def stamp(): return datetime.now().isoformat()
def gen_id(): return sha256(uuid5(NAMESPACE_X500, time().hex()).bytes).hexdigest()

def build_eml(to, subject, filename, message_id, base64str):
    with open(join(helpers.config.template_folder_path, "template.eml"), 'r') as fout:
        data = fout.read()
        data = data.replace('{{to}}', to)\
            .replace('{{subject}}', subject+'-'+message_id)\
            .replace('{{message_id}}', message_id)\
            .replace('{{filename}}', filename)\
            .replace('{{base64string}}', base64str)

        eml_path = f'{helpers.config.template_folder_path}/{message_id}.eml'
        with open(eml_path, 'w') as fin:
            fin.write(data)
            fin.close()
        fout.close()
    return eml_path

def sendmail_proc(eml_path):
    """ TODO : Implement SES  Here """
    ...

def sendmail(form_data, task_id):
    x_batch_size = int(form_data._dict["X-BATCH-SIZE"])
    x_target_inbox = form_data._dict["X-TARGET-INBOX"]
    x_file = form_data._dict["X-FILE"]
    x_thread_subject = form_data._dict["X-THREAD-SUBJECT"]
    b64str = base64.b64encode(x_file.file.read()).decode()
    eml_path = build_eml(
        filename=x_file.filename, subject=x_thread_subject, message_id=task_id, to=x_target_inbox, base64str=b64str
    )
    with ThreadPoolExecutor(max_workers=x_batch_size) as executor:
        fs = []
        for i in range(0, x_batch_size):
            fs.append(executor.submit(sendmail_proc, eml_path))
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