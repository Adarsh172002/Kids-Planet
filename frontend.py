import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from models import MCQArray, ShortAnswerArray, TrueFalseArray
import os
import re
# Backend logic for story generation and question extraction


load_dotenv()
def rewrite_with_ai(topic, num_questions, question_types):
    # Retrieve OpenAI API key from environment variable
    openai_api_key = os.getenv("OPENAI_API_KEY")

    # Initialize the GPT API model
    model_name = "gpt-3.5-turbo"
    model = ChatOpenAI(openai_api_key=openai_api_key, temperature=0, model=model_name)

    # Generate a story about the provided topic
    story_generation_prompt = f"Generate a story about {topic} that is at least {num_questions*3} lines long. Ensure each line has more than 30 words[[most important]]."

    # Set up prompts for different question types
    prompts = []
    parser = None
    for q_type in question_types:
        if q_type == "MCQ":
            prompt = f"Generate strictly only {num_questions} multiple choice questions based on the story and their correct answers. Ensure the options are shuffled and not predictable. Do not repeat questions."
            parser = JsonOutputParser(pydantic_object=MCQArray)
        elif q_type == "True/False":
            prompt = f"Generate strictly only {num_questions} True/False questions based on the story and their correct answers with explanations. Do not repeat questions."
            parser = JsonOutputParser(pydantic_object=TrueFalseArray)
        elif q_type == "Short Answer":
            prompt = f"Generate strictly only {num_questions} short answer questions based on the story with answers that are strictly 5 lines long and detailed. Do not repeat questions."
            parser = JsonOutputParser(pydantic_object=ShortAnswerArray)
        prompts.append(prompt)

    # Combine all prompts into one
    question_generation_prompt = "\n".join(prompts)

    # Set up a parser + inject instructions into the prompt template.
    prompt = PromptTemplate(
        template="{story_query}\n\n{question_query}\n\n{format_instructions}",
        input_variables=["story_query", "question_query"],
        partial_variables={"format_instructions": parser.get_format_instructions() if parser else ""},
    )

    chain = prompt | model | parser

    # Invoke the model to generate the response
    response = chain.invoke({"story_query": story_generation_prompt, "question_query": question_generation_prompt})
    
    if 'mcqs' in response:
        response['mcqs'] = response['mcqs'][:num_questions]
    if 'true_false_questions' in response:
        response['true_false_questions'] = response['true_false_questions'][:num_questions]
    if 'short_answer_questions' in response:
        response['short_answer_questions'] = response['short_answer_questions'][:num_questions]
    return response

def main():
    st.title("KIDS-PLANET")

    # Input form for topic, number of questions, and question type
    topic = st.text_input("Enter the topic of the story:")
    num_questions = st.number_input("Number of questions:", min_value=1, step=1)
    question_types = st.multiselect("Select question types:", ["MCQ", "True/False", "Short Answer"])

    if st.button("SUBMIT"):
        if topic.strip() == "":
            st.error("Please provide a topic.")
        elif num_questions < 1:
            st.error("Please enter a valid number of questions.")
        elif not question_types:
            st.error("Please select at least one question type.")
        else:
            # Call backend API with input data and display generated questions
            response = rewrite_with_ai(topic, num_questions, question_types)
            display_story_and_questions(response)



def display_story_and_questions(response):
    # Split the story into three paragraphs
    def split_into_paragraphs(text):
        sentences = re.split(r'(?<=[.!?]) +', text)
        num_sentences = len(sentences)
        part_size = num_sentences // 4

        # Ensure at least three parts
        if num_sentences < 3:
            return [text]

        paragraphs = [
            ' '.join(sentences[:part_size]).strip(),
            ' '.join(sentences[part_size:2 * part_size]).strip(),
            ' '.join(sentences[2 * part_size:]).strip()
        ]
        return paragraphs

    # Display the story
    if 'story' in response:
        st.subheader("Generated Story:")
        paragraphs = split_into_paragraphs(response['story'])
        for paragraph in paragraphs:
            st.write(paragraph)
            st.write("")  # Add an extra line break for better readability
        
        
    if 'mcqs' in response:
        st.subheader("Multiple Choice Questions:")
        for idx, mcq in enumerate(response['mcqs']):
            st.write(f"{idx + 1}. {mcq['question']}")
            for opt_idx, option in enumerate(mcq['options']):
                st.write(f"   {chr(97 + opt_idx)}. {option}")
            st.write(f"   Correct Option: {chr(97 + mcq['correct_option'])}")
            st.write("")

    if 'true_false_questions' in response:
        st.subheader("True/False Questions:")
        for idx, tf in enumerate(response['true_false_questions']):
            st.write(f"{idx + 1}. {tf['question']}")
            if 'options' in tf:
                st.write("   Options:")
                for opt_idx, option in enumerate(tf['options']):
                    st.write(f"      {chr(97 + opt_idx)}. {option}")
            st.write(f"   Correct Answer: {'True' if tf['correct_answer'] else 'False'}")
            st.write(f"   Explanation: {tf['explanation']}")
            st.write("")

    if 'short_answer_questions' in response:
        st.subheader("Short Answer Questions:")
        for idx, sa in enumerate(response['short_answer_questions']):
            st.write(f"{idx + 1}. {sa['question']}")
            st.write(f"   Expected Answer: {sa['correct_answer']}")
            st.write("")

if __name__ == "__main__":
    main()
