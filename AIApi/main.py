import threading

from fastapi import FastAPI
from sync_docs import create_docs_from_folder, query_collection
from ollama import chat
from ollama import ChatResponse

# # sync_docs.start_monitor()
# scanFoldersThread = threading.Thread(target=create_docs_from_folder, args=('C:\\Users\\nicola\\obsidian-data'), kwargs={})
# scanFoldersThread.start()
# create_docs_from_folder('C:\\Users\\nicola\\obsidian-data')

app = FastAPI()

scanFoldersThread = threading.Thread(target=create_docs_from_folder, args=('C:\\Users\\nicola\\obsidian-data',), kwargs={})
scanFoldersThread.start()

@app.get("/query/{vault_name}")
async def query_vault(vault_name: str, query: str):
    documents = query_collection(vault_name, query)
    messages = [
        {
            'role': 'system',
            'content': 'Keep answers short and very factual',
        },
        {
            'role': 'system',
            'content': 'You are a rude travel assistant',
        }
    ]
    for document in documents[0]:
        messages.append({
            'role': 'assistant',
            'content': document,
        })

    messages.append({
        'role': 'user',
        'content': query,
    })

    print(messages)

    response: ChatResponse = chat(model='llama3.2', messages=messages)
    return {
        'response': response['message']['content'],
        'context': messages
    }


@app.get("/test/{prompt}")
async def test(prompt: str):
    # collection.add(
    #     ids=["1", "2", "3"], documents=["Venice is in veneto", "Rome is hot in summer",
    #                                     "Transistors are mede of silicon"])

    # return collection.query(
    #     query_texts=[prompt],
    #     n_results=10)["documents"][0]
    return ""
