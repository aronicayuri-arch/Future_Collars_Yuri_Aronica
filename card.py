
from datetime import datetime

# Get current year
current_year = datetime.now().year

# 1. Prompt user for required information
recipient_name = input("Enter the recipient's name: ")
year_of_birth = input("Enter the recipient's year of birth (e.g., 2000): ")
personal_message = input("Enter your personalized message: ")
sender_name = input("Enter the sender's name: ")

# 2. Calculate age (ensure proper conversion)
age = current_year - int(year_of_birth)

# 3. Generate and display the personalized birthday card
print("\n" + "="*40 + "\n")
print(f"{recipient_name}, let's celebrate your {age} years of awesomeness!")
print(f"Wishing you a day filled with joy and laughter as you turn {age}!\n")
print(f"{personal_message}\n")
print("With love and best wishes,")
print(f"{sender_name}")
print("\n" + "="*40)



