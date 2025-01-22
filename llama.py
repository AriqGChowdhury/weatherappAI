import torch
from transformers import pipeline

class Llama:
    def __init__(self, forecast_data):
        self.model_id = "meta-llama/Llama-3.2-3B-Instruct"
        self.pipe = pipeline(
            "text-generation",
            model=self.model_id,
            torch_dtype=torch.bfloat16,
            device_map="auto",
        )
        
        self.forecast_data = forecast_data
    
    def define_model(self):
        
        
        
        messages = [
            {"role": "system", "content": """You are a weather advisor. 
            I will provide you with the weather for the next 5 days.
            Your job is to summarize the data I provide to the user.
            Please provide a human like response!
            The temperatures provided are in farenheit.
            """},
            
            {"role": "user", "content": f'Forecast Data:{self.forecast_data}'}
        ]
        
        outputs = self.pipe(
            messages,
            max_length=1000
        )[0]["generated_text"][-1]
        return outputs
    
    # def check_city(self, validateCity):
    #     messages = [
    #         {
    #             "role": "system",
    #             "content": """You will be given a city name, zip code, gps coordinates, landmarks, town, etc..
    #             Your job is to verify if the user input is valid and matches to the city.
    #             Dont invalidate user input just because of commas.
    #             If valid, respond only with city name.
    #             If its not valid then say "not valid"
    #             """
    #         },
    #         {
    #             "role": "user",
    #             "content": validateCity
    #         }
    #     ]
        
    #     outputs = self.pipe(
    #         messages,
    #     )[0]["generated_text"][-1]
        
    #     return outputs
        
# llama_obj = Llama()
# llama_obj.define_model()