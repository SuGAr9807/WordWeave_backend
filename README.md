# Word Weave

## Templates are not used as pure css and html is harder than using React
## It also take large time and we are using agile model to complete it in time


# APIS FOR AUTHORIZATION

## SignUp API

### http://127.0.0.1:8000/signup/
method: POST

Left side:
Content-TYPE : multipart/form-data

Right side:

Type: Form

username: text
name: text
email: text
password: text
profile_picture: file


## Login API

method: POST

Left side:
Content-TYPE : application/json

Right side:

Type: TEXT

example:
- {
- "email":"abc@gmail.com",
- "password":"password"
- }