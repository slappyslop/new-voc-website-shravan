# new-voc-website
## Developer Setup ##
1. Fork and clone this repository
2. Create a Python virtual environment using venv. The specific instructions are different depending on your operating system, and can be found [here](https://docs.python.org/3/library/venv.html)
3. With the virtual environment activated, install dependencies
    ```
    pip install -r requirements.txt
    ```
4. Run the server
    ```sh
    cd src/ubc_voc_website
    python manage.py runserver
    ```

## Development ##
For mode code changes, the web server will automatically restart to include the updated code. If you have to change anything in a `models.py` file, you will have to migrate the change to the database schema:
```sh
python manage.py makemigrations
python manage.py migrate
```
This will automatically generate a new file in the `migrations` folder of the app whose models you have updated. Ensure to include this file when you commit your change.

## Learn More ##
If you have not worked on a Django project before, understanding the [Model-View-Template architecture](https://docs.djangoproject.com/en/5.2/intro/overview/) will help clarify the file structure of this project
