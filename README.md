# VIS Chatbot

VIS Chatbot is a visualization tool, utilizing OpenAI's ChatGPT to transform natural language prompts into data visualizations. This chatbot is built upon Paula Maddigan and Teo Susnjak's work Chat2VIS (https://ieeexplore.ieee.org/document/10121440). Reflecting upon their work, this app aims to provide conversational interface, code explanations and reasoning behind the choice of a specific plot type. 

## Main Features
- **Interactive Chat Interface**: Engage in a conversational experience, allowing users to input prompts in natural language, akin to communicating with ChatGPT.
- **Exploration Mode**: Dive into datasets with ease. Start with "Explore:" to get suggested prompts from ChatGPT, tailored to the dataset at hand.
- **Plot Generation**: Leverage the power of the ChatGPT API to generate data visualizations. Users can start prompts with "Show:" to initiate plot creation based on the provided dataset.
- **Plot Understanding**: After generating a plot, users can ask for a detailed description and rationale behind the chosen plot type by saying "Describe it".

## Usage
- **Prompt Suggestions**: Ask the chatbot to provide example prompts to kickstart your data exploration journey.
- **Interactive Plotting**: Enter your prompt in the input box, and the chatbot will generate a visualization based on the selected dataset.
- **Sidebar Guide**:
  - Input your OpenAI API Key in the provided field.
  - Choose your dataset from a list of available datasets or upload your own CSV file.
  - Access the prompt guide:
    - Explore Mode: Type "Explore:" to receive suggested prompts.
    - Show Mode: Type "Show:" to generate plots.
    - Description Mode: Type "Describe it" for an explanation of the generated plot.

## Requirements
- **Python Version**: 3.9.12
- **Libraries**: Streamlit, OpenAI, Matplotlib, Pandas
- **API Access**: A paid ChatGPT4 account API key is required for utilizing the ChatGPT functionalities.

## How It Works
- **vis_chatbot.py**: The main file of the application. It handles user interactions, manages datasets, and communicates with ChatGPT-4 API to generate and describe plots.
- **helpers.py**: A support module. It contains utility functions for plot identification, response formatting, and interaction with the ChatGPT API.

