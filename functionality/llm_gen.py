from openai import OpenAI
import json
import os
from functionality.utils import save_json_to_csv, read_csv_to_json

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
class LLM:
    def __init__(self, log_file_path, system_prompt):
        self.client = OpenAI()
        self.system_prompt = system_prompt
        self.running_memory = []  # List to store conversation logs
        self.update_memory("system", self.system_prompt) # Must be called to include system prompt 
        self.log_file_path = log_file_path

    def ask(self, prompt, **kwargs):
        """Interact with the OpenAI API using the provided prompt and kwargs. This function automatically updates the running memory with the query(prompt) and response.

        Args:
            prompt (str): query to be sent to the model
            kwargs: additional parameters to be passed to the model's .create() method

        Returns:
            str: model response based on the query and running memory
        """
        # Default settings
        default_settings = {
            "model": "gpt-3.5-turbo-0125",  # Use the specified model as the default
            # Add other default settings here if needed, for example:
            # "temperature": 0.7,
            # "max_tokens": 100,
        }

        # Update default settings with any provided kwargs
        settings = {**default_settings, **kwargs}
        
        # Add the latest prompt to the running memory. This is what the model will respond to.
        self.update_memory("user", prompt)
        
        # Pass kwargs directly to the completions.create() call
        response = self.client.chat.completions.create(**settings, messages=self.running_memory)
        
        # Add the model response to the running memory
        self.update_memory("assistant", response.choices[0].message.content.strip())
        return response.choices[0].message.content.strip()

    def update_memory(self, role, content):
        """Update the running memory with the prompt and response."""
        #self.running_memory.append({"prompt": prompt, "response": response})
        self.running_memory.append({"role": role, "content": content})

    def save_memory_to_file(self):
        """Save the running memory to a file."""
        save_json_to_csv(self.running_memory, self.log_file_path)

    def close(self):
        """Save the conversation log and perform any cleanup before closing."""
        if len(self.running_memory) > 1:
            self.save_memory_to_file()
            # Perform any other necessary cleanup
    
    def new_memory(self):
        """Save running memory to a file and clear the running memory, then update the memory with the system prompt."""
        if len(self.running_memory) > 1: # Only save if there is a conversation, not just the system prompt
            self.save_memory_to_file()
            self.running_memory = []
            self.update_memory("system", self.system_prompt)
        else:
            print("No conversation to save, only system prompt was in memory. No file was saved.")
            self.running_memory = []
            self.update_memory("system", self.system_prompt)
    
    def __del__(self):
        """Destructor to ensure that the log is saved when the object is deleted."""
        self.close()

# # Usage example:
# llm = LLM(log_file_path='conversation_log.csv', system_prompt='You are an assistant designed to help users with their queries. Please answer to the best of your ability.')
# # Use the ask method with additional parameters as needed
# response = llm.ask("")
# print(response)
# llm.close()  # Make sure to call this when you're done to save the log
