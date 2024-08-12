import config
import pandas as pd
from fuzzywuzzy import fuzz, process

def load_data(input_file):
    return pd.read_excel(input_file)

def save_data(data, output_file):
    data.to_excel(output_file, index=False)

def safe_fuzz_ratio(str1, str2):
    """Handle nulls for fuzzy matching safely."""
    if pd.isna(str1) or pd.isna(str2):
        return 0
    return fuzz.ratio(str1, str2)


def calculate_score(first_contact, second_contact):
    first_name_score = safe_fuzz_ratio(first_contact['name'], second_contact['name'])
    last_name_score = safe_fuzz_ratio(first_contact['name1'], second_contact['name1'])
    email_score = safe_fuzz_ratio(first_contact['email'], second_contact['email']) if first_contact['email'] and second_contact['email'] else 0

    zip_code_score = 0
    if pd.notna(first_contact.get('postalZip')) and pd.notna(second_contact.get('postalZip')):
        zip_code_score = 100 if first_contact['postalZip'] == second_contact['postalZip'] else 0

    address_score = safe_fuzz_ratio(first_contact['address'], second_contact['address']) if first_contact['address'] and second_contact['address'] else 0

    weighted_score = (first_name_score * config.FIRST_NAME_WEIGHT +
                      last_name_score * config.LAST_NAME_WEIGHT +
                      email_score * config.EMAIL_WEIGHT +
                      zip_code_score * config.ZIP_CODE_WEIGHT +
                      address_score * config.ADDRESS_WEIGHT)

    return weighted_score

def find_potential_duplicates(df):
    results = []

    for i, first_contact in df.iterrows():
        for j, second_contact in df.iterrows():
            if i >= j:
                continue
            score = calculate_score(first_contact, second_contact)
            if score <= config.POTENTIAL_DUPLICATES_LOW_THREASHOLD:
                results.append({
                    'contact-id-source': first_contact['contactID'],
                    'contact-id-match': second_contact['contactID'],
                    'accuracy': 'LOW'
                })

            if score > config.POTENTIAL_DUPLICATES_LOW_THREASHOLD and score < config.POTENTIAL_DUPLICATES_MEDIUM_THREASHOLD:
                results.append({
                    'contact-id-source': first_contact['contactID'],
                    'contact-id-match': second_contact['contactID'],
                    'accuracy': 'MEDIUM'
                })

            if score > config.POTENTIAL_DUPLICATES_MEDIUM_THREASHOLD:
                results.append({
                    'contact-id-source': first_contact['contactID'],
                    'contact-id-match': second_contact['contactID'],
                    'accuracy': 'HIGH'
                })

    return pd.DataFrame(results)

def main(input_file, output_file):
    df = load_data(input_file)
    potential_duplicates = find_potential_duplicates(df)
    save_data(potential_duplicates, output_file)

if __name__ == "__main__":
    input_file = "contacts.xlsx"
    output_file = "potential_duplicates.xlsx"
    main(input_file, output_file)