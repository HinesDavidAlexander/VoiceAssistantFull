# My Home Assistant - Longer Term Project

## README is currently inaccurate. Will change later.

## Overview

This project is a one-day experiment aimed at creating a simple version of a home assistant. The goal is to implement basic functionalities that can serve as a foundation for a more complex home automation system. Due to the limited timeframe, the focus is on simplicity, feasibility, and demonstration of core concepts rather than building a fully-featured application.

## Features

- **Voice Command Recognition**: Accept basic voice commands to perform tasks like turning on/off lights or checking the weather.
- **Device Integration**: [NOT IMPLEMENTED] Basic integration with simulated home devices (e.g., lights, thermostat).
- **Weather Updates**: Provide current weather information upon request.
- **Location Data**: Provide location readout to the user based on IP location

## Limitations

Given the time constraint of a single day, the following limitations apply:

- Limited device compatibility: Only a predefined set of virtual actions will be usable.
- Simplified voice recognition: May not accurately interpret all commands due to the use of basic voice recognition techniques.
- Basic functionality: Features will be rudimentary, focusing on demonstrating the concept rather than providing a polished user experience.

## Future Possible Improvements

The following are a list of potential future improvements that could be made based on the current state of the application.

- Decorators for Action Consistency:
    - Due to the nature of how Actions are handled, requiring specific return types, ensuring consistency is good. Create a decorator that takes the Action output and converts it to str if not already str.
    - This would open up the option to further improve using this decorator, options like auto-filling the actions dict and similar functionality come to mind.
- Simulated Voice for readouts
- NLP for similarity to 'run command' action phrase, recognition isn't always accurate and may need a few tries sometimes
- NLP for simmilarity to command options from the dict, same reason as prior note
- More advanced GUI, current GUI implementation targets function over style, and therefore is quite rudamentary.
- Change action input style and usage rules relating to methods and fns (see TODO in App.run_action method in `main.py`)
- [NEXT STEP] Wrap the Action calls in a decision LLM agent that takes the text var of the voice input and uses the function chosen as a 'tool', later outputting a final result that's rendered to the GUI (later spoken aloud?)

## Technologies Used

- **Programming Language**: Python 3.x (for its extensive support for quick prototyping and available libraries for device control and voice recognition).
- **Libraries**: See requirements.txt


## Setup Instructions

1. **Clone the repository**: `git clone https://github.com/HinesDavidAlexander/VoiceAssistant.git`
2. **Install dependencies**: Navigate to the project directory and run `pip install -r requirements.txt` to install necessary Python libraries.
3. **API Keys**: Obtain necessary API keys (e.g., SpeechRecognition API) and set them in the configuration file (`.env`) at the root level. Required keys are shown in `.env.example`
4. **Run the Assistant**: Execute `main.py` to start the home assistant. Ensure your microphone is set up correctly for voice commands.

## Usage

- **Voice Commands**: Say "Run Command - [some command]" to get the assistant to pick and run the specified command. Current actions [subject to expansion] are: Weather, Location
- **GUI Interface**: Access the simple dashboard by running `main.py`

## Contributing

This is a one-day project and not intended for further development. However, suggestions and feedback are welcome to inspire future projects or improvements.

## License

N/A

---

**Note**: This project is a proof of concept created within a single day. It's aimed at learning and demonstrating basic home automation concepts and is not intended for real-world application without significant enhancements and testing.