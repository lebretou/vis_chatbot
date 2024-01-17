import random
import matplotlib.pyplot as plt
import io
import openai
from matplotlib.lines import Line2D
import matplotlib.collections as mcoll
import matplotlib.lines as mlines
import matplotlib.patches as mpatches

def identify_plot_type(ax):
    for item in ax.get_children():
        if isinstance(item, Line2D):
            return "Line Plot"
        elif isinstance(item, mcoll.PathCollection):
            return 'Scatter Plot'
        elif isinstance(item, mpatches.Wedge):
            return 'Pie Chart'
        elif isinstance(item, mpatches.Rectangle):
            return 'Bar Plot'
    return "Unknown Plot Type"


# function that simply sends user's prompt to the chatgpt api and returns the response
def ask_gpt(task, prompt, key):
    openai.api_key = key
    model = "gpt-4"

    response = openai.ChatCompletion.create(model=model,
        messages=[{"role":"system","content":task},{"role":"user","content":prompt}])

    llm_response = response["choices"][0]["message"]["content"]

    return llm_response


def simulate_chatgpt_response(user_message):
    """
    Simulates a response from the ChatGPT API. This is a basic simulation and does not
    actually understand or process the user's input. It randomly chooses a response
    from a predefined list.

    :param user_message: The user's message to which the bot will respond.
    :return: A simulated response message.
    """

    # Sample responses to simulate a conversation
    responses = [
        "That's an interesting point!",
        # "I'm not sure I understand, could you elaborate?",
        # "Yes, I agree with you.",
        # "Hmm, I'd need to think more about that.",
        # "Can you tell me more about it?",
        # "That's a great question, let me think...",
        # "I'm sorry, I'm not equipped to answer that.",
        """
        import matplotlib.pyplot as plt
        plt.plot([1, 2, 3, 4])
        plt.ylabel('some numbers')
        """ 
    ]

    return random.choice(responses)


# def execute_and_capture_plot(code):
#     """
#     Executes the given Python code which is expected to generate a matplotlib plot.
#     Captures the plot and returns it as an image.

#     :param code: A string of Python code to execute.
#     :return: BytesIO object containing the plot image.
#     """
#     # Execute the code
#     exec(code, globals())

#     # Save the plot to a BytesIO object
#     buf = io.BytesIO()
#     plt.savefig(buf, format='png')
#     plt.close()
#     buf.seek(0)
    
#     return buf


def run_request(question_to_ask, key):
    """
    This function sends the user prompt input to the chatgpt-4 api
    retrieves back the python code to generate the plot 
    """

    # Run OpenAI ChatCompletion API
    task = "Generate Python Code Script."
    # Ensure GPT-4 does not include additional comments
    task = task + " The script should only include code, no comments."

    openai.api_key = key

    response = openai.ChatCompletion.create(model="gpt-4",
        messages=[{"role":"system","content":task},{"role":"user","content":question_to_ask}])
    llm_response = response["choices"][0]["message"]["content"]

    return llm_response

def describe_plot(plot_code, key):
    """
    Describes the plot by sending the code response to generate the plot back to chatgpt 
    """

    task = """Describe the plot that this code generates. 
    Start with this plot shows...Specify the plot type, x and y axis if applicable. Describe what variables are used.
    Detail on aggregation method if applicable. 
    Do not talk about the aspect of the code and only the plot itself. Keep the description short. 
    """

    model = "gpt-4"
    openai.api_key = key

    response = openai.ChatCompletion.create(model=model,
        messages=[{"role":"system","content":task},{"role":"user","content":plot_code}])
    llm_response = response["choices"][0]["message"]["content"]

    return llm_response

def describe_dataset(df_dataset):
    """
    This function takes a dataframe and returns a description of the dataset
    """
    desc = """
    I built a natural language to data visualization chatbot using openai api. Now to help users explore the dataset and suggest 
    useful prompts, below is a description of the dataset including the column names and their data types. I also appended
    a head of the dataset. Based on the description above and user input, could you suggest 5 prompts? Answer in the fashion of 1. 2. 3. 4. 5. Do not include other text in your answer just 
    the suggested prompts. 
    """

    for i in df_dataset.columns:
        if len(df_dataset[i].drop_duplicates()) < 20 and df_dataset.dtypes[i]=="O":
            desc = desc + "\nThe column '" + i + "' has categorical values '" + \
                "','".join(str(x) for x in df_dataset[i].drop_duplicates()) + "'. "
        elif df_dataset.dtypes[i]=="int64" or df_dataset.dtypes[i]=="float64":
            desc = desc + "\nThe column '" + i + "' is type " + str(df_dataset.dtypes[i]) + " and contains numeric values. "
    
    desc += "\n\nHead of the dataset:\n" + df_dataset.head().to_string()
    desc += "\n\nUser input:"
    
    return desc


def format_response(res):
    """
    Remove the load_csv from the answer if it exists
    """

    csv_line = res.find("read_csv")
    if csv_line > 0:
        return_before_csv_line = res[0:csv_line].rfind("\n")
        if return_before_csv_line == -1:
            # The read_csv line is the first line so there is nothing to need before it
            res_before = ""
        else:
            res_before = res[0:return_before_csv_line]
        res_after = res[csv_line:]
        return_after_csv_line = res_after.find("\n")
        if return_after_csv_line == -1:
            # The read_csv is the last line
            res_after = ""
        else:
            res_after = res_after[return_after_csv_line:]
        res = res_before + res_after
    return res

def format_question(primer_desc,primer_code , question):
    """
    Fill in the model_specific_instructions variable
    """
    instructions = ""

    primer_desc = primer_desc.format(instructions)  
    # Put the question at the end of the description primer within quotes, then add on the code primer.
    return  '"""\n' + primer_desc + question + '\n"""\n' + primer_code

def get_primer(df_dataset,df_name):
    """
    Primer function to take a dataframe and its name
    and the name of the columns
    and any columns with less than 20 unique values it adds the values to the primer
    and horizontal grid lines and labeling
    """

    primer_desc = "Use a dataframe called df from data_file.csv with columns '" \
        + "','".join(str(x) for x in df_dataset.columns) + "'. "
    for i in df_dataset.columns:
        if len(df_dataset[i].drop_duplicates()) < 20 and df_dataset.dtypes[i]=="O":
            primer_desc = primer_desc + "\nThe column '" + i + "' has categorical values '" + \
                "','".join(str(x) for x in df_dataset[i].drop_duplicates()) + "'. "
        elif df_dataset.dtypes[i]=="int64" or df_dataset.dtypes[i]=="float64":
            primer_desc = primer_desc + "\nThe column '" + i + "' is type " + str(df_dataset.dtypes[i]) + " and contains numeric values. "   
    primer_desc = primer_desc + "\nLabel the x and y axes appropriately."
    primer_desc = primer_desc + "\nAdd a title. Set the fig suptitle as empty."
    primer_desc = primer_desc + "\nPut your reasoning of why you chose the specifc plot type and other reasons of how you came up with the plot according to the prompt in a long string and store it in a variable named \"reasoning\"" # Space for additional instructions if needed
    primer_desc = primer_desc + "\nUsing Python version 3.9.12, create a script using the dataframe df to graph the following: "
    pimer_code = "import pandas as pd\nimport matplotlib.pyplot as plt\n"
    pimer_code = pimer_code + "fig,ax = plt.subplots(1,1,figsize=(10,4))\n"
    pimer_code = pimer_code + "ax.spines['top'].set_visible(False)\nax.spines['right'].set_visible(False) \n"
    pimer_code = pimer_code + "df=" + df_name + ".copy()\n"
    return primer_desc,pimer_code