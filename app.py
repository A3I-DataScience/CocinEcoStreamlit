import streamlit as st
import datetime

import io 
from profiles import predefined_profiles

from supported_countries import supported_countries
from RAG_agent_definition import init_llm
from RAG_agent_definition import init_conversational_rag_chain
from RAG_agent_definition import init_chroma_vector_store
from agents_profiles import all_in_one_agent
# Initialize LLM and embeddings

def process_new_profile():

    reset_chat_history()

    st.session_state.llm = init_llm(temperature = st.session_state.temperature,
                    llm_model = "gpt-4o-mini")
    st.session_state.vector_store_from_client = init_chroma_vector_store(embedding_model=st.session_state.embedding_model_name ,
                                                                             chunk_size= st.session_state.chunk_size,
                                                                                collection_name = st.session_state.agent_profile['collection_name'],
                                                                                folders = st.session_state.agent_profile['folders'],)
        
    st.session_state.conversational_rag_chain = init_conversational_rag_chain(vector_store = st.session_state.vector_store_from_client,
                                                                                  llm = st.session_state.llm,
                                        qa_prompt_generation_function = st.session_state.agent_profile['qa_prompt_generation_function'])



# Process User Prompt
def process_prompt(prompt):

    output = st.session_state.conversational_rag_chain.invoke(
        {"input": prompt},
        config={"configurable": {"session_id": "abc123"}},
    )
    answer = output["answer"]

    st.session_state.chat_history.append((prompt, answer))
    return answer


def send_meal_plan(answer):
    # Generate a filename with the current timestamp
    
    file_name = f"Meal-Plan_{datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')}.csv"

    # Extract the CSV content from the answer
    csv_content = answer.split("```")[1]

    # Prepare the CSV file content (you can customize this logic)
    # Convert the CSV string into a binary stream for download
    file_buffer = io.StringIO(csv_content)

    # Replace the placeholder message with a user-friendly message
    answer = answer.replace(
        answer.split("```")[1],
        "Get ready to nourish your body! Your customized Meal Plan, blending sustainability, nutrition, and your unique health needs is now downloadable.",
    )
    answer = answer.replace("```", "")

    # Show the answer text in the app
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.chat_message("assistant").write(answer)
    # Add a download button
    st.download_button(
        label="Download Meal Plan",
        data=file_buffer.getvalue(),
        file_name=file_name,
        mime="text/csv"
    )

def reset_chat_history():
    st.session_state.chat_history = []
def update_fields_with_profile(profile_data):
    st.session_state.gender = profile_data["gender"]
    st.session_state.age = profile_data["age"]
    st.session_state.height = profile_data["size"]
    st.session_state.weight = profile_data["weight"]
    st.session_state.country = profile_data["country"]
    process_new_profile()

def initialize_frontend():
    st.sidebar.selectbox(
        "Select Profile", 
        list(predefined_profiles.keys()),
        on_change=lambda: update_fields_with_profile(predefined_profiles[st.session_state.profile_choice]),
        index=None,
        key="profile_choice")
    
    st.sidebar.selectbox(
        "Gender",
        ["male", "female"],
        on_change=process_new_profile,
        key='gender'
    )
    st.sidebar.number_input(
        "Select Your Age",
        min_value=10,
        max_value=100,
        step=1,
        on_change=process_new_profile,
        key='age'
    )
    st.sidebar.number_input(
        "Select Your Height (cm)",
        min_value=120,
        max_value=210,
        step=1,
        on_change=process_new_profile,
        key='height'
    )

    st.sidebar.number_input(
        "Enter Your Weight (kg)",
        min_value=20,  # Minimum weight
        max_value=300,  # Maximum weight
        step=1,
        on_change=process_new_profile,
        key='weight'
    )

    st.sidebar.selectbox(
        "Select Your Country", 
        supported_countries, 
        on_change=process_new_profile,
        key='country'
        )
        
    st.title("CocinEco by A3I-Data Science")
    st.sidebar.empty()


def initialize_chatbot():
# Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if "bot_initialized" not in st.session_state:
        st.session_state.bot_initialized = False

    if not st.session_state.bot_initialized:
        # Global Variables stored in st.session_state
        st.session_state.llm = None
        st.session_state.embeddings = None
        st.session_state.chunk_size = 1000
        st.session_state.embedding_model_name = "text-embedding-3-small"
        st.session_state.temperature = 0.2
        st.session_state.vector_store_from_client = None
        st.session_state.conversational_rag_chain = None
        st.session_state.chat_history = []
        st.session_state.agent_profile = all_in_one_agent
        
        chat_message = ("Hello there! I'm CocinEco: an AI assistant that will help you elaborate sustainable meal plans."
                        + "I will ask you a few questions to understand you better and provide"
                        + "you with personalized nutrition advice. Let's get started! ok?")

        # Initialize chatbot
        st.chat_message("assistant").write(chat_message)
        st.session_state.messages.append({"role": "assistant", "content": chat_message})

        process_new_profile()
        
        st.session_state.bot_initialized = True


def main():
    
    initialize_frontend()
    initialize_chatbot()

    if prompt := st.chat_input():
        with st.chat_message("user"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.write(prompt)

        with st.spinner("Processing..."):
            answer = process_prompt(prompt)
        if "```" in answer:
            send_meal_plan(answer)
        else:
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.chat_message("assistant").write(answer)


if __name__ == "__main__":
    main()