import streamlit as st
import openai
import pandas as pd
from helpers import *


def execute_and_capture_plot(code):
    """
    Executes the given Python code which is expected to generate a matplotlib plot.
    Captures the plot and returns it as an image.

    :param code: A string of Python code to execute.
    :return: BytesIO object containing the plot image.
    """
    # Execute the code
    try: 
        exec(code, globals())
    except Exception as e:
        st.info("Chatgpt failed to generate a plot. Please try again.")
        st.stop()
    
    # Save the plot to a BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)

    return buf

# List to hold datasets
if "datasets" not in st.session_state:
    datasets = {}
    # Preload datasets
    datasets["Movies"] = pd.read_csv("movies.csv")
    datasets["Housing"] =pd.read_csv("housing.csv")
    datasets["Cars"] = pd.read_csv("cars.csv")
    datasets["Colleges"] =pd.read_csv("colleges.csv")
    datasets["Customers & Products"] = pd.read_csv("customers_and_products_contacts.csv")
    datasets["Department Store"] = pd.read_csv("department_store.csv")
    datasets["Energy Production"] = pd.read_csv("energy_production.csv")
    st.session_state["datasets"] = datasets
else:
    # use the list already loaded
    datasets = st.session_state["datasets"]

with st.sidebar:
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")

    # First we want to choose the dataset, but we will fill it with choices once we've loaded one
    dataset_container = st.empty()
    # Add facility to upload a dataset
    try:
        uploaded_file = st.file_uploader(":computer: Load a CSV file:", type="csv")
        index_no=0
        if uploaded_file:
            # Read in the data, add it to the list of available datasets. Give it a nice name.
            file_name = uploaded_file.name[:-4].capitalize()
            datasets[file_name] = pd.read_csv(uploaded_file)
            # We want to default the radio button to the newly added dataset
            index_no = len(datasets)-1
    except Exception as e:
        st.error("File failed to load. Please select a valid CSV file.")
        print("File failed to load.\n" + str(e))
    # Radio buttons for dataset choice
    chosen_dataset = dataset_container.radio(":bar_chart: Choose your data:",datasets.keys(),index=index_no)

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Prompt Guide")
    st.sidebar.markdown("- 🗒️ Start with \"Explore:\" to get suggested prompt from chatgpt")
    st.sidebar.markdown("- 📉 Start with \"Show:\" to have chatgpt generate a plot based on your entered prompt")
    st.sidebar.markdown("- 📖 Start with \"Describe:\" to have chatgpt describe the plot it just generated for you")


st.title("💬 VIS Chatbot")
st.caption("A chatbot designed to create data visualizations from natural language with interactivity")

# Initial message from chatgpt
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

# This would keep any vis output from chatgpt staying in place
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])
    if "image" in msg:
        st.chat_message("assistant").image(msg["image"], caption=msg["prompt"], use_column_width=True)

# Stores the most recent plot code
if "vis_code" not in st.session_state:
    st.session_state["vis_code"] = ""

print(st.session_state["vis_code"])

if prompt := st.chat_input():
    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    # Set the API key globally for version 0.28
    openai.api_key = openai_api_key

    # Add your current message to the session state
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # simulate response
    # msg = simulate_chatgpt_response(prompt)

    # initialize answer with an empty string 
    answer = ""

    # naive approach to have chatgpt describe the most recently generated plot
    # If a prompt starts with "describe" we will send the plot code back to chatgpt api and have it describe the code
    if prompt.startswith("describe") or prompt.startswith("Describe"):
        if st.session_state["vis_code"]:
            answer = describe_plot(st.session_state["vis_code"], openai_api_key)
        else:
            st.info("You haven't created any visualization yet!")
            st.stop()
    
    elif prompt.startswith("show") or prompt.startswith("Show"):
        # Generate the prompt template depending on the selected dataset
        primer1, primer2 = get_primer(datasets[chosen_dataset],'datasets["'+ chosen_dataset + '"]') 
        
        # Format the question to be ready to sent to chatgpt api
        question_to_ask = format_question(primer1, primer2, prompt)

        # Retrieve the code answer
        answer = run_request(question_to_ask, openai_api_key)
        answer = primer2 + answer
        answer = format_response(answer)
    
    elif "explore" in prompt or "Explore" in prompt:
        answer = ask_gpt(describe_dataset(datasets[chosen_dataset]), prompt, openai_api_key)

    # simply send the prompt to chatgpt api
    else:
        answer = ask_gpt("", prompt, openai_api_key)

    # print(answer)

    # Execute the code 
    if "plt.show()" in answer:
        # Execute the code and get the plot image
        plot_image = execute_and_capture_plot(answer)

        # # display text
        msg = 'A visualization has been created based on your prompt'
        st.session_state.messages.append({"role": "assistant", "content": msg, "prompt": prompt, "image":plot_image})
        st.chat_message("assistant").write(msg)

        # Display the plot in the image container
        st.chat_message("assistant").image(plot_image, caption="Generated Plot", use_column_width=True)

        # Store the current code in the session state
        st.session_state["vis_code"] = answer
    else:
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.chat_message("assistant").write(answer)
    
# Display the datasets in a list of tabs
tab_list = st.tabs(datasets.keys())

# Load up each tab with a dataset
for dataset_num, tab in enumerate(tab_list):
    with tab:
        # Can't get the name of the tab! Can't index key list. So convert to list and index
        dataset_name = list(datasets.keys())[dataset_num]
        st.subheader(dataset_name)
        st.dataframe(datasets[dataset_name],hide_index=True)
