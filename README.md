# Hybrid RAG app for Financial Intelligence

### 🔥 **Overview**
The **Financial Intelligence Hub** is a comprehensive RAG-based (Retrieval-Augmented Generation) application designed to **enhance financial knowledge accessibility**.  

---

### **🌟 Features**
- 🔎 **Hybrid RAG Retrieval**:  
    - Combines **SQL filtering** with **Pinecone vector search** for **accurate glossary retrieval**.
- 🔥 **Reranking**:  
    - Improves result relevance by **reranking using SQL boosting** and **cosine similarity**.  
- 🛠️ **Efficient Vector Search with Pinecone**:  
    - Stores financial glossary embeddings in **Pinecone** for fast and scalable retrieval. 
- ⚙️ **RESTful APIs with FastAPI**:  
    - Exposes clean and modular **APIs for glossary retrieval and management**.  

---

### **🛠️ Tech Stack**
#### ✅ **Languages & Frameworks**
- **Python** → Main programming language.
- **FastAPI** → For building RESTful APIs.
- **SQLAlchemy** → ORM for PostgreSQL integration.

#### ✅ **Database & Vector Search**
- **PostgreSQL** → Metadata store for glossary terms.  
- **Pinecone** → Vector database for **semantic search**.  

#### ✅ **Embedding Models**
- **OpenAI Embeddings** → For Pinecone vector insertion.

---

### **💡 How It Works**
**Flow Diagram:**
![Flow Diagram](Fin-RAG.png)

---

### **🔧 How to Run**
1️⃣ **Clone the repository:**
```bash
git clone https://github.com/your-username/financial-intelligence-hub.git
cd financial-intelligence-hub
```

2️⃣ **Set up environment variables:**
Create a .env file with the following details:
```bash
PINECONE_API_KEY=<YOUR_PINECONE_KEY>  
PINECONE_INDEX_NAME=<YOUR_INDEX_NAME> 
PINCONE_ENV=<YOUR_PINECONE_REGION>

PG_USER=""
PG_PASSWORD=""
PG_HOST=""
PG_PORT=5432
GLOSSARY_DB=glossary

OPENAI_API_KEY=<YOUR_OPENAI_KEY>
```

3️⃣ **Install dependencies:**
```bash
pip install -r requirements.txt
```

4️⃣ **Run the PostgreSQL query:**
```sql
CREATE TABLE glossary (
	id uuid DEFAULT gen_random_uuid() NOT NULL,
	term text NOT NULL,
	definition text NOT NULL,
	simplified_explanation text NULL,
	contextual_examples jsonb NULL,
	created_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
	updated_at timestamp DEFAULT CURRENT_TIMESTAMP NOT NULL,
	deleted_at timestamp NULL,
	embedded bool NULL
);
```

5️⃣ **Run:**
```bash
python main.py
```