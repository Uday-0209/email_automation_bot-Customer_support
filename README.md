# email_automation_bot-Customer_support
This repository contains three applications: a local system service program, a Streamlit-based conversational bot powered by Gemini LLM, and a RAG-enabled model for knowledge retrieval and response generation. Together, they showcase multiple AI interaction workflows.
<h2 align="center">🚀 AI Project Suite – Three Major Applications</h2>

<p align="center">
This repository contains <b>three independent AI applications</b>, each developed with a specialized workflow, model, and deployment flow.  
They are organized into three separate folders within this repository.
</p>

<hr>

<h3>🟢 1️⃣ Systemd Backend Service – Email Automation (Llama 3.8 / 7B)</h3>

<p>
Runs as a <b>Linux systemd service</b> working in the background. It loads a local <b>Llama 3.8 7B model</b> and performs automated email resolution:
</p>

<ul>
  <li>Fetches and checks incoming emails via Google API</li>
  <li>Extracts issue_id from email subject/body</li>
  <li>Retrieves the corresponding record from local dataset</li>
  <li>Pushes issue + solution to LLM for final formatting</li>
  <li>LLM generates reply email</li>
  <li>Return email sent back automatically to customer</li>
</ul>

<p><b>No cloud dependency – runs fully offline as systemd background service.</b></p>

<div align="center">
<pre>
[ Email ] → [ Llama Model ] → [ Generated Reply ] → [ Customer ]
</pre>
</div>

<hr>

<h3>🔵 2️⃣ Streamlit + Gemini 2.5 Flash – Cloud Hosted</h3>

<p>
Developed as a <b>Streamlit chatbot frontend</b>, powered by <b>Gemini 2.5 Flash</b>.  
Model containerized → Docker Image → hosted on <b>AWS EC2 + ECS</b>.
</p>

<ul>
  <li>Interactive web interface for issue solving</li>
  <li>Docker-based deployment</li>
  <li>Runs on AWS ECS container cluster</li>
  <li>Fast inference with Gemini Flash</li>
</ul>

<div align="center">
<pre>
User → Streamlit UI → Gemini 2.5 Flash → Response
      (Docker + AWS ECS Hosting)
</pre>
</div>

<hr>

<h3>🟣 3️⃣ RAG Powered Streamlit Model – Hybrid Retrieval + LLM</h3>

<p>
A <b>Retrieval Augmented Generation (RAG)</b> based solution:
</p>

<ul>
  <li>Uses vector search + issue lookup</li>
  <li>Extracts issue data based on ID</li>
  <li>Embeds + retrieves context from vectordb</li>
  <li>Sends combined context to LLM for rich output</li>
  <li>Supports both containerized AWS deployment & offline mode</li>
</ul>

<div align="center">
<pre>
Issue No → Dataset Lookup
        → RAG Vector Search
        → Combined Output → LLM → Result
</pre>
</div>

<p align="center"><b>Streamlit UI + Docker deployment + Offline capability.</b></p>

<hr>

<h2 align="center">📁 Repository Structure Overview</h2>

<div align="center">
<pre>
root/
 ├── systemd_service_llama/
 ├── streamlit_gemini_docker/
 └── rag_streamlit_docker/
</pre>
</div>

<hr>

<h2 align="center">📊 Architecture Visual Summary</h2>

<table>
<tr>
<td align="center"><b>Service Type</b></td>
<td align="center"><b>Model</b></td>
<td align="center"><b>Interface</b></td>
<td align="center"><b>Deployment</b></td>
</tr>

<tr>
<td>Local Systemd Backend</td>
<td>Llama 3.8 7B</td>
<td>Automation (No UI)</td>
<td>On-prem Linux</td>
</tr>

<tr>
<td>Cloud Bot</td>
<td>Gemini-2.5 Flash</td>
<td>Streamlit</td>
<td>AWS ECS + EC2</td>
</tr>

<tr>
<td>RAG Solution</td>
<td>Local + Cloud Models</td>
<td>Streamlit</td>
<td>AWS EC2 + Offline</td>
</tr>
</table>

<hr>

<h2 align="center">⭐ Technology Highlights</h2>

<ul>
  <li><b>LLM Engines:</b> Llama-3.8 7B, Gemini-2.5 Flash</li>
  <li><b>Frameworks:</b> Systemd, Docker, RAG, Streamlit</li>
  <li><b>Cloud:</b> AWS EC2 + ECS Container Hosting</li>
  <li><b>Backend Logic:</b> Automated email issue processing</li>
  <li><b>Offline + Cloud Hybrid AI architecture</b></li>
</ul>

<p align="center"><b>These three projects demonstrate end-to-end intelligent automation from emails → LLM → customer response.</b></p>
