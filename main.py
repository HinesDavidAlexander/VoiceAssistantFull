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
from functionality.timer import Timer


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
        self.history_label = tk.CTkLabel(self.gui, text="Last thing you said...", pady=5)
        self.history_label.pack()
        self.output_label = tk.CTkLabel(self.gui, text="Readout here...", pady=35)
        self.output_label.pack()
        self.thread = None
        self.state_queue = queue.Queue()
        self.command_queue = queue.Queue()
        self.gui_queue = queue.Queue()
        
        self.trigger_phrase = "run command"
        self.followup_phrase = "next command"
        self.command_dict = command_dict
        
        self.speech_recog = SpeechRecog(self.state_queue) #TODO: Does not need queue, it doesn't use it. Need to change this

    def start(self):
        if self.thread is None:
            self.thread = threading.Thread(target=self.manage_conversation)
            self.thread.start()
            self.check_queue()

    def _check_state_queue(self):
        """Check the state queue for new state messages. This will always update the status label with the most recent state, nothing else.
        """
        # Check the state queue for new state messages. This will always update the status label with the most recent state, nothing else.
        try:
            state_msg = self.state_queue.get_nowait()  # Non-blocking check of the queue
            self.status_label.configure(text=state_msg)  # Update the label with the new state
            print(f'GUI: Reflecting state change to {state_msg}')
        except queue.Empty:
            pass  # No new state, do nothing

    def _check_command_queue(self):
        # Check the command queue for new commands
        try:
            command_msg = self.command_queue.get_nowait()  # Non-blocking check of the queue
            print(f'GUI: On command_queue - Received command: {command_msg}')
        except queue.Empty:
            pass  # No new state, do nothing

    def _check_gui_queue(self):
        # Check the gui queue for new commands
        try:
            action, element, value = self.gui_queue.get_nowait()  # Non-blocking check of the queue
            print(f'GUI: On gui_queue - Received action: {action}, element: {element}, value: {value}')
            if action == "update":
                element_obj = getattr(self, element)
                try:
                    element_obj.configure(text=value)
                except Exception as e:
                    print(f'GUI: Error updating element: {e}')
        except queue.Empty:
            pass

    def check_queue(self):
        # NOTE: Currently each queue processes only one item per call of this function. This can be changed to have it loop through each queue and process all items in each queue. Not sure which is better yet.
        
        self._check_state_queue()
        
        self._check_command_queue()
        
        self._check_gui_queue()

        # Check the queue again in 100ms (recursive call to this function)
        if self.thread is not None and self.thread.is_alive():
            self.gui.after(100, self.check_queue)

    def send_gui_update(self, action, element, value):
        """Send a message to the GUI to update an element with a new value.

        Args:
            action (str): action for the GUI to take
            element (str): element to update
            value (any): new value for the element
        """
        self.gui_queue.put((action, element, value))
    
    def send_command(self, command):
        """Send a command to the command queue. NOTE: _check_command_queue is not implemented yet, therefore none of the commands will be processed.

        Args:
            command (any): command to send to the command queue
        """
        self.command_queue.put(command)
    
    def send_state(self, state):
        """Send a state message to the state queue.

        Args:
            state (str): state message to send
        """
        self.state_queue.put(state)

    def run_action(self) -> tuple[bool, any]:
        
        # Start Listening for Speech. Update the status label to reflect the current state of the speech recog
        self.send_state("Starting...")
        #self.send_state(self.speech_recog.state)
        #self.status_label.configure(text=self.speech_recog.state)
        text = self.speech_recog.listen_for_speech()
        
        
        # Handle Printing the understood text to the gui
        time.sleep(0.11) # sleep longer than the next tick of the "check_queue" function
        final_text = "You said: " + text
        self.send_gui_update("update", "history_label", final_text)
        #self.status_label.configure(text=final_text)
        
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
                    self.send_gui_update("update", "output_label", f"Invalid Action Path. Key Error: {k}")
                    #self.output_label.configure(text=f"Invalid Action Path. Key Error: {k}")
                    return False, None
                
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
                    self.send_gui_update("update", "output_label", action_return)
                    #self.output_label.configure(text=action_return)
                    return True, action_return
        
        #self.thread = None
        return False, None
    
    def handle_followup(self, followup_text: str):
        """LLM will handle the followup text and determine if the conversation should continue or not.

        Args:
            followup_text (str): followup text from the user
        """
        print(f"Followup Text: {followup_text}")
        self.send_gui_update("update", "output_label", f"Followup Text: {followup_text}")
        self.send_gui_update("update", "history_label", f"You Said: {followup_text}")
        
        #TODO: NOTE: When implementing this, make sure there's a "new conversation" verbal option that starts over with the self.run_action() call and resets the memory of the LLM.
    
    def manage_conversation(self):
        """Handle the conversation so that it times out after 15 seconds, otherwise it will listen and run the action if the trigger phrase is said.
        """
        action_run, action_return = self.run_action()
        
        # Short Circuit if no action was run, therefore no need to continue the conversation
        if not action_run:
            print("No action was run during initial listen, ending...")
            self.send_state(f"{self.speech_recog.state} No action run.")
            self.thread = None
            return
        
        
        conversation_timer = Timer(15)
        while True:
            followup_text = self.speech_recog.listen_for_set_time(10)
            if self.followup_phrase in followup_text.lower():
                followup_req = followup_text.split(self.followup_phrase)[1].strip()
                self.handle_followup(followup_req)
                conversation_timer.reset()
            elif followup_text == "":
                print("Conversation Timed Out due to lack of Mic input.")
                self.send_state(f"{self.speech_recog.state} due to Timeout.")
                break
            elif followup_text == "error":
                if conversation_timer.has_expired():
                    print(f"Conversation Timed Out due to timer expiring after error with audio recognition. {self.speech_recog.state}")
                    self.send_state("Conversation timed out due to error with audio recognition.")
                    break
            else:
                if conversation_timer.has_expired():
                    print("Conversation Timed Out due to timer expiring.")
                    self.send_state(f"{self.speech_recog.state} at Timer=0.")
                    break
        
        self.thread = None
        return

if __name__ == "__main__":
    # Initialize the command dictionary with function based actions
    commands = {"weather": {"Now":get_weather, "Forecast":get_weather_forecast}, "location": get_location, "search": Search.search}
    # Create the app
    app = App(command_dict=commands)
    # Add class based actions to the command dictionary
    app.command_dict | {}
    
    # Start the GUI loop
    app.gui.mainloop()