import customtkinter as tk
import threading
import time
from functionality.speech_recog import SpeechRecog
import queue
import copy

# Import the actions
from actions.weather import get_weather, get_weather_forecast
from actions.find_location import get_location
from actions.lookup_query import Search

# Import the funcitonalities
from functionality.action_router import get_action
from functionality.func_inspect import call_with_signature, has_args


class App():
    def __init__(self, command_dict: dict = {}):
        self.gui = tk.CTk()
        self.gui.title("Custom Home Voice Assistant")
        self.gui.geometry("900x600")
        self.prompt_label = tk.CTkLabel(self.gui, text="Press the button and say something...", pady=35)
        self.prompt_label.pack()
        self.start_button = tk.CTkButton(self.gui, text="Start", command=self.start)
        self.start_button.pack()
        self.status_label = tk.CTkLabel(self.gui, text="Status...", pady=35)
        self.status_label.pack()
        self.output_label = tk.CTkLabel(self.gui, text="Readout here...", pady=35)
        self.output_label.pack()
        self.thread = None
        self.state_queue = queue.Queue()
        
        self.trigger_phrase = "run command"
        self.command_dict = command_dict
        
        self.speech_recog = SpeechRecog(self.state_queue)

    def start(self):
        if self.thread is None:
            self.thread = threading.Thread(target=self.run_action)
            self.thread.start()
            self.check_queue()

    def check_queue(self):
        try:
            state = self.state_queue.get_nowait()  # Non-blocking check of the queue
            self.status_label.configure(text=state)  # Update the label with the new state
            #print(f'GUI: Reflecting state change to {state}')
        except queue.Empty:
            pass  # No new state, do nothing

        if self.thread is not None and self.thread.is_alive():
            self.gui.after(100, self.check_queue)

    def run_action(self):
        
        # Start Listening for Speech. Update the status label to reflect the current state of the speech recog
        self.status_label.configure(text=self.speech_recog.state)
        text = self.speech_recog.listen_for_speech()
        
        
        # Handle Printing the understood text to the gui
        time.sleep(0.11) # sleep longer than the next tick of the "check_queue" function
        final_text = "You said: " + text
        self.status_label.configure(text=final_text)
        
        # Handle running the command
        if self.trigger_phrase in text:
            # Get the command from the text
            user_command_req = text.split(self.trigger_phrase)[1].strip()
            # Use LLM to pick the best action from the command dictionary
            action_selected_response = get_action(user_command_req, self.command_dict)
            
            print(f"Action Selection Dict: {action_selected_response}, type: {type(action_selected_response)}")
            
            # Traverse the LLM Return dict to find the action to run
            if "path" in action_selected_response.keys():
                # Get the path to the action
                key_nest_path = action_selected_response["path"]
                # Deep copy the command dictionary to prevent changes to the original
                running_dict = copy.deepcopy(self.command_dict)
                
                # Convert the running_dict to a callable through digging down into the nested dictionary
                try:
                    for key in key_nest_path:
                        running_dict = running_dict[key]
                except KeyError as k:
                    print(f"Invalid Action Path. Key Error: {k}")
                    self.output_label.configure(text=f"Invalid Action Path. Key Error: {k}")
                    return "No Action Found"
                
                # Rename the variable for clarity
                final_callable = running_dict
                
                # Run the callable
                if callable(final_callable):
                    print(f"Running Action: {final_callable.__name__}")
                    
                    # Check if the function has arguments, if so, pass the user_command_req to the function (that should always be the input for the function, should be type str)
                    if has_args(final_callable):
                        # Check if the function has arguments, if so, pass the user_command_req to the function (that should always be the input for the function, should be type str)
                        action_return = call_with_signature(final_callable, [user_command_req]) # TODO: This needs to not use final callable, or be wrapped? I don't know if this will stay once I have an LLM determine calling
                    else:
                        action_return = final_callable()
                    
                    
                    
                    # if "Args:" in final_callable.__doc__: #TODO: Change this to check if it's a class method or function, and have the rule that only methods can accept arguments, and functions cannot
                    #     # Check if the function has arguments, if so, pass the user_command_req to the function (that should always be the input for the function, should be type str)
                    #     action_return = final_callable(user_command_req)
                    # else:
                    #     action_return = final_callable()
                    
                    
                    # render the return to the GUI
                    self.output_label.configure(text=action_return)
        
        self.thread = None
        return

if __name__ == "__main__":
    # Initialize the command dictionary with function based actions
    commands = {"weather": {"Now":get_weather, "Forecast":get_weather_forecast}, "location": get_location, "search": Search.search}
    #call_with_signature(Search.search, ["New York"])
    app = App(command_dict=commands)
    # Add class based actions to the command dictionary
    app.command_dict | {}
    
    # Start the GUI loop
    app.gui.mainloop()