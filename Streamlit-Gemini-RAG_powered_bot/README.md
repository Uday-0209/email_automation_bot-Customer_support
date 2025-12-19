<h1 align="center">🟣 RAG Powered Email Automation – Chroma VectorDB + Gemini</h1>

<p align="center">
This project implements a Retrieval Augmented Generation (RAG) based email support system
where incoming email content is processed, relevant knowledge is extracted from a local
vector database built using <b>Chroma + HuggingFace embeddings</b>, merged with structured
dataset lookups, and sent to <b>Gemini LLM</b> for final email response creation.
</p>

<hr>

<h2>📌 What makes this version different?</h2>

<p>
Unlike previous projects, this solution uses a <b>Vector Database</b> to retrieve deep contextual
knowledge. This allows the model to use historical solution data, device texts,
and support recordings beyond static dataset matching.
</p>

<ul>
<li>Uses <b>Chroma Vector store</b> – no chunking required</li>
<li>Embeddings stored once and persisted locally</li>
<li>Query performed on live email body input</li>
<li>Vector search output + dataset lookup combined</li>
<li>Gemini generates email using both knowledge layers</li>
</ul>

<hr>

<h2>🧠 Core Component – gemini_llm_response.py</h2>

<p>
The core RAG logic resides inside <code>generate_email()</code> where the email body is semantically
searched against the Chroma embedding database. This retrieves the most relevant text samples 
related to the user query.  
Dataset extraction (issue number → issue → solution → device) is also included for additional structure.
</p>

<p>
Here are the major steps taken inside the function: :contentReference[oaicite:0]{index=0}
</p>

<ol>
<li>Load issue & solution from <code>mtcm_intellipod.json</code>.</li>
<li>Load HuggingFace embedding model: 
<pre>sentence-transformers/all-mpnet-base-v2</pre>
</li>
<li>Initialize Chroma vector store:
<pre>persist_directory="./chroma_langchain_db2"</pre>
</li>
<li>Perform similarity search:
<pre>vectordb.similarity_search(body, k=2)</pre>
</li>
<li>Combine:
<b>structured dataset</b> + <b>vector extraction</b></li>
<li>Build prompt with template + tech context</li>
<li>Generate email using:
<pre>Gemini 2.5 Flash</pre></li>
</ol>

<hr>

<h2>📦 High-level Architecture</h2>

<pre align="center">
Incoming Email Body
       │
       ▼
Chroma VectorDB  ←  Embedding Model (MPNet-base)
       │
       ▼ 
RAG Combined Context (device + issue + solution + vectors)
       │
       ▼
Gemini LLM Email Response
       │
       ▼
Automated Customer Reply
</pre>

<hr>

<h2>🟢 Why no chunking?</h2>

<p>
Since this implementation works with well-structured device level JSON data
and direct email body queries, chunking is not required.
Embeddings are directly created from existing solution/knowledge files.
</p>

<p>
This leads to:
</p>

<ul>
<li>Faster indexing pipeline</li>
<li>Lower complexity</li>
<li>Direct semantic matching</li>
<li>Better accuracy on issue-based lookups</li>
</ul>

<hr>

<h2>📁 Files Required</h2>

<ul>
<li><code>mtcm_intellipod.json</code> – primary issue/solution dataset</li>
<li><code>chroma_langchain_db2/</code> – persistent vector storage</li>
<li><code>credentials.json</code> – Gmail OAuth client file</li>
<li><code>token_read.json</code> – inbox read permission</li>
<li><code>token_send.json</code> – sending email permission</li>
</ul>

<hr>

<h2>💡 How the RAG query works</h2>

<pre>
vector_extract = vectordb.similarity_search(body, k = 2)
</pre>

<p>
The body text of each incoming email is used as the search query.
The top-2 semantic matches are returned → inserted into the LLM prompt.
</p>

<p>
Final AI email includes:
</p>

<ul>
<li>exact device context</li>
<li>recommended solution</li>
<li>vector knowledge references</li>
<li>structured issue mapping</li>
</ul>

<hr>

<h2>🎯 Gemini Prompt Strategy</h2>

<p>
Prompt dynamically changes:
</p>

<ul>
<li>If dataset match found → include issue + solution + device fields</li>
<li>If dataset match missing → rely entirely on vector knowledge extraction</li>
</ul>

<pre>
If issue known:
"issue number, issue, solution, device + vector_extract"
Else:
"only vector_extract"
</pre>

<hr>

<h2>📦 Deployment Structure</h2>

<p>This RAG model supports the same deployment pattern as Gemini container version:</p>

<ul>
<li>Docker image build</li>
<li>Upload to AWS ECR</li>
<li>Run container on AWS EC2</li>
<li>Expose Streamlit UI for email triggers</li>
<li>Offline vector search supported</li>
</ul>

<hr>

<h2>🛠 Setup Notes</h2>

<ol>
<li>Generate embeddings & persist into <code>chroma_langchain_db2</code></li>
<li>Add JSON dataset file</li>
<li>Provide Gmail tokens</li>
<li>Store vector DB directory inside container or mounted volume</li>
<li>Open Streamlit interface</li>
</ol>

<hr>

<h2>🌐 Docker + AWS Deployment (quick)</h2>

<pre>
docker build -t rag-support-app .
docker run -p 8502:8501 rag-support-app
</pre>

<p>Then:</p>

<pre>
aws ecr create-repository rag-support-app
docker tag → push → pull → launch container on EC2
</pre>

<hr>

<h2 align="center">🚀 Final Outcome</h2>

<p align="center">
This RAG application significantly improves troubleshooting accuracy by blending:
<b>structured dataset lookup + vector intelligence + Gemini LLM</b>
to produce rich email responses that outperform plain dataset-only models.
</p>

