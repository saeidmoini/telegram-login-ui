import logging

# Create a custom logger
logger = logging.getLogger("telegram_client")  # Use a unique name for your app's logger
logger.setLevel(logging.DEBUG)  # Set the logging level for your logger

# Create handlers for file and console
file_handler = logging.FileHandler("app.log")  # Log to a file
console_handler = logging.StreamHandler()  # Log to the console

# Define a logging format
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to the custom logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Prevent the root logger from duplicating messages
logger.propagate = False

