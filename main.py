import streamlit as st
from pymongo import MongoClient
from urllib.parse import quote_plus

# Replace 'your_username' and 'your_password' with your actual username and password
username = st.secrets['username']
password = st.secrets['password']

escaped_username = quote_plus(username)
escaped_password = quote_plus(password)


connection_string = f"mongodb+srv://{escaped_username}:{escaped_password}@cluster0.g5mlgod.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

cluster = MongoClient(connection_string)

db = cluster['Freshmanfaqs']
collection = db['q&a']
def page1():

    from openai import OpenAI

    st.title("Sreenidhi Freshman FAQS")

    client = OpenAI(api_key=st.secrets['apikey'])

    pre_prompt = 'You are an expert in Sreenidhi college hyderabad and your job is to answer  questions about Sreenidhi college Hyderabad. Assume that all questions are related to the college. Keep your answers technical and based on facts – do not hallucinate features. If you don\'t know the answer for that question about the college, reply with "I am sorry, I do not know the answer to your question. Your question is added to the community forum. Please check there." If the question is not related to the college, reply with "I am sorry; I can only assist you with questions related to the college."'

    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-3.5-turbo"

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": pre_prompt}]

    if "unanswered" not in st.session_state:
        st.session_state.unanswered = set()  # Using a set to keep track of unique questions

    for message in st.session_state.messages:
        if message['role'] != 'system':
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if prompt := st.chat_input("Welcome to SNIST Chatbot!"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            response = st.write_stream(stream)

            # Check if the response includes the specific apology message
            apology_message = "I am sorry, I do not know the answer to your question. Your question is added to the community forum. Please check there."
            if apology_message in response:
                if prompt not in st.session_state.unanswered:
                    st.session_state.unanswered.add(prompt)

        st.session_state.messages.append({"role": "assistant", "content": response})

    # Display unanswered questions
    def add_question_to_mongodb(question):
        # Check if the question already exists in the database
        existing_question = collection.find_one({"question": question})

        if not existing_question:
            # If the question doesn't exist, insert it into the database
            collection.insert_one({"question": question})

        else:
            pass


    if st.session_state.unanswered:
        for idx, question in enumerate(st.session_state.unanswered, start=1):
            user_question = question
            add_question_to_mongodb(user_question)



def page2():
    st.title("Page 2")
    st.write("This is the content of Page 2.")

    def display_question_answer(question, answer):
        st.markdown(f"**Question:** {question}")
        st.write(f"**Answer:** {answer}")
        st.markdown("---")

    def main():
        st.title("Sreenidhi Freshman FAQS")

        st.header("Questions with Answers:")
        answered_questions = collection.find({"question": {"$exists": True}, "answer": {"$exists": True}})
        for doc in answered_questions:
            display_question_answer(doc["question"], doc["answer"])

        st.header("Unanswered Questions:")
        unanswered_questions = collection.find({"question": {"$exists": True}, "answer": {"$exists": False}})
        for doc in unanswered_questions:
            st.markdown(f"**Unanswered Question:** {doc['question']}")
            st.markdown("---")

    if __name__ == "__main__":
        main()


def main():
    st.sidebar.title("Welcome")
    selected_page = st.sidebar.radio("Select a page", ["Home", "Community Forum"])

    if selected_page == "Home":
        page1()
    elif selected_page == "Community Forum":
        page2()

if __name__ == "__main__":
    main()
