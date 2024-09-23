import json
import sys
import re

# Function to load the JSON data from a file
def load_json_data(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

# Function to extract the conditions from the starting conditions list
def extract_conditions(starting_conds):
    conditions = []
    for cond in starting_conds:
        if cond.startswith("IsTool"):
            conditions.append(cond.split("=")[0][6:])  # Strip "IsTool" and keep the key intact
        elif cond.startswith("Is") and not cond.startswith("IsCategory"):
            conditions.append(cond.split("=")[0][2:])  # Strip "Is" and keep the key intact
    return ", ".join(conditions)

# Function to extract the category from the starting conditions
def extract_category(starting_conds):
    for cond in starting_conds:
        if cond.startswith("IsCategory"):
            return cond.split("=")[0][10:]  # Strip "IsCategory" and keep the key intact
    return "Unknown"

# Function to extract all Stat fields dynamically and clip the "Stat" prefix
def extract_stats(starting_conds):
    stats = {}
    stat_keys = []
    for cond in starting_conds:
        if cond.startswith("Stat"):
            key = cond.split("=")[0][4:]  # Remove "Stat" prefix
            value = cond.split("x")[-1]  # Extract the value after "x"
            stats[key] = value
            stat_keys.append(key)  # Collect keys for the Stats list
    return stats, stat_keys

# Function to generate an infobox based on the JSON data
def generate_infobox(data):
    name = data.get("strNameFriendly", "Unknown")
    item_def = data.get("strItemDef", "Unknown")
    category = extract_category(data.get("aStartingConds", []))
    
    # Extract all Stat fields and clip "Stat"
    stats, stat_keys = extract_stats(data.get("aStartingConds", []))
    
    # Other fields
    portrait = data.get("strPortraitImg", "Unknown")
    conditions = extract_conditions(data.get("aStartingConds", []))
    interactions = ", ".join(data.get("aInteractions", []))
    description = data.get("strDesc", "No description available.")
    
    # Generate the Stats list as a comma-separated string
    stats_list = ", ".join(stat_keys)

    # Generate the quote block
    quote_block = f"{{{{Quote|{description}|Item description}}}}\n"

    # Generate the infobox string
    infobox = f"""
{{{{Infobox item
|images=
    {portrait}.png:Intact,
    {portrait}Dmg.png:Damaged
| Name                = {name}
| Type                = {data.get("strType", "Unknown")}
| Category            = {category}
| ItemDefinition      = {item_def}
| Interactions        = {interactions}
| Conditions          = {conditions}
| Stats               = {stats_list}
"""
    # Add Stat fields dynamically (without "Stat" prefix)
    for key, value in stats.items():
        infobox += f"| {key} = {value}\n"

    infobox += f"| Portrait            = {portrait}\n}}}}\n"
    return quote_block + infobox.strip()

# Main function to run the script
def main():
    if len(sys.argv) != 3:
        print("Usage: python generate_infobox.py <strName> <json_file>")
        sys.exit(1)

    str_name = sys.argv[1]
    json_file = sys.argv[2]

    data = load_json_data(json_file)

    matching_item = next((item for item in data if item["strName"] == str_name), None)

    if not matching_item:
        print(f"Item with strName '{str_name}' not found in {json_file}.")
        sys.exit(1)

    infobox = generate_infobox(matching_item)
    print(infobox)

if __name__ == "__main__":
    main()
