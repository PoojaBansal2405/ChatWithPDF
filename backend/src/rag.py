from typing import  List, Dict, Any
from src.retriever import RAGRetriever
import time
import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()
#Initialize the groq llm

api_key = os.getenv("groq_api_key");
llm=ChatGroq(
    groq_api_key=api_key,
    model_name="openai/gpt-oss-120b",
    temperature=0.1,
    max_tokens=1024
)

class AdvancedRAGPipeline:
    def __init__(self, retriever: RAGRetriever, llm):
        self.retriever = retriever
        self.llm = llm
        

    def query(self, 
              question: str, 
              notebook_id: str, 
              
              top_k: int = 5, 
              min_score: float = 0.2, 
              stream: bool=False, 
              summarize: bool = False) -> Dict[str, Any]:
     


      
          
        results = self.retriever.retrieve(query=question, 
        notebook_id=notebook_id,
        top_k=top_k, score_threshold=min_score)

        if not results:
            return{
            "question": question,
            "answer" : "No relevent context found.",
            "sources" : [],
            "summary" : None
            }
        
           
           
        context = "\n\n".join([doc['content'] for doc in results]) 

        sources = [{
              'source': doc['metadata'].get('source_file', doc['metadata'].get('source', 'unknown')),
              'page': doc['metadata'].get('page' ,'unknown'),
              'score': doc['similarity_score'],
              'preview': doc['content'][:120] + '...'
            } for doc in results]

           # Streaming answer simulation
        prompt = f"""Use the following context to answer the question concisely.\nContext:\n{context}\n\nQuestion: {question}\n\nAnswer"""
          

            #generate anser using llm
        response = self.llm.invoke(prompt)
        answer = response.content

        # Add citations to answer
        citations = [f"[{i+1}] {src['source']} (page {src['page']})" for i, src in enumerate(sources)]

        answer_with_citations = answer + "\n\nCitations:\n" + "\n".join(citations) if citations else answer 


        #optionally summarize answer
        summary = None

        if summarize and answer:


            summary_prompt = f"Summarize the following answer in 2 sentences:\n{answer}"
            summary_resp=self.llm.invoke([summary_prompt])
            summary=summary_resp.content

       

        return {
           'question': question,
           'answer': answer_with_citations,
           'sources': sources,
           'summary': summary,
        }


