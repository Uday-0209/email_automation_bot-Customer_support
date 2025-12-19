
class run_generator:
    @staticmethod
    def generate_email( issue_value):

        import google.generativeai as genai
        import pandas as pd
        from dotenv import load_dotenv
        import os

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
        data = pd.read_json('possible_error.json')

        issue_num = None
        issue = None
        solution = None


        for i in zip(data['issue_number'], data['issue'], data['solution']):
            if i[0] == issue_value:
                issue_num = i[0]
                issue = i[1]
                solution = i[2]
        
        prompt = f"Consider yourself as tech supporter, here is possible issue number{issue_num}, issue {issue} and solution {solution}.Consider the inputs and generate the final ouput as clean email , mention issue number, issue and solution(descriptive), generate in 100 words, here is templeate{template}"
        
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel("gemini-2.5-flash")
        
        response = model.generate_content(prompt)
        return response.text
