import os
import uuid
import hashlib
import chromadb
from mpmath import limit

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)

# embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

client = chromadb.HttpClient(
    host='localhost',
    port=8000,
    tenant='oai',
    database='obsidian-docs',
)

def query_collection(vault_name, query):
    collection = client.get_or_create_collection(vault_name)
    return collection.query(n_results=100, query_texts=[query])["documents"]

def get_vault_name(stem_path, path):
    if path == '':
        return ''
    return path.replace(stem_path, '').split('\\')[0].replace(' ', '_')


def create_docs_from_folder(stem_path: str, path: str = ''):
    for full_path, folders, files in os.walk(os.path.join(stem_path, path)):
        vault_name = get_vault_name(stem_path, path)

        if vault_name != '':
            if vault_name != "Asia_2025":
                continue

            collection = client.get_or_create_collection(vault_name)

            for filename in files:
                if path.__contains__(".trash"):
                    continue
                if not filename.endswith(".md"):
                    continue
                print(full_path)
                print(filename)
                print(vault_name)
                print("....")
                with open(os.path.join(full_path, filename), 'r', encoding="utf8") as file:
                    file_content = file.read()
                    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
                    chunked_documents = text_splitter.create_documents([file_content])
                    # for document in chunked_documents:
                    for ix in range(0, len(chunked_documents)):
                        collection.upsert(
                            documents=[chunked_documents[ix].page_content],
                            ids=[hashlib.md5((os.path.join(full_path, filename) + str(ix)).encode()).hexdigest()]
                        )
                    # if len(chunked_documents) > 0:
                    #     print(filename)
                    #     Chroma.from_documents(
                    #         ids=[str(uuid.uuid1()) for _ in chunked_documents],
                    #         documents=chunked_documents,
                    #         collection_name=vault_name,
                    #         client=client,
                    #     )

        for folder_name in folders:
            create_docs_from_folder(stem_path, os.path.join(path, folder_name))

        break

# class FileEventsHanlder(FileSystemEventHandler):
#     def on_modified(self, event):
#         print(f'event type: {event.event_type} path : {event.src_path}')
#         if event.src_path.endswith('.md'):
#             with open(event.src_path, 'r') as file:
#                 file_content = file.read()
#             text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
#             chunked_documents = text_splitter.create_documents([file_content])
#             print(len(chunked_documents))
#             if len(chunked_documents) > 0:
#                 Chroma.from_documents(
#                     ids=[str(uuid.uuid1()) for _ in chunked_documents],
#                     documents=chunked_documents,
#                     collection_name="default",
#                     client=client,
#                 )
#
#     def on_created(self, event):
#         print(f'event type: {event.event_type} path : {event.src_path}')
#
#     def on_deleted(self, event):
#         print(f'event type: {event.event_type} path : {event.src_path}')
#
#
# event_handler = FileEventsHanlder()
# observer = Observer()
#
#
# def start_monitor():
#     observer.schedule(event_handler, path='C:\\Users\\nicola\\obsidian-data', recursive=True)
#     observer.start()
#
#
# def stop_monitor():
#     observer.stop()
#     observer.join()
