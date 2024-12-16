from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from decouple import config
from langchain_huggingface.llms import HuggingFacePipeline
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

from langchain_huggingface import HuggingFaceEmbeddings



GOOGLE_API_KEY = config('GOOGLE_API_KEY')
model_generative_name = "gemini-2.0-flash-exp"
model_embeddings_name = "models/embedding-001"

llm = GoogleGenerativeAI(model=model_generative_name,
                         google_api_key=GOOGLE_API_KEY)

query_embeddings_model = GoogleGenerativeAIEmbeddings(model=model_embeddings_name,
                                                      task_type="retrieval_query",
                                                      google_api_key=GOOGLE_API_KEY)

doc_embeddings_model = GoogleGenerativeAIEmbeddings(model=model_embeddings_name,
                                                    task_type="retrieval_document",
                                                    google_api_key=GOOGLE_API_KEY)

# query_embeddings_model = HuggingFaceEmbeddings(model_name='paraphrase-multilingual-MiniLM-L12-v2')
#
# doc_embeddings_model = query_embeddings_model