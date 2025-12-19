
class run_generator:
    @staticmethod
    def generate_email( issue_value, body):

        import google.generativeai as genai
        import pandas as pd
        from dotenv import load_dotenv
        import os
        from langchain_community.embeddings import HuggingFaceEmbeddings
        from langchain_community.vectorstores import Chroma
        import warnings

        warnings.filterwarnings('ignore')

        load_dotenv(override = True)
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        api_key = gemini_api_key 
        
        template = '''
        Dear customer,

        issue number:

        issue:

        solution:

        Feel free to contact us

        Best Regards,
        Uday Hiremath
        AI Expert
        '''
        data = pd.read_json('mtcm_intellipod.json')

        issue_num = None
        issue = None
        solution = None


        for i in zip(data['issue_number'], data['issue'], data['solution'], data['device']):
            if i[0] == issue_value:
                issue_num = i[0]
                issue = i[1]
                solution = i[2]
                device = i[3]

        embedding_model = HuggingFaceEmbeddings(
            model_name = 'sentence-transformers/all-mpnet-base-v2'
        )
        vectordb = Chroma(
            persist_directory = './chroma_langchain_db2',
            embedding_function = embedding_model
        )

        vector_extract = vectordb.similarity_search(body, k = 2)
        
        if issue_num is None or issue is None or solution is None:
            prompt = f"Consider yourself as tech supporter, here is possible issue  from vector database extraction {vector_extract}.Consider the inputs and generate the final ouput as clean email , mention issue number, issue and solution(descriptive),try to give one or more solution, generate in 150 words, here is templeate{template}"
        else:
            prompt = f"Consider yourself as tech supporter, here is possible issue number{issue_num}, issue {issue}, solution {solution}, device{device}  and vector database extraction {vector_extract}.Consider the inputs and generate the final ouput as clean email , mention issue number, issue and solution(descriptive),try to give one or more solution, generate in 150 words, here is templeate{template}"
        
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        response = model.generate_content(prompt)
        return response.text
