from nt import link
from lib.linkedin_wrapper import LinkedinWrapper

linkedin = LinkedinWrapper("productionadamh@gmail.com", "gptproject135764", debug=True)
profile = linkedin.get_profile("ACoAAEQa7lwBDUlhlFJn7LGu3KSFGDUjMMw9UQk")

print(profile)
