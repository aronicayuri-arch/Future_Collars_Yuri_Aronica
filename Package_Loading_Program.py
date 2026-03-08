# Ask for maximum number of items
max_items = int(input("Enter maximum number of items to ship: "))

# Variables to track
current_package_weight = 0
packages = []
count = 0

print("\nEnter item weights one by one (0 to stop):")

while count < max_items:
    weight = int(input("Weight (1–10 or 0 to stop): "))

    if weight == 0:
        break  # stop early

    if weight < 1 or weight > 10:
        print("Invalid weight, must be 1–10. This item is skipped.")
        count = count + 1
        continue

    # If adding the weight goes above 20
    if current_package_weight + weight > 20:
        packages.append(current_package_weight)
        current_package_weight = weight
    else:
        current_package_weight = current_package_weight + weight

    count = count + 1

# If there is leftover weight in a package
if current_package_weight > 0:
    packages.append(current_package_weight)

# Now calculate statistics
num_packages = len(packages)
total_weight_sent = 0

for w in packages:
    total_weight_sent = total_weight_sent + w

total_capacity = num_packages * 20
total_unused_capacity = total_capacity - total_weight_sent

# Find the package with the most unused capacity
most_unused = -1
most_unused_index = 0
i = 0

for w in packages:
    unused = 20 - w
    if unused > most_unused:
        most_unused = unused
        most_unused_index = i
    i = i + 1

# Print results
print("\n--- SUMMARY ---")
print("Number of packages sent:", num_packages)
print("Total weight of packages:", total_weight_sent)
print("Total unused capacity:", total_unused_capacity)

if num_packages > 0:
    print(
        "Package with most unused capacity:",
        most_unused_index + 1,
        "(" + str(most_unused) + " kg unused)"
    )
print("----------------")

