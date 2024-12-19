# Email_fetch

# Email Fetcher

This project demonstrates how to fetch unread emails and mark them as read using the Gmail API. Follow the steps below to set up and run the code.

## Prerequisites

- Python installed on your machine.
- A Google Cloud Console account.
- Basic knowledge of APIs and OAuth.

---

## Steps to Set Up and Run the Project

### Step 1: Enable APIs for Your Project

To use the Gmail API, you must enable it in the Google API Console.

1. Open the [API Library](https://console.cloud.google.com/apis/library) in the Google API Console.
2. If prompted, select a project, or create a new one.
3. Use the search bar to find the Gmail API or click **View All** under "Google Workspace".
4. Select the Gmail API and click the **Enable** button.
5. If prompted, enable billing.
6. Read and accept the API's Terms of Service if required.

---

### Step 2: Create Authorization Credentials

To access the Gmail API, create OAuth 2.0 credentials for your project.

1. Go to the [Credentials page](https://console.cloud.google.com/apis/credentials).
2. Click **Create Credentials > OAuth client ID**.
3. Select the **Web Application** application type.
4. Fill in the form:
   - Add a name for your OAuth client.
   - Specify authorized redirect URIs. For testing, use: `http://localhost:8080`.
5. Click **Create** to generate the credentials.
6. Download the `client_secret.json` file and save it securely. Ensure the file is accessible to your application.

---

### Step 3: Clone the Repository

Clone this repository to your local machine:

```bash
git clone https://github.com/mitesharora22/Email_fetch.git
cd Email_fetch
```

---

### Step 4: Install Dependencies

Install the required Python libraries using `pip`:

```bash
pip install -r requirements.txt
```

---

### Step 5: Authenticate and Fetch Emails

1. Place the `client_secret.json` file in the root directory of the project.
2. Run the script to authenticate and fetch unread emails:

```bash
python fetch_emails.py
```

3. During the first run, a browser window will open prompting you to log in to your Google account and grant the necessary permissions.
4. After successful authentication, the script will fetch unread emails and mark them as read.

---

### Step 6: View Results

Check the console output for details of fetched emails. The script will automatically mark them as read in your Gmail inbox.

---

## Troubleshooting

- Ensure the `client_secret.json` file is correctly placed and matches the credentials generated in the Google Cloud Console.
- Check your Python version and installed dependencies.
- Verify that the Gmail API is enabled for your project in the Google API Console.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Contributing

Feel free to submit issues and pull requests for improvements or bug fixes.
