import os
import flask
import requests
import sqldatabase
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import sqlite3
# File containing OAuth 2.0 client ID and secret
CLIENT_SECRETS_FILE = "cred.json"

# OAuth 2.0 Scopes
# SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
API_SERVICE_NAME = 'gmail'
API_VERSION = 'v1'

# Flask app configuration
app = flask.Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xeb]/'  

@app.route('/')
def index():
    return print_index_table()

@app.route('/gmail')
def gmail_api_request():
    if 'credentials' not in flask.session:
        return flask.redirect('/authorize')

    features = flask.session.get('features', {})

    if features.get('gmail'):
        # Load credentials from the session
        credentials = google.oauth2.credentials.Credentials(
            **flask.session['credentials'])

        gmail = googleapiclient.discovery.build(
            API_SERVICE_NAME, API_VERSION, credentials=credentials)

        # Fetch unread messages using `q` parameter
        results = gmail.users().messages().list(userId='me', q='is:unread').execute()
        messages = results.get('messages', [])

        emails = []  # Collect email data for database storage

        # Iterate over messages and fetch their details
        for msg in messages:
            message_id = msg['id']
            message = gmail.users().messages().get(userId='me', id=message_id, format='metadata').execute()
            headers = {header['name']: header['value'] for header in message['payload']['headers']}
            emails.append({'headers': headers})  # Append the parsed headers

            # Mark the message as read by removing the UNREAD label
            gmail.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()

        # Handle pagination if there's a nextPageToken
        while 'nextPageToken' in results:
            next_page_token = results['nextPageToken']
            results = gmail.users().messages().list(userId='me', q='is:unread', pageToken=next_page_token).execute()
            messages = results.get('messages', [])

            for msg in messages:
                message_id = msg['id']
                message = gmail.users().messages().get(userId='me', id=message_id, format='metadata').execute()
                headers = {header['name']: header['value'] for header in message['payload']['headers']}
                emails.append({'headers': headers})  # Append the parsed headers

                # Mark the message as read by removing the UNREAD label
                gmail.users().messages().modify(
                    userId='me',
                    id=message_id,
                    body={'removeLabelIds': ['UNREAD']}
                ).execute()

        # Save emails to the SQLite database using the `sqldatabase` script
        sqldatabase.initialize_database()  # Ensure the database is initialized
        sqldatabase.parse_and_store_emails(emails)

        # Save credentials back to session in case access token was refreshed
        flask.session['credentials'] = credentials_to_dict(credentials)

        return '<p>Unread emails fetched, processed, and stored in the database successfully.</p>'
    else:
        return '<p>Gmail feature is not enabled.</p>'

@app.route('/authorize')
def authorize():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES
    )
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        access_type='offline',  # Request offline access
        include_granted_scopes='true'
    )

    flask.session['state'] = state
    return flask.redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    state = flask.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    # Fetch OAuth 2.0 tokens
    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials in the session
    credentials = flow.credentials
    flask.session['credentials'] = credentials_to_dict(credentials)

    # Check granted scopes
    features = check_granted_scopes(credentials)
    flask.session['features'] = features

    return flask.redirect('/')

@app.route('/revoke')
def revoke():
    if 'credentials' not in flask.session:
        return ('You need to <a href="/authorize">authorize</a> before ' +
                'testing the code to revoke credentials.')

    credentials = google.oauth2.credentials.Credentials(
        **flask.session['credentials'])

    revoke = requests.post('https://oauth2.googleapis.com/revoke',
                           params={'token': credentials.token},
                           headers={'content-type': 'application/x-www-form-urlencoded'})

    if revoke.status_code == 200:
        return 'Credentials successfully revoked.' + print_index_table()
    else:
        return 'An error occurred.' + print_index_table()

@app.route('/clear')
def clear_credentials():
    if 'credentials' in flask.session:
        del flask.session['credentials']
    return 'Credentials have been cleared.<br><br>' + print_index_table()

def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

def check_granted_scopes(credentials):
    features = {}
    if 'https://www.googleapis.com/auth/gmail.modify' in credentials.scopes:
        features['gmail'] = True
    else:
        features['gmail'] = False
    return features

def print_index_table():
    return ('<table>' +
            '<tr><td><a href="/gmail">Test Gmail API request</a></td>' +
            '<td>Submit an API request to list Gmail messages and see a JSON response.</td></tr>' +
            '<tr><td><a href="/authorize">Authorize</a></td>' +
            '<td>Go to the authorization flow. If there are stored credentials, reauthorization may not be needed.</td></tr>' +
            '<tr><td><a href="/revoke">Revoke credentials</a></td>' +
            '<td>Revoke the access token associated with the current session.</td></tr>' +
            '<tr><td><a href="/clear">Clear credentials</a></td>' +
            '<td>Clear the access token currently stored in the session.</td></tr>' +
            '</table>')


@app.route('/view-emails')
def view_emails():
    conn = sqlite3.connect('emails.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, sender, subject, timestamp FROM Emails')
    emails = cursor.fetchall()
    conn.close()

    # Create a simple HTML table for display
    table = '<table border="1">'
    table += '<tr><th>ID</th><th>Sender</th><th>Subject</th><th>Timestamp</th></tr>'
    for email in emails:
        table += f'<tr><td>{email[0]}</td><td>{email[1]}</td><td>{email[2]}</td><td>{email[3]}</td></tr>'
    table += '</table>'
    return table



if __name__ == '__main__':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
    app.run('localhost', 8080, debug=True)
