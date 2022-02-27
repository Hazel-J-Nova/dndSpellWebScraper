
import sys
# note: Python versions before 3.3 don't have sys.base_prefix
# if you're not in virtual environment
running_in_virtualenv = sys.prefix != sys.base_prefix
print(running_in_virtualenv)
