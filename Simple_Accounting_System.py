balance = 0
warehouse = {}
operations = []

# Show available commands
print("Available commands:")
print("balance  sale  purchase  account  list  warehouse  review  end")

command = ""

# Main loop
while command != "end":
    command = input("\nEnter command: ")

    # balance
    if command == "balance":
        amount_str = input("Enter amount to change the balance (+ or -): ")
        if amount_str.lstrip("+-").isdigit():
            amount = int(amount_str)
            balance = balance + amount
            operations.append("Balance change " + str(amount))
            print("Balance updated.")
        else:
            print("Invalid amount, must be a number.")

    # sale
    if command == "sale":
        product = input("Product name: ")
        price_str = input("Price: ")
        qty_str = input("Quantity: ")

        if price_str.isdigit() and qty_str.isdigit():
            price = int(price_str)
            qty = int(qty_str)

            # check if in warehouse
            if product in warehouse and warehouse[product]["qty"] >= qty:
                total = price * qty
                balance = balance + total
                warehouse[product]["qty"] = warehouse[product]["qty"] - qty
                operations.append("Sale " + product + " " + str(price) + " " + str(qty))
                print("Sale completed.")
            else:
                print("Not enough product in warehouse.")
        else:
            print("Invalid price or quantity.")

    # purchase
    if command == "purchase":
        product = input("Product name: ")
        price_str = input("Price: ")
        qty_str = input("Quantity: ")

        if price_str.isdigit() and qty_str.isdigit():
            price = int(price_str)
            qty = int(qty_str)
            total = price * qty

            if balance >= total:
                balance = balance - total
                if product not in warehouse:
                    warehouse[product] = {"price": price, "qty": 0}
                warehouse[product]["qty"] = warehouse[product]["qty"] + qty
                operations.append("Purchase " + product + " " + str(price) + " " + str(qty))
                print("Purchase completed.")
            else:
                print("Not enough balance.")
        else:
            print("Invalid price or quantity.")

    # account
    if command == "account":
        print("Current balance:", balance)

    # list
    if command == "list":
        if len(warehouse) == 0:
            print("Warehouse is empty.")
        else:
            print("Warehouse inventory:")
            for p in warehouse:
                print(p, "Price:", warehouse[p]["price"], "Qty:", warehouse[p]["qty"])

    # warehouse
    if command == "warehouse":
        product = input("Enter product name: ")
        if product in warehouse:
            print(product, "Price:", warehouse[product]["price"], "Qty:", warehouse[product]["qty"])
        else:
            print("Product not found.")

    # review
    if command == "review":
        print("Enter from index (or blank):")
        fr = input()
        print("Enter to index (or blank):")
        to = input()

        if fr == "" and to == "":
            # show all
            for i in range(len(operations)):
                print(i, operations[i])

        else:
            if fr.isdigit() and to.isdigit():
                fr_i = int(fr)
                to_i = int(to)
                if fr_i >= 0 and to_i < len(operations) and fr_i <= to_i:
                    for i in range(fr_i, to_i + 1):
                        print(i, operations[i])
                else:
                    print("Index range out of bounds.")
            else:
                print("Invalid indices.")

    # end
    if command == "end":
        print("Program terminated.")

    # unknown
    if (command != "balance" and command != "sale" and
        command != "purchase" and command != "account" and
        command != "list" and command != "warehouse" and
        command != "review" and command != "end"):
        print("Unknown command.")
