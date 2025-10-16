def create_shaded_list():
    # Ask the user for the start and end of the range
    start = int(input("Enter the start of the range: "))
    end = int(input("Enter the end of the range: "))

    # Ask for a two-digit integer suffix
    suffix = int(input("Enter a two-digit integer suffix: "))

    # Ensure the suffix is two digits
    if not (0 <= suffix <= 99):
        print("The suffix must be a two-digit integer.")
        return

    shade_color = input("Enter the shade color: ")

    shade_type = input("Enter the shade type (S, F, N): ")

    # Create a list to store the results
    result_list = []

    # Calculate the new values and add them to the list
    for number in range(start, end + 1):
        new_number = number * 100 + suffix
        result_list.append(new_number)

    result_list.extend([shade_color, f"{shade_type}{suffix}"])

    # Print the resulting list
    print(f"{','.join([str(num) for num in result_list])}")


# Run the function
create_shaded_list()
