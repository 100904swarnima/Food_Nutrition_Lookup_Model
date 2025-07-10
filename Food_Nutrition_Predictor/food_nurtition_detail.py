import pandas as pd
from difflib import get_close_matches

# Load and preprocess CSV
df = pd.read_csv("Indian_Food_Nutrition_Processed.csv")

# Normalize column names (remove whitespace and lowercase)
df.columns = df.columns.str.strip().str.lower()

# Ensure food name column is correct
if 'dish name' not in df.columns:
    print("❌ 'dish name' column not found.")
    print("Available columns:", df.columns)
    exit()

# Clean dish names
df['dish name'] = df['dish name'].str.lower().str.strip()

def get_nutrition_info(food_name):
    food_name = food_name.lower().strip()

    if food_name in df['dish name'].values:
        result = df[df['dish name'] == food_name].iloc[0]
    else:
        matches = get_close_matches(food_name, df['dish name'], n=1, cutoff=0.6)
        if matches:
            print(f"🔍 Closest match: {matches[0].title()}")
            result = df[df['dish name'] == matches[0]].iloc[0]
        else:
            return "⚠️ No match found. Please check the name."

    # Format result
    output = f"\n🍽️ Dish: {result['dish name'].title()}\n"
    for col in df.columns:
        if col != 'dish name':
            output += f"{col.title()}: {result[col]}\n"
    return output

# Main loop
if __name__ == "__main__":
    print("=== Indian Food Nutrition Lookup ===")
    while True:
        food = input("\nEnter food name (or 'exit'): ")
        if food.lower() == 'exit':
            break
        print(get_nutrition_info(food))


