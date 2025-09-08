#Library used.
import random

# The phrase that the program has to achieve.
target_phrase = "METHINKS IT IS LIKE A WEASEL"

# Permited characters.
possible_characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ "

# Quantity of copies.
copies = 100

# The mutation rate.
mutation_rate = 5  # 5%

#Defs and functions on the program

def inicial_phrase (wheasel):
    
    #Creates a inicial completely string random with the same lenght of the target phrase.
    random_phrase = input("Enter a random phrase with 28 characters: ").upper()
    for _ in range(wheasel):
        random_phrase
    return random_phrase

def apply_mutation (father):
    
    #Recieves the phrase (the "father") and returns a new version with random mutations,
    #based on the mutation_rate.
    
    new_phrase = ""
    for character in father:
        if random.randint(1, 100) <= mutation_rate:
            # If the condition has been met, replaces the character for a random.
            new_phrase += random.choice(possible_characters)
        else:
            # Otherwise, keeps the original charactere.
            new_phrase += character
    return new_phrase

def assessment_of_phrase(phrase):
    
    # Compares a sentence with the target_phrase and returns a similarity score (fitness). 
    # The score is the number of characters that are in the correct position.
    position_number = 0
    for i in range(len(target_phrase)):
        if phrase[i] == target_phrase[i]:
            position_number += 1
    return  position_number

# Main executionS
def execute_simulation():
    
    # Main function that orchestrates and executes the evolutionary cycle of the Doninha Program.
    # Create the first random sentence ("Generation 0").
    close_phrase = inicial_phrase(len(target_phrase))
    close_position = assessment_of_phrase(close_phrase)
    generation_counter = 0

    print("--- STARTING THE SIMULATION---")
    print(f"Generation {generation_counter}: Position Numbers={close_position}/{len(target_phrase)},Phrase='{close_phrase}'")

    # Main loop
    while close_position < len(target_phrase):
        generation_counter += 1
        # Creates a list
        generation_copies = []
        for _ in range(copies):
            mutant_copies = apply_mutation(close_phrase)
            generation_copies.append(mutant_copies)

        # Avalia cada cópia e encontra a melhor da geração atual.
        for copy in generation_copies:
            current_position = assessment_of_phrase(copy)
            # If the position of the copy is closer to the
            #  phrase than the current one,
            # it becomes the new close position for the next generation.
            if current_position > close_position:
                close_position = current_position
                close_phrase = copy

        # Print the progress
        print(
            f"Generation {generation_counter}: Position Number={close_position}
            /{len(target_phrase)}, Phrase='{close_phrase}'"
        )

    print("\n=== SIMULATION COMPLETE! ===")

# =========ENTRANCE OF THE PROGRAM=========
# Ensures that the function execute_simulation() is called when the file is executed.
if __name__ == "__main__":
    execute_simulation()
