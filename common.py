import base64
import helpers
from os.path import join
from concurrent.futures import ThreadPoolExecutor as Thread_pool, wait, FIRST_EXCEPTION


MAX_TIMEOUT = 120
MAX_WORKERS = 10

def build_eml(to, subject, filename, message_id, context, base64str, **kwargs):
    helpers.logger.info(
        f"{kwargs.get('request').client.host} | {helpers.stamp()} | build_eml | " +
        f"params({to}, {subject}, {filename}, {message_id}, {context}, {base64})"
    )
    tmp_file = join(helpers.config.template_folder_path, "template.eml")
    helpers.logger.info(
        f"{kwargs.get('request').client.host} | {helpers.stamp()} | build_eml::open | params({tmp_file}, r)"
    )
    with open(tmp_file, 'r') as fout:
        data = fout.read()
        data = data.replace('{{to}}', to)\
            .replace('{{subject}}', subject+'-'+message_id)\
            .replace('{{message_id}}', message_id)\
            .replace('{{context}}', context)\
            .replace('{{filename}}', filename)\
            .replace('{{base64string}}', base64str)
        helpers.logger.info(
            f"{kwargs.get('request').client.host} | {helpers.stamp()} | send_mail::open::read | " +
            f"params({fout}) | returns({data})"
        )
        eml_path = f'{helpers.config.template_folder_path}/{message_id}.eml'
        helpers.logger.info(
            f"{kwargs.get('request').client.host} | {helpers.stamp()} | send_mail::open | params({eml_path}, w)"
        )
        with open(eml_path, 'w') as fin:
            fin.write(data)
            helpers.logger.info(
                f"{kwargs.get('request').client.host} | {helpers.stamp()} | send_mail::open::write | params({data}) "
            )
    helpers.logger.info(
        f"{kwargs.get('request').client.host} | {helpers.stamp()} | send_mail | returns({eml_path})"
    )
    return eml_path


def sendmail_proc(recipient, subject, body, message_id, b64_attachment_data, filename, **kwargs):
    helpers.logger.info(
        f"{kwargs.get('request').client.host} | {helpers.stamp()} | sendmail_proc | " +
        f"params({recipient}, {subject}, {body}, {message_id}, {b64_attachment_data}, {filename})"
    )
    res = helpers.ses.send_mail(recipient, subject, body, message_id, b64_attachment_data, filename, **kwargs)
    helpers.logger.info(f"{kwargs.get('request').client.host} | {helpers.stamp()} | sendmail_proc | returns({res})")
    # helpers.file_remove(eml_path, **kwargs)
    return res


def thread_state_checker(
        batch_size=None, recipient=None, subject=None, body=None,
        message_id=None, b64_attachment_data=None, filename=None, **kwargs
):
    helpers.logger.info(
        f"{kwargs.get('request').client.host} | {helpers.stamp()} | thread_state_checker | " +
        f"params({batch_size}, {recipient}, {subject}, {body} , {b64_attachment_data}, {filename})"
    )
    helpers.logger.info(
        f"{kwargs.get('request').client.host} | {helpers.stamp()} | thread_state_checker::Thread_pool | " +
        f"params({batch_size})"
    )
    with Thread_pool(max_workers=MAX_WORKERS) as executor:
        fs = []
        for i in range(0, batch_size):
            fs.append(
                executor.submit(
                    sendmail_proc, recipient, subject, body, message_id, b64_attachment_data, filename, **kwargs
                )
            )
        helpers.logger.info(
            f"{kwargs.get('request').client.host} | {helpers.stamp()} | thread_state_checker::Thread_pool | " +
            f"fs={fs})"
        )
        states = []
        for f in fs:
            states.append(wait(fs=[f], timeout=MAX_TIMEOUT, return_when=FIRST_EXCEPTION))
        helpers.logger.info(
            f"{kwargs.get('request').client.host} | {helpers.stamp()} | thread_state_checker::Thread_pool | " +
            f"states={states})"
        )
        if all([state.done for state in states]):
            futures = [s.done.pop() for s in states]
            if all([f._state == 'FINISHED' for f in futures]):
                results = [f.result() for f in futures]
            helpers.logger.info(
                f"{kwargs.get('request').client.host} | {helpers.stamp()} | thread_state_checker::Thread_pool | " +
                f"results({results}) | status=Done sending emails)"
            )
        else:
            helpers.logger.info(
                f"{kwargs.get('request').client.host} | {helpers.stamp()} | thread_state_checker::Thread_pool | " +
                f"results(None) | status=not Done)"
            )


def handle_form_data(form_data):
    x_context_type = form_data._dict["X-CONTEXT-TYPE"]
    if "clean" in x_context_type:
        x_context_type = "This is a clean email!"
    elif "phishing" in x_context_type:
        x_context_type = """This is a Phishing Email!\nhttp://operatf.xyz/redirect53dfhbhfhfhb"""
    elif "suspicious" in x_context_type:
        x_context_type = """This is a Suspicious Email!\nhttp://this-is-suspicious.com/login.php"""
    elif "malicious" in x_context_type:
        x_context_type = """This is a Malicious Email!\nhttp://www.xvira-malwareavrad.com"""
    else:
        x_context_type = """This is a Custom Email!\n%s""" % form_data._dict["X-RAW-DATA"]
    x_batch_size = int(form_data._dict["X-BATCH-SIZE"])
    x_target_inbox = form_data._dict["X-TARGET-INBOX"]
    x_thread_subject = form_data._dict["X-THREAD-SUBJECT"]
    x_file = form_data._dict["X-FILE"]
    b64str = base64.b64encode(x_file.file.read()).decode() if x_file != "null" else ""
    filename = x_file.filename if x_file != "null" else ""
    return x_batch_size, x_target_inbox, x_context_type, x_thread_subject, b64str, filename

def sendmail(form_data, task_id, **kwargs):
    helpers.logger.info(
        f"{kwargs.get('request').client.host} | {helpers.stamp()} | sendmail | params({form_data}, {task_id})"
    )
    x_batch_size, x_target_inbox, x_context_type, x_thread_subject, b64str, filename = handle_form_data(form_data)
    helpers.logger.info(
        f"{kwargs.get('request').client.host} | {helpers.stamp()} | sendmail_proc::thread_state_executor | " +
        f"params({filename}, {x_thread_subject}, {task_id}, {x_target_inbox}, {x_context_type}, {b64str})"
    )
    thread_state_checker(
        batch_size=x_batch_size, recipient=x_target_inbox, body=x_context_type, message_id=task_id,
        subject=x_thread_subject, b64_attachment_data=b64str, filename=filename, **kwargs
    )
