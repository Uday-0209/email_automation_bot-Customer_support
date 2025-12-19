

import subprocess
import sys
import re
from tqdm import tqdm
import pandas as pd

class run_generator:
    @staticmethod
    def ensure_llm(model):
        try:
            result = subprocess.run(
                ['ollama', 'list'],
                capture_output = True,
                text = True, 
                timeout = 10
            )
        except FileNotFoundError:
            raise RuntimeError("ERROR: Ollama is not installed or not in PATH.")
        except subprocess.TimeOutExpired:
            raise RuntimeError("ERROR: 'ollama list' timed out. Is Ollama running?")
        except Exception as e:
            raise RuntimeError(f"Unexpected error when listing models: {str(e)}")

        if model in result.stdout:
            print(f"[OK] {model} is installed and working")
            return True
        
        print(f"[INFO] model {model} not found")
        print(f"Downloading the model{model} .....\n")

        pbar = tqdm(total = 100, unit = '%', bar_format = "{l_bar}{bar}| {n_fmt}/{total_fmt}%")
        process = subprocess.Popen(
            ['ollama', 'pull', model], 
            stdout = subprocess.PIPE, 
            stderr = subprocess.STDOUT,
            text = True, 
            bufsize = 1
        )

        try:
            for line in process.stdout:
                line = line.strip()

                match = re.search(r"(\d+)%", line)
                if match:
                    percent = int(match.group(1))
                    pbar.n = percent
                    pbar.refresh()
    
                # Print other stages (like resolving, verifying)
                if "pulling" not in line and "%" not in line:
                    tqdm.write(line)
    
            process.wait()
            pbar.n = 100
            pbar.refresh()
            pbar.close()
    
            if process.returncode == 0:
                print(f"\n[SUCCESS] Model '{model}' downloaded.")
                return True
            else:
                raise RuntimeError(f"Model pull failed with return code {process.returncode}")
    
        except Exception as e:
            pbar.close()
            print("ERROR while downloading model:", e)
            raise e   
    
    @staticmethod
    def generate_email(issue_value):

        model = 'llama3.2'

        ensure = run_generator.ensure_llm(model)
        
        process = subprocess.Popen(
            ['ollama', 'run', 'llama3.2:3b'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True
        )
        
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
        data = pd.read_json('/home/smddc/Documents/new_pro/email_classifier/possible_error.json')

        issue_num = None
        issue = None
        solution = None


        for i in zip(data['issue_number'], data['issue'], data['solution']):
            if i[0] == issue_value:
                issue_num = i[0]
                issue = i[1]
                solution = i[2]
        
        prompt = f"Consider yourself as tech supporter, here is possible issue number{issue_num}, issue {issue} and solution {solution}.Consider the inputs and generate the final ouput as clean email , mention issue number, issue and solution(descriptive), generate in 100 words, here is templeate{template}"
        
        process.stdin.write(prompt)
        process.stdin.close()     # IMPORTANT — tells ollama you're done sending input
        
        for line in process.stdout:
            yield line

        
        
