client_id = '9d12427a09038c2bb406'
client_secret = 'f610ca435a754cd7271b0c578c8adc3a40ff45ba'
from flask import Flask, redirect, jsonify, Response
from furl import furl
import psycopg2
from psycopg2 import Error
import requests
import io 
import csv
import json
from flask import request
from github import Github

app = Flask(__name__)

# user authentication
@app.route('/', methods=['GET', 'POST'])
def index():
    url = 'https://github.com/login/oauth/authorize'
    params = {
        'client_id': client_id,
        'scope': 'repo read:user', #set scope so that both private and pblic repos can be fetched
        'state': 'random string.',
        'allow_signup': 'true'    
    }
    url = furl(url).set(params)
    return redirect(str(url), 302)


@app.route('/oauth2/<service>/callback')
def oauth2_callback(service):

    code = request.args.get('code')
    access_token_url = 'https://github.com/login/oauth/access_token'
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': code,
        'state': 'random string.',
        'scope': 'repo read:user'
    }
    r = requests.post(access_token_url, json=payload, headers={'Accept': 'application/json'})
    access_token = json.loads(r.text).get('access_token')
    print(access_token)

    g = Github(access_token)
    
    repo_list = []
    repo_idarr = []
    repo_status = []
    repo_stars = []

    # fetch owner_id, owner_name, owner_email, repo_id, repo_name, status, stars_count using PyGitHub
    for repo in g.get_user().get_repos(visibility="all"):
        repo_list.append(repo.name)

    for repo in g.get_user().get_repos(visibility="all"):
        repo_idarr.append(str(repo.id))

    for repo in g.get_user().get_repos(visibility="all"):
        if repo.private == True:
            repo_status.append("Private")
        else:
            repo_status.append("Public")
    
    for repo in g.get_user().get_repos(visibility="all"):
        repo_stars.append(repo.stargazers_count)
    
    normalized_data = []
    i = 0
    for repo in repo_list:
    
        owner_id = g.get_user().id
        owner_name = g.get_user().login
        owner_email = g.get_user().email
        repo_id = repo_idarr[i]
        repo_name = repo_list[i]
        status = repo_status[i]
        stars_count = repo_stars[i]

        # ensuring no duplicates based on repo id (did not include owner id field as one owner will have multiple repos)
        if repo_id not in normalized_data:
            normalized_data.append((owner_id, owner_name, owner_email, repo_id, repo_name, status, stars_count))

        i+=1
        
    # insert data into postgres table
    try:
        connection = psycopg2.connect(user="postgres",
                                    password="tanisha",
                                    host="127.0.0.1",
                                    port="5432",
                                    database="balkan")

        cursor = connection.cursor()
        create_table_query = '''CREATE TABLE git_repo
            (Owner_ID TEXT NOT NULL,
            Owner_name TEXT NOT NULL,
            Owner_email TEXT,
            Repo_ID TEXT UNIQUE,
            Repo_name TEXT,
            Status TEXT,
            Stars_count INT); '''   

        cursor.execute(create_table_query)
        connection.commit()
        print("Table created successfully in PostgreSQL ")

        for item in normalized_data:
            data = (item[0], item[1], item[2], item[3], item[4], item[5], item[6])
            query =  "INSERT INTO git_repo (Owner_ID, Owner_name, Owner_email, Repo_ID, Repo_name, Status, Stars_count) VALUES (%s, %s, %s, %s, %s, %s, %s);"
            cursor.execute(query, data)
            connection.commit()

    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)

    cursor.execute("Select * from git_repo")
    result = cursor.fetchall()  
    output = io.StringIO()
    writer = csv.writer(output)

    line = ['Owner_ID', 'Owner_name', 'Owner_email', 'Repo_ID', 'Repo_name', 'Status', 'Stars_count']
    writer.writerow(line)

    for row in result:
        for r in row:
            r = str(r)
            print(r)
        writer.writerow(row)

    output.seek(0)

    # downloadable .CSV file
    return Response(output, mimetype="text/csv",
                        headers={"Content-Disposition": "attachment;filename=repodata.csv"})