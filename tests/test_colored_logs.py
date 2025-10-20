"""Test colored logging output."""
from lyricflow.utils.logging import setup_logger
import logging

# Setup logger with colors
logger = setup_logger(name="test", level=logging.DEBUG, verbose=True)

print("\n" + "=" * 60)
print("Testing Colored Logs")
print("=" * 60 + "\n")

# Test different log levels
logger.debug("This is a DEBUG message - showing detailed information")
logger.info("This is an INFO message - normal operation")
logger.warning("This is a WARNING message - something to pay attention to")
logger.error("This is an ERROR message - something went wrong")
logger.critical("This is a CRITICAL message - serious problem!")

print("\n" + "=" * 60)
print("All log levels displayed above")
print("=" * 60 + "\n")
