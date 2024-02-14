from openai import OpenAI
import json

class LLM:
    def __init__(self, api_key, log_file_path, system_prompt):
        self.client = OpenAI()
        self.system_prompt = system_prompt
        self.api_key = api_key
        self.running_memory = []  # List to store conversation logs
        self.update_memory("system", self.system_prompt) # Must be called to include system prompt 
        self.log_file_path = log_file_path
        self.client.api_key = self.api_key

    def ask(self, prompt, **kwargs):
        """Interact with the OpenAI API using the provided prompt and kwargs."""
        # Default settings
        default_settings = {
            "model": "gpt-3.5-turbo-0125",  # Use the specified model as the default
            # Add other default settings here if needed, for example:
            # "temperature": 0.7,
            # "max_tokens": 100,
        }

        # Update default settings with any provided kwargs
        settings = {**default_settings, **kwargs}
        
        # Pass kwargs directly to the Completion.create() call
        response = self.client.chat.completions.create(**settings, messages=self.running_memory + [{"role": "user", "content": prompt}])
        self.update_memory("user", prompt)
        self.update_memory("assistant", response.choices[0].text.strip())
        return response.choices[0].text.strip()

    def update_memory(self, role, content):
        """Update the running memory with the prompt and response."""
        #self.running_memory.append({"prompt": prompt, "response": response})
        self.running_memory.append({"role": role, "content": content})

    def save_memory_to_file(self):
        """Save the running memory to a file."""
        json.dump(self.running_memory, open(self.log_file_path, 'w'))
        # with open(self.log_file_path, 'w') as file:
        #     for entry in self.running_memory:
        #         file.write(f"Prompt: {entry['prompt']}\n")
        #         file.write(f"Response: {entry['response']}\n\n")

    def close(self):
        """Save the conversation log and perform any cleanup before closing."""
        self.save_memory_to_file()
        # Perform any other necessary cleanup
    
    def new_memory(self):
        """Clear the running memory."""
        self.save_memory_to_file()
        self.running_memory = []
        self.update_memory("system", self.system_prompt)
    
    def __del__(self):
        """Destructor to ensure that the log is saved when the object is deleted."""
        self.close()

# Usage example:
# llm = LLM(api_key='your_openai_api_key_here', log_file_path='conversation_log.txt')
# Use the ask method with additional parameters as needed
# response = llm.ask("What is the capital of France?", engine="text-davinci-003", temperature=0.7)
# print(response)
# llm.close()  # Make sure to call this when you're done to save the log
