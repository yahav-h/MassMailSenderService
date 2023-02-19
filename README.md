# MassMailSenderService

---
This is a server side application which uses the AWS/SES for mass distribution of emails .

---
## Configuration 
when this project is being cloned for the first time, 
note the `properties.json` configuration file
```json
{
  "service": <AWS-SERVICE-TYPE-HERE>,  /* E.g: "ses" */
  "region": <AWS-SERVICE-REGION-HERE>, /* E.g: "us-east-1" */
  "access-key": <AWS-ACCESS-KEY-HERE>, /* E.g: "blah-blah-123-123" */
  "secret-key": <AWS-SECRET-KEY-HERE>  /* E.g: "123-blah-123-blah" */
}
```
the service uses the above template for which allow us to interact with the SES.

---

## Disclaimer
generally , 
the service within this repository developed using `Python3.9.2`  
hence,  
I suggest you to create a `venv` for any operation made by the service app.

---
### Setup Environment
follow the steps , and you're good to go!
```shell
# create a virtual environment for the service
$> python3 -m venv venv

# upgrade pip
$> ./venv/bin/python3.9 -m pip install --upgrade pip

# install all server dependencies
$> ./venv/bin/python3.9 -m pip install -r ./requirements.txt
```

---
### Endpoints Docs
This Service have three (3) endpoints,  

<p>
    The 1st is a UI `/`.
    <br/>See documentation below:
</p>

```xml
<route name="/">
    <url method="GET">
        http://localhost:80/
    </url>
    <description>
        This endpoint will load  an `index.html` template page. 
    </description>
</route>
```
---
<p>
    The 2nd is a `swagger` endpoint.
    <br/>See documentation below:
</p>

```xml
<route name="docs#">
    <url method="GET">
        http://localhost:80/docs#
    </url>
    <description>
        This endpoint will serve a SWAGGER UI which  
        documents and mapp all available endpoint in the backend  
    </description>
</route>
```
---
<p>
    The 3rd is a RESTFUL API `/api/tasks`.
    <br/>See documentation below:
</p>

```xml
<route name="/api/tasks">
    <url method="POST">
        http://localhost:80/api/tasks
    </url>
    <description>
        This endpoint will serve a single rest  
        call that contains the metadata required for    
        the service to handle a massive email distribution   
    </description>
    <payload type="application/www-form-data">
        <X-TARGET-INBOX required="true">
            recipient inbox 
        </X-TARGET-INBOX>
        <X-FILE required="true">
            an attachment file
        </X-FILE>
        <X-THREAD-SUBJECT required="true">
            the subject of the message
        </X-THREAD-SUBJECT>
        <X-BATCH-SIZE required="true">
            the batch size of how many emails
        </X-BATCH-SIZE>
        <X-CONTEXT-TYPE required="true">
            the type of email content (clean, phishing, suspicious, malicious, custom)
        </X-CONTEXT-TYPE>
        <X-RAW-DATA required="false">
            a custom email content (applied only when X-CONTEXT-TYPE is custom) 
        </X-RAW-DATA>
    </payload>
</route>

```
---
### Startup
running the service using the following script
```shell
chmod +x ./start_service.sh && sudo ./start_service.sh
```
