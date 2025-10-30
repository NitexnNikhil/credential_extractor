import re
import csv
from pathlib import Path

class DataExtractor:
    def __init__(self, input_file, output_file='extracted_data.csv'):
        self.input_file = input_file
        self.output_file = output_file

        # Regex patterns
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        self.deepgram_pattern = r'DEEPGRAM_API_KEY\s*=\s*([A-Za-z0-9]{10,})'
        self.project_id_pattern = r'PROJECT_ID\s*=\s*([A-Za-z0-9\-]{20,})'


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
        cleaned_emails = [email[5:] if email.lower().startswith("mail-") else email for email in emails]
        return list(dict.fromkeys(cleaned_emails))  # Remove duplicates

    def extract_deepgram_keys(self, text):
        """Extract DEEPGRAM_API_KEY values."""
        raw_keys = re.findall(self.deepgram_pattern, text)
        valid_keys = [key for key in raw_keys if len(key) == 40]
        invalid_keys = [key for key in raw_keys if len(key) != 40]
        for key in invalid_keys:
            print(f"❌ Invalid DEEPGRAM_API_KEY found: {key}")
        return list(dict.fromkeys(valid_keys))

    def extract_project_ids(self, text):
        """Extract all PROJECT_ID values."""
        project_ids = re.findall(r'PROJECT_ID\s*=\s*([A-Za-z0-9\-]{20,})', text)
        if not project_ids:
            print("⚠️ No PROJECT_ID found.")
        return list(dict.fromkeys(project_ids))

    def extract_all(self):
        """Extract all required data."""
        content = self.read_file()
        if content is None:
            return None

        print("\n--- Extraction Summary ---")
        emails = self.extract_emails(content)
        keys = self.extract_deepgram_keys(content)
        project_ids = self.extract_project_ids(content)

        print(f"✅ Emails found: {len(emails)}")
        print(f"✅ DEEPGRAM_API_KEYs found: {len(keys)}")
        print(f"✅ PROJECT_IDs found: {len(project_ids)}")

        return {
            'emails': emails,
            'deepgram_keys': keys,
            'project_ids': project_ids
        }

    def save_to_csv(self, data):
        """Save extracted data to CSV."""
        if not data:
            print("No data to save.")
            return

        max_len = max(len(data['emails']), len(data['deepgram_keys']), len(data['project_ids']))
        rows = []

        for i in range(max_len):
            rows.append({
                'email': data['emails'][i] if i < len(data['emails']) else '',
                'PROJECT_ID': data['project_ids'][i] if i < len(data['project_ids']) else '',
                'DEEPGRAM_API_KEY': data['deepgram_keys'][i] if i < len(data['deepgram_keys']) else ''
            })

        try:
            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                # ✅ Corrected header order
                writer = csv.DictWriter(f, fieldnames=['email', 'PROJECT_ID', 'DEEPGRAM_API_KEY'])
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
    output_file = 'deepgram_data.csv'

    if not Path(input_file).exists():
        print(f"❌ File '{input_file}' not found in directory: {Path.cwd()}")
        return

    extractor = DataExtractor(input_file, output_file)
    extractor.run()


if __name__ == '__main__':
    main()
