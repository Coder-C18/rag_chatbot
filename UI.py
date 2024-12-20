import time
import streamlit as st
import tempfile
import pandas as pd
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from qdrant_client.http.exceptions import UnexpectedResponse
from utils.vector_db import get_list_collection_names, delete_collection
from VectorStoreDB import load_docs_from_text
import os
from generate import  generate_answer


def stream_data(text):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.02)


def load_document(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=uploaded_file.name.split('.')[-1], dir='tmp') as tmp_file:

        tmp_file.write(uploaded_file.read())
        temp_file_path = tmp_file.name

        if uploaded_file.name.endswith(".pdf"):
            loader = PyPDFLoader(temp_file_path)
        elif uploaded_file.name.endswith(".docx"):
            loader = Docx2txtLoader(temp_file_path)
        else:
            st.error("Unsupported file type. Please upload a PDF or DOCX file.")

    documents = loader.load()

    text = ''.join(page.page_content for page in documents)
    os.remove(temp_file_path)
    return text


def show_content(text):
    st.text_area("Content", text, height=500)


# Tạo sidebar cho ứng dụng
st.sidebar.title("Menu")
page = st.sidebar.radio(" ", ["Document Manager", "Chat Bot"])

# Trang 2: Chat Bot
if page == "Chat Bot":

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("What is up?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        anwser = generate_answer(prompt)
        #
        # # Display assistant response in chat message container
        with st.chat_message("assistant"):
            response = st.write_stream(stream_data(text=anwser))
        # # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": "Hello there! How can I assist you today?"})


    # # st.title("Chat Bot")
    # user_input = st.chat_input("Say something")
    # st.chat_message("assistant").write('Chào bạn! Tôi có thể giúp gì cho bạn hôm nay? 😊')
    # if user_input:
    #     user = st.chat_message('user')
    #     message = st.chat_message("assistant")
    #     user.write(user_input)
    #     anwser = generate_answer(user_input)
    #     message.write_stream(stream_data(text=anwser))

# Trang 3: Database Viewer
elif page == "Document Manager":
    tab3, tab2 = st.tabs(["Insert Document", 'Document', ])

    with tab2:
        st.title("Document List")
        collection_names = get_list_collection_names()
        if collection_names:
            df = pd.DataFrame(collection_names)
            event = st.dataframe(data=df,
                                 on_select="rerun",
                                 selection_mode="multi-row",
                                 use_container_width=True,
                                 hide_index=True)

            remove_df = df.loc[event.selection.get('rows')][['name', 'id']]

            if not remove_df.empty:
                if st.button("Delete Document"):
                    with st.spinner('processing...'):
                        for _, row in remove_df.iterrows():
                            print(row)
                            delete_collection(row['name'], row['id'])
                        st.rerun()
    with tab3:
        st.title("Upload Document")
        uploaded_file = st.file_uploader("Tải lên file của bạn với định dạng pdf hoặc word:", type=["pdf", "docx"])
        if uploaded_file is not None:

            text = load_document(uploaded_file)
            description = st.text_input("Nhập mô tả cho tài liệu", placeholder='descript for document', )
            button1, button2 = st.columns(2)
            if button2.button("Insert to Database"):
                if description:
                    with st.spinner('processing...'):
                        try:

                            load_docs_from_text(text, uploaded_file.name, description)
                            st.success(" insert completed successfully!")
                            time.sleep(1)
                            st.rerun()
                        except UnexpectedResponse as e:
                            if e.status_code == 409:
                                st.error('⚠️ Document already exists!')
                            else:
                                st.error(e)

                else:
                    st.error("⚠️ Please enter a description!")

            if button1.button("show content"):
                show_content(text=text)
