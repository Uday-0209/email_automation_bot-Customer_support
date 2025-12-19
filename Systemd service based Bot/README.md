<h1 align="center">📧 Automated Email Support System – Systemd LLM Service</h1>

<p align="center">
This project contains three Python modules running together to form a self-reliant AI-powered email response automation engine.  
It continuously reads unread emails, identifies issue numbers, generates LLM-driven replies, and sends responses back to customers — all running as a Linux <b>systemd</b> service.
</p>

<hr>

<h2>🟢 Project Components</h2>

<ul>
<li><b>email_reader.py</b> → Reads new Gmail messages, extracts issue number, filters spam, triggers generation engine.</li>
<li><b>reply_generator.py</b> → LLM + dataset driven response builder using Ollama + local llama model.</li>
<li><b>email_generator.py</b> → Sends final email response to customer automatically using Gmail API.</li>
</ul>

<hr>

<h2>🧩 System Architecture Overview</h2>

<pre align="center">
[Gmail Inbox] → email_reader.py → reply_generator.py → email_generator.py → [Customer Reply Sent]
</pre>

<hr>

<h2>⚙️ Running as a Linux Systemd Background Service</h2>
<p>
The application stays active permanently on Linux using systemd.  
It restarts on reboot and runs without supervision.
</p>

<hr>

<h2>📌 Gmail API Credential Setup Guide</h2>

<p>
Before running the scripts, you must generate three secure authentication files:
<b>credentials.json</b>, <b>token_read.json</b>, and <b>token_send.json</b>.  
These files allow your Python code to read and send emails through Gmail API.
</p>

<hr>

<h3>✔️ Step 1: Create Google Cloud Project</h3>

<ol>
<li>Go to: https://console.cloud.google.com/</li>
<li>Create a new project → name it anything like "Email Automation"</li>
<li>Enable the Gmail API inside this project</li>
</ol>

<hr>

<h3>✔️ Step 2: Generate <code>credentials.json</code></h3>

<ol>
<li>Inside your Google Cloud Gmail API project, open the <b>Credentials</b> page</li>
<li>Click:
<br>
<b>Create Credentials → OAuth Client ID</b>
</li>
<li>Select
<ul>
<li><b>Desktop Application</b> as app type</li>
</ul>
</li>
<li>Download the JSON file</li>
<li>Rename it to:
<pre>credentials.json</pre>
</li>
<li>Place it inside your project folder path</li>
</ol>

<p>
This file stores your client secret and OAuth redirect IDs. It is needed only once to generate tokens.
</p>

<hr>

<h3>✔️ Step 3: First Run Generates <code>token_read.json</code></h3>

<p>
The script <b>email_reader.py</b> automatically generates the read token when executed.
</p>

<ol>
<li>Run:
<pre>python3 email_reader.py</pre>
</li>
<li>A Google login page will open</li>
<li>Sign-in using the Gmail account that should be monitored</li>
<li>Approve permission: "Read Gmail inbox"</li>
<li>Upon success, a new file will be created:
<pre>token_read.json</pre>
</li>
</ol>

<p>
This file allows the script to continuously read Gmail inbox without needing login again.
</p>

<hr>

<h3>✔️ Step 4: Generate <code>token_send.json</code></h3>

<p>
To send emails back from the same Gmail ID, you must also authorize Gmail Sending scope.
</p>

<ol>
<li>Open <b>email_reader.py</b> and ensure SCOPES_send is enabled (it already is).</li>
<li>Run:
<pre>python3 email_reader.py</pre>
</li>
<li>Second login window opens requesting:
"Send email permission"</li>
<li>After approval, file will be stored as:
<pre>token_send.json</pre>
</li>
</ol>

<p>
Once created, sending email through Gmail becomes fully automated.
</p>

<hr>

<h3>📁 Token File Purpose Summary</h3>

<table>
<tr><th>File Name</th><th>Purpose</th></tr>
<tr><td>credentials.json</td><td>Google OAuth credential file downloaded from Google Cloud</td></tr>
<tr><td>token_read.json</td><td>Stores OAuth token allowing script to read inbox</td></tr>
<tr><td>token_send.json</td><td>Stores OAuth token allowing script to send emails</td></tr>
</table>

<hr>

<h3>⚠️ Security Warning</h3>

<p>
Never push <b>credentials.json</b> or token files to public GitHub repositories.  
These contain authentication metadata that can expose your Gmail account.
</p>

<hr>

<h2>🚀 Personal Setup Instructions</h2>

<ol>
<li>Install Python 3 and required libraries (google-api-python-client, oauthlib, pandas, ollama).</li>
<li>Download llama model using Ollama CLI.</li>
<li>Place dataset file <code>possible_error.json</code> in working directory.</li>
<li>Run the script once to generate tokens.</li>
<li>Create <code>.service</code> systemd file pointing to python execution.</li>
<li>Enable service:
<pre>sudo systemctl enable email_service</pre>
</li>
<li>Start service:
<pre>sudo systemctl start email_service</pre>
</li>
</ol>

<hr>

<h2 align="center">🎯 Final Outcome</h2>
<p align="center">
Your system becomes an automated email support engine:  
It reads customer emails → identifies issue → generates LLM-based replies → and responds automatically — running 24/7.
</p>

