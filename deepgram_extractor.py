import re
import csv
from pathlib import Path

class DataExtractor:
    def __init__(self, input_file, output_file='extracted_data.csv'):
        self.input_file = input_file
        self.output_file = output_file

        # Regex patterns
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        self.deepgram_pattern = r'DEEPGRAM_API_KEY\s*=\s*([A-Za-z0-9]{10,})'  # match long strings first

    def read_file(self):
        """Read the input file."""
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"❌ Error: File '{self.input_file}' not found.")
            return None
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return None

    def extract_emails(self, text):
        """Extract and clean email addresses."""
        emails = re.findall(self.email_pattern, text)
        cleaned_emails = []

        for email in emails:
            if email.lower().startswith("mail-"):
                email = email[5:]  # remove 'Mail-' prefix
            cleaned_emails.append(email)

        # Remove duplicates while preserving order
        return list(dict.fromkeys(cleaned_emails))

    def extract_deepgram_keys(self, text, emails):
        """Extract DEEPGRAM_API_KEY values and validate their length."""
        raw_keys = re.findall(self.deepgram_pattern, text)
        valid_keys = []

        for idx, key in enumerate(raw_keys):
            if len(key) == 40:
                valid_keys.append(key)
            else:
                email = emails[idx] if idx < len(emails) else "unknown email"
                print(f"❌ {key} (invalid key) not fetched with {email}")

        return list(dict.fromkeys(valid_keys))

    def extract_all(self):
        """Extract all required data."""
        content = self.read_file()
        if content is None:
            return None

        print("\n--- Extraction Summary ---")
        emails = self.extract_emails(content)
        keys = self.extract_deepgram_keys(content, emails)

        print(f"✅ Emails found: {len(emails)}")
        print(f"✅ Valid DEEPGRAM_API_KEYs found: {len(keys)}")

        return {'emails': emails, 'deepgram_keys': keys}

    def save_to_csv(self, data):
        """Save extracted data to CSV."""
        if not data:
            print("No data to save.")
            return

        max_len = max(len(data['emails']), len(data['deepgram_keys']))
        rows = []

        for i in range(max_len):
            rows.append({
                'email': data['emails'][i] if i < len(data['emails']) else '',
                'DEEPGRAM_API_KEY': data['deepgram_keys'][i] if i < len(data['deepgram_keys']) else ''
            })

        try:
            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['email', 'DEEPGRAM_API_KEY'])
                writer.writeheader()
                writer.writerows(rows)
            print(f"\n✅ Data successfully saved to '{self.output_file}' ({len(rows)} rows).")
        except Exception as e:
            print(f"❌ Error writing CSV: {e}")

    def run(self):
        """Main runner."""
        print(f"Reading from: {self.input_file}")
        data = self.extract_all()
        if data:
            self.save_to_csv(data)


def main():
    input_file = 'deepgram_keys.txt'
    output_file = 'deepgram_keys.csv'

    if not Path(input_file).exists():
        print(f"❌ File '{input_file}' not found in directory: {Path.cwd()}")
        return

    extractor = DataExtractor(input_file, output_file)
    extractor.run()


if __name__ == '__main__':
    main()
