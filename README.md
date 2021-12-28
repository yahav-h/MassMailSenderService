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

### Startup
run `start_service.sh` script to start the service
