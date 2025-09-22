# new-voc-website
## Developer Setup ##
1. Fork and clone this repository
2. Create a Python virtual environment using venv. The specific instructions are different depending on your operating system, and can be found [here](https://docs.python.org/3/library/venv.html)
3. With the virtual environment activated, install dependencies
    ```
    pip install -r requirements.txt
    ```
4. Create a superuser (admin) login and add them as a VOC Exec
   ```sh
    python manage.py createsuperuser
   ```
   Follow the prompts to set an email and password. Then, run the development server:
   ```sh
    python manage.py runserver
   ```
    Navigate to localhost:8000/membership/manage-roles and add your superuser as an Exec. <br>
    If your change requires testing with a user that has lower privileges than an Exec, you can create their login on the website and activate their "Membership" with your Exec login.

## Development ##
For mode code changes, the web server will automatically restart to include the updated code. If you have to change anything in a `models.py` file, you will have to migrate the change to the database schema:
```sh
python manage.py makemigrations
python manage.py migrate
```
This will automatically generate a new file in the `migrations` folder of the app whose models you have updated. Ensure to include this file when you commit your change.

## Learn More ##
If you have not worked on a Django project before, understanding the [Model-View-Template architecture](https://docs.djangoproject.com/en/5.2/intro/overview/) will help clarify the file structure of this project
