import streamlit as st

st.set_page_config(
    page_title="Search",
    page_icon="🔍"
)

st.header("Search")
st.subheader("Search what you are looking for")
st.write("Huggingface official document")

prompt = st.text_input("Question:","")

if st.button("Ask"):
    if prompt:
        generated_text="Answer"
        st.write(generated_text)
    else:
        st.warning("Please enter a question")