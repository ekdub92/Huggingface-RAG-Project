# Python Packages
import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain.embeddings import HuggingFaceBgeEmbeddings

# Load vectorstore
# refer to 'save_vectorstore.py'
model_name = "BAAI/bge-large-en-v1.5"
model_kwargs = {'device': 'cpu'}
encode_kwargs = {"normalize_embeddings": True}

embedding_function = HuggingFaceBgeEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)

db = FAISS.load_local('faiss_store', embedding_function, allow_dangerous_deserialization=True)
num_k = 3

# Default streamlit settings
st.set_page_config(
    page_title="Search",
    page_icon="🔍"
)

st.header("Search")
st.subheader("Search what you are looking for")
st.write("Huggingface official document")

# Prompt and Answer using vector database
prompt = st.text_input("Question:","")

if st.button("Ask"):
    if prompt:
        matched_docs = db.similarity_search(query=prompt, k=num_k)
        for doc_ind in range(num_k):
            st.write(matched_docs[doc_ind].metadata['title'] + " [[link]](%s)" %matched_docs[doc_ind].metadata['source'])
            st.write(matched_docs[doc_ind].page_content)
            st.divider()
    else:
        st.warning("Please enter a question")