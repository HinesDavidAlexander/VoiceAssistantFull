import customtkinter as tk
import threading
import time
import queue
import copy
from typing import Any

# Import the actions
from actions.weather import get_weather, get_weather_forecast
from actions.find_location import get_location
from actions.lookup_query import Search

# Import the funcitonalities
from functionality.action_router import get_action
from functionality.func_inspect import call_with_signature, has_args
from functionality.timer import Timer
from functionality.llm_gen import LLM
from functionality.speech_recog import SpeechRecog

class App():
    def __init__(self, command_dict: dict = {}):
        self.gui = tk.CTk()
        self.gui.title("Custom Home Voice Assistant")
        self.gui.geometry("900x600")
        
        self.open_top_level_button = tk.CTkButton(self.gui, text="History", command=self.open_toplevel)
        self.open_top_level_button.pack(side="top", padx=20, pady=20)
        self.toplevel = None
        self._create_top_level(from_init=True) # initialize the toplevel
        
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
        
        # Create the conversational LLM that will handle conversations. MUST BE RESET AFTER EACH CONVERSATION
        self.llm = LLM(log_file_path='conversation_log.csv', system_prompt='You are an assistant designed to help users with their queries. Please answer to the best of your ability. Please respond formally and in between one and three sentences.') #TODO: Move prompt to a file

    def _create_top_level(self, from_init=False):
        """Create the toplevel window if it doesn't exist. It will be hidden until the open_toplevel function is called.
        """
        if self.toplevel is None or not self.toplevel.winfo_exists():
            self.toplevel = tk.CTkToplevel(self.gui)
            self.toplevel.title("History")
            x = self.gui.winfo_x()
            y = self.gui.winfo_y()
            self.toplevel.geometry(f"300x300+{x}+{y}")
            self.toplevel_label = tk.CTkLabel(self.toplevel, text="History")
            self.toplevel_label.pack()
            self.toplevel_button = tk.CTkButton(self.toplevel, text="Close", command=self.close_toplevel)
            self.toplevel_button.pack()
            if from_init: # Hide the toplevel window if it was created from the __init__ function
                self.toplevel.withdraw()

    def open_toplevel(self):
        """Open the toplevel window if it is not already open. If it is open, it will be brought to the front. If it is minimized, it will be restored to its previous state.
        """
        # Create the toplevel window if it doesn't exist ()
        self._create_top_level()
        if self.toplevel.state() == "normal" or self.toplevel.state() == "zoomed":
            self.toplevel.focus()
        elif self.toplevel.state() == "withdrawn" or self.toplevel.state() == "iconic":
            x = self.gui.winfo_x()
            y = self.gui.winfo_y()
            self.toplevel.geometry(f"300x300+{x}+{y}")
            self.toplevel.deiconify()
            #self.toplevel.focus() # TODO: Fix the flashing issue where it flashes the toplevel window and then it goes behind the main window. This did not fix it.
    
    def close_toplevel(self):
        self.toplevel.withdraw()

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



    def run_action(self) -> tuple[bool, any, str]:
        user_command_req = ""
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
                    return False, None, user_command_req
                
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
                    
                    # render the return to the GUI
                    self.send_gui_update("update", "output_label", action_return)
                    #self.output_label.configure(text=action_return)
                    return True, action_return, user_command_req
        
        #self.thread = None
        return False, None, user_command_req
    
    
    
    def handle_followup(self, followup_query: str):
        """LLM will handle the followup text and determine if the conversation should continue or not.

        Args:
            followup_text (str): followup query from the user
            action_return (Any): return from the action that was run
            initial_query (str): initial query from the user
        """
        print(f"Followup Query: {followup_query}")
        self.send_gui_update("update", "history_label", f"You said: {followup_query}")
        
        #TODO: NOTE: When implementing this, make sure there's a "new conversation" verbal option that starts over with the self.run_action() call and resets the memory of the LLM.
        
        llm_response = self.llm.ask(followup_query)
        
        self.send_gui_update("update", "output_label", llm_response)
    
    
    
    def manage_conversation(self):
        """Handle the conversation so that it times out after 15 seconds, otherwise it will listen and run the action if the trigger phrase is said.
        """
        action_run, action_return, initial_query = self.run_action()
        
        # Short Circuit if no action was run, therefore no need to continue the conversation
        if not action_run:
            print("No action was run during initial listen, ending...")
            self.send_state(f"{self.speech_recog.state} No action run.")
            self.thread = None
            return
        
        # Start a new memory for the LLM, this will save the current memory (previous conversation) to the log file and reset the memory for this conversation
        self.llm.new_memory()
        
        # Update the LLM with the initial query and the action return for this conversation. This will show up as the first two rows in the conversation log after the system prompt.
        self.llm.update_memory("user", initial_query)
        self.llm.update_memory("assistant", action_return)
        
        # Conversation Loop
        conversation_resets = 0
        conversation_timer = Timer(15)
        while True:
            # Listen for a followup query from the User
            followup_text = self.speech_recog.listen_for_set_time(15)
            
            # Handle Printing the understood text to the gui
            self.send_gui_update("update", "history_label", f"You said: {followup_text}")
            
            # Handle the followup text and determine if the conversation should continue or not
            # STAY
            if self.followup_phrase in followup_text.lower(): 
                followup_req = followup_text.split(self.followup_phrase)[1].strip()
                self.handle_followup(followup_req)
                conversation_timer.reset()
            # RETURN
            elif followup_text == "":  
                # No input detected
                print("Conversation Timed Out due to lack of Mic input.")
                self.send_state(f"{self.speech_recog.state} due to Timeout.")
                break
            # BOTH
            elif followup_text == "error":
                # Error with audio recognition
                # STAY
                if conversation_timer.time_remaining() < 5 and not conversation_timer.has_expired():
                    # Error with audio recognition and timer not expired resets timer to 5 seconds and increments conversation_resets
                    conversation_resets += 1
                    if conversation_resets <= 2:
                        print(f"Conversation Resetting to 5 seconds... (reset #{conversation_resets})")
                        conversation_timer.set_time_remaining(5)
                
                # RETURN
                if conversation_timer.has_expired():
                    # Error with audio recognition and timer expired
                    print(f"Conversation Timed Out due to timer expiring after error with audio recognition. {self.speech_recog.state}")
                    self.send_state("Conversation timed out due to error with audio recognition.")
                    break
            # RETURN
            elif conversation_timer.has_expired():
                    # Timer expired before followup text was received
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