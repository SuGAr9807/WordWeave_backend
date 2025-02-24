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

### http://127.0.0.1:8000/login/
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

output: 
token : "token"

- save the token

## Change Password API when logged in

### http://127.0.0.1:8000/change-password/
method: POST
note:only do when you are logged in and have token


Left side:
Content-TYPE : application/json
Authorization : Bearer <token>

Right side:

Type: TEXT

example:
- {
- "current_password":"currentpass",
- "new_password":"newpass"
- }



## Forgot Password API

### http://127.0.0.1:8000/password-reset/
method: POST


Left side:
Content-TYPE : application/json

Right side:

Type: TEXT

example:
- {
- "email":"abc@gmail.com"
- }

output: We will get the email on the given email address to change the password

## Logout API

### http://127.0.0.1:8000/logout/
method: POST


Left side:
Content-TYPE : application/json
Authorization : Bearer <token>

Right side:
Nothing needed


output: Token is removed and you are logged out from backend