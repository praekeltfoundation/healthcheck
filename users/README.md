### Users application
This application containts `User` model.
Superuser account can use [admin panel](http://127.0.0.1:8000/admin) to create new API users and provide existing users with access tokens.

API users are identified with a username, given to them by admin and can not perform any operatiosn with their accounts without superadmin interference.

API access tokens must be included in `Authorization` header in format `Token text_of_token`.