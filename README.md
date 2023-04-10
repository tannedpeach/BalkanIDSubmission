Modules to install and import:
PostgreSQL
Flask
Furl
psycopg2
Requests
import io 
import csv
import json
from github import Github

How to run:
1. Clone this repository
2. In VSCode, open this project and create a Python environment by selecting View -> Command Palette -> Python: Create Environment. Next, open a new terminal by selecting View -> Command Palette -> Terminal: Create New Terminal. 
3. Create an OAuth app in github. Set the Homepage URL to http://127.0.0.1:5000, and Authorization callback URL to http://127.0.0.1:5000/oauth2/github/callback.
2. In app.py, enter your Client ID and Client Secret for OAuth authentication.
3. For connection to Postgres database, enter your username, password, host (usually 127.0.0.1), port (5432) and database name.
4. In the terminal, run the command python -m flask run. 
5. Finally, open the index.html page in a chrome tab and click on the 'Download CSV' button.