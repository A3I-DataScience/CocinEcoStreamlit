from user_profiles import predefined_profiles, init_user_agent_from_profile
from agents_profiles import all_in_one_agent
from RAG_agent_definition import init_rag_agent_from_profile
from app import process_prompt, save_meal_plan_to_csv, reset_profile
import os
import streamlit as st
import datetime

import logging
import logging.config

logger = logging.getLogger("simulation")

logging.basicConfig(
    filename="LogFile.log",
    filemode="a",
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.INFO,
)


def chat_simulation_for_all_profiles():
    for user_name in predefined_profiles.keys():
        chat_simulation(user_name)


def chat_simulation(user_name):
    profile_data = predefined_profiles[user_name]

    reset_profile(profile_data)

    user_llm, user_system_prompt = init_user_agent_from_profile(predefined_profiles[user_name])
    conversational_rag_chain = init_rag_agent_from_profile(agent_profile=all_in_one_agent)

    file_name = f"Meal-Plan_{st.session_state.user_name}_{datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')}.csv"

    chat_history = []
    chat_message = (
        "Hello there! I'm CocinEco: an AI assistant that will help you elaborate sustainable meal plans."
        + "I will ask you a few questions to understand you better and provide"
        + "you with personalized nutrition advice. Let's get started! ok?"
    )
    logger.info("Cocineco : ")
    logger.info(chat_message)

    for _ in range(20):
        conversation = [("system", user_system_prompt)]
        conversation.append(("user", chat_message))
        user_response = user_llm.invoke(input=conversation).content
        logger.info("==========================================================")
        logger.info("= %s : ", user_name)
        logger.info("= %s : ", user_response)
        logger.info("==========================================================")

        chat_message, context, chat_history = process_prompt(
            user_response,
            conversational_rag_chain=conversational_rag_chain,
            chat_history=chat_history,
        )
        logger.info("==========================================================")
        logger.info("= Cocineco : ")
        logger.info("= Message : %s", chat_message)
        logger.info("= Context : %s", context)
        logger.info("==========================================================")
        if "```" in chat_message:
            save_meal_plan_to_csv(chat_message, file_name)
            print("!!! The chat is over !!!")
            break

def main():
    chat_simulation_for_all_profiles()

if __name__ == "__main__":
    main()