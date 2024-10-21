from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_correctness

# Assuming 'result' is the response from your model.py as provided
result = {
    "question": "What is the fine for littering?",
    "chat_history": [
        {
            "type": "HumanMessage",
            "content": "What is the fine for littering?"
        },
        {
            "type": "AIMessage",
            "content": "The fine for littering in Singapore is up to $2,000, with increased fines for repeat offenders. Thanks for asking!"
        }
    ],
    "answer": "The fine for littering in Singapore is up to $2,000, with increased fines for repeat offenders. Thanks for asking!",
    "source_documents": [
        {
            "page_content": "34SINGAPORE LAWS\nWhile working here, you must obey Singapore laws. Otherwise, you will face the \npenalties. Your work permit will be revoked and you will not be allowed to enter \nSingapore in the future. \nOffences\nLittering\nWastage of water\nUrinating in public  \nplaces\nJaywalking\nPublic drunkenness\nUnlawful consumption  \nof liquor in public places\nMaking a false  \npolice report\nTheft (stealing  \nor shoplifting)Penalties\n• Fine of up to $2,000, with increased fines\n for repeat offenders.\n• Imprisonment of up to 3 years or \n a fine of up to $50,000, or both.\n• $1,000 for every day or part thereof \n in case of continuing offence.\n• Fine of up to $1,000, with increased fines \n for repeat offenders.\n• Imprisonment of up to 3 months or a fine \n of up to $1,000, or both, with increased fines \n for repeat offenders.\n• Imprisonment of up to 1 month \n or a fine of up to $1,000.\n• For offenders detected within the Liquor \n Control Zone, an enhanced penalty of not \nmore than 1.5 times will apply.",
            "metadata": {
                "page": 35,
                "source": "docs/mw-handy-guide-english.pdf"
            }
        },
        # ... (Include other source_documents if needed)
    ],
    "generated_question": "What is the fine for littering?"
}

# Extract data from the result
question = result['question']
answer = result['answer']
contexts = [doc['page_content'] for doc in result['source_documents']]

# Define a ground truth answer (this can be adjusted based on authoritative sources)
ground_truth = "In Singapore, the fine for littering is up to $2,000 for a first-time offender, with increased fines for repeat offenders."

# Create the dataset
data_samples = {
    'question': [question],
    'answer': [answer],
    'contexts': [contexts],
    'ground_truth': [ground_truth]
}

dataset = Dataset.from_dict(data_samples)

# Evaluate using RAGAS
score = evaluate(dataset, metrics=[faithfulness, answer_correctness])
df = score.to_pandas()
df.to_csv('score.csv', index=False)
print(df)
