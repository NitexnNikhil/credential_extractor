import re
import csv
from pathlib import Path

class DataExtractor:
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file
        
        # Enhanced regex patterns
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        self.url_pattern = r'(?:https?|wss?)://[^\s<>"{}|\\^`\[\]\',;]+'


    def read_file(self):
        """Read the input text file"""
        try:
            with open(self.input_file, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Error: File '{self.input_file}' not found.")
            return None
        except Exception as e:
            print(f"Error reading file: {e}")
            return None
    
    def extract_emails(self, text):
        """Extract all email addresses and clean unwanted prefixes"""
        emails = re.findall(self.email_pattern, text)
    
        # Clean prefix like 'Mail-' or 'mail-'
        cleaned_emails = []
        for email in emails:
            if email.lower().startswith("mail-"):
                email = email[5:]  # remove 'Mail-' prefix
            cleaned_emails.append(email)
        
        # Remove duplicates while preserving order
        return list(dict.fromkeys(cleaned_emails))

    
    def extract_urls(self, text):
        """Extract all URLs"""
        urls = re.findall(self.url_pattern, text)
        # Clean up URLs (remove trailing punctuation)
        cleaned_urls = []
        for url in urls:
            url = url.rstrip('.,;:)]}')
            cleaned_urls.append(url)
        return list(dict.fromkeys(cleaned_urls))  # Remove duplicates
    
    def extract_keys(self, text):
        """Extract API keys and secret keys with multiple strategies"""
        all_potential_keys = []
        api_keys = []
        secret_keys = []
        
        # Strategy 1: Extract ALL potential key-like strings (alphanumeric with special chars)
        # This will catch standalone keys like "QKodEq23IoaeeOvH5dXhAvFnTwhjce9jefqs8Bnx27"
        all_potential_keys = re.findall(r'\b[A-Za-z0-9_.\-*]{20,}\b', text)
        
        # Strategy 2: Look for key=value or key: value patterns
        api_key_patterns = [
            r'(?:LIVEKIT[_\s-]?)?API[_\s-]?KEY["\']?\s*[:=]\s*["\']?([A-Za-z0-9_.*-]{10,})["\']?',
            r'(?:LIVEKIT[_\s-]?)?APIKEY["\']?\s*[:=]\s*["\']?([A-Za-z0-9_.*-]{10,})["\']?',
        ]
        
        secret_key_patterns = [
            r'(?:LIVEKIT[_\s-]?)?SECRET[_\s-]?KEY["\']?\s*[:=]\s*["\']?([A-Za-z0-9_.*-]{10,})["\']?',
            r'(?:LIVEKIT[_\s-]?)?SECRETKEY["\']?\s*[:=]\s*["\']?([A-Za-z0-9_.*-]{10,})["\']?',
            r'(?:LIVEKIT[_\s-]?)?API[_\s-]?SECRET["\']?\s*[:=]\s*["\']?([A-Za-z0-9_.*-]{10,})["\']?',
            r'(?:LIVEKIT[_\s-]?)?APISECRET["\']?\s*[:=]\s*["\']?([A-Za-z0-9_.*-]{10,})["\']?',
        ]
        
        # Extract labeled API keys
        for pattern in api_key_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            api_keys.extend(matches)
        
        # Extract labeled Secret keys
        for pattern in secret_key_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            secret_keys.extend(matches)
        
        # Strategy 3: Line-by-line analysis
        lines = text.split('\n')
        for i, line in enumerate(lines):
            line_lower = line.lower()
            line_stripped = line.strip()
            
            if not line_stripped:
                continue
            
            # Check if this line or previous line has key indicators
            prev_line = lines[i-1].lower() if i > 0 else ""
            
            # Find all potential keys in this line
            line_keys = re.findall(r'\b[A-Za-z0-9_.\-*]{20,}\b', line)
            
            for key in line_keys:
                # Check if current or previous line mentions the key type
                combined_context = prev_line + " " + line_lower
                
                if 'api' in combined_context and 'key' in combined_context:
                    if 'secret' not in combined_context and key not in api_keys:
                        api_keys.append(key)
                
                if 'secret' in combined_context and 'key' in combined_context:
                    if key not in secret_keys:
                        secret_keys.append(key)
        
        # Strategy 4: If we found potential keys but couldn't categorize them,
        # try to infer based on position or common patterns
        categorized = set(api_keys + secret_keys)
        uncategorized = [k for k in all_potential_keys if k not in categorized]
        
        if uncategorized:
            # Look at the context around each uncategorized key
            for key in uncategorized:
                # Find the key in the text with surrounding context
                key_escaped = re.escape(key)
                context_match = re.search(r'.{0,100}' + key_escaped + r'.{0,100}', text, re.IGNORECASE)
                
                if context_match:
                    context = context_match.group().lower()
                    
                    if 'api' in context and 'key' in context and 'secret' not in context:
                        if key not in api_keys:
                            api_keys.append(key)
                    elif 'secret' in context:
                        if key not in secret_keys:
                            secret_keys.append(key)
                    # If no clear label, check for common prefixes
                    elif key.startswith(('API', 'api')):
                        if key not in api_keys:
                            api_keys.append(key)
                    elif key.startswith(('SK', 'sk', 'SECRET', 'secret')):
                        if key not in secret_keys:
                            secret_keys.append(key)
        
        # Remove duplicates while preserving order
        api_keys = list(dict.fromkeys(api_keys))
        secret_keys = list(dict.fromkeys(secret_keys))
        
        # Filter out URLs
        api_keys = [k for k in api_keys if not k.lower().startswith(('http', 'https', 'www'))]
        secret_keys = [k for k in secret_keys if not k.lower().startswith(('http', 'https', 'www'))]
        
        return api_keys, secret_keys
    
    def extract_all(self):
        """Extract all data from the file"""
        content = self.read_file()
        if content is None:
            return None
        
        print("\n--- Extraction Process ---")
        
        emails = self.extract_emails(content)
        print(f"Emails found: {len(emails)}")
        if emails:
            for email in emails[:3]:  # Show first 3
                print(f"  - {email}")
        
        urls = self.extract_urls(content)
        print(f"\nURLs found: {len(urls)}")
        if urls:
            for url in urls[:3]:  # Show first 3
                print(f"  - {url}")
        
        api_keys, secret_keys = self.extract_keys(content)
        print(f"\nAPI Keys found: {len(api_keys)}")
        if api_keys:
            for key in api_keys[:3]:  # Show first 3
                print(f"  - {key[:20]}..." if len(key) > 20 else f"  - {key}")
        
        print(f"\nSecret Keys found: {len(secret_keys)}")
        if secret_keys:
            for key in secret_keys[:3]:  # Show first 3
                print(f"  - {key[:20]}..." if len(key) > 20 else f"  - {key}")
        
        print("\n" + "-" * 30 + "\n")
        
        return {
            'emails': emails,
            'urls': urls,
            'api_keys': api_keys,
            'secret_keys': secret_keys
        }
    
    def save_to_csv(self, data):
        """Save extracted data to CSV file"""
        if data is None:
            print("No data to save.")
            return
        
        # Determine maximum length for rows
        max_len = max(
            len(data['emails']) if data['emails'] else 1,
            len(data['urls']) if data['urls'] else 1,
            len(data['api_keys']) if data['api_keys'] else 1,
            len(data['secret_keys']) if data['secret_keys'] else 1
        )
        
        # Prepare rows
        rows = []
        for i in range(max_len):
            row = {
                'email': data['emails'][i] if i < len(data['emails']) else '',
                'LIVE_KIT_URL': data['urls'][i] if i < len(data['urls']) else '',
                'LIVEKIT_API_KEYS': data['api_keys'][i] if i < len(data['api_keys']) else '',
                'LIVEKIT_SECRET_KEYS': data['secret_keys'][i] if i < len(data['secret_keys']) else ''
            }
            rows.append(row)
        
        # Write to CSV
        try:
            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['email', 'LIVE_KIT_URL', 'LIVEKIT_API_KEYS', 'LIVEKIT_SECRET_KEYS']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                writer.writeheader()
                writer.writerows(rows)
            
            print(f"✓ Data successfully extracted and saved to '{self.output_file}'")
            print(f"  - Total rows written: {len(rows)}")
        except Exception as e:
            print(f"Error writing to CSV: {e}")
    
    def run(self):
        """Main execution method"""
        print(f"Reading from: {self.input_file}")
        data = self.extract_all()
        if data:
            self.save_to_csv(data)


def main():
    # You can change these paths
    input_file = 'livekit_keys.txt'
    output_file = 'livekit_data.csv'
    
    # Check if file exists in current directory
    if not Path(input_file).exists():
        print(f"Error: '{input_file}' not found in current directory.")
        print(f"Current directory: {Path.cwd()}")
        print("\nPlease ensure your input file is in the same directory as this script,")
        print("or provide the full path to the file.")
        
        # List files in current directory
        print("\nFiles in current directory:")
        for file in Path.cwd().iterdir():
            if file.is_file():
                print(f"  - {file.name}")
        return
    
    extractor = DataExtractor(input_file, output_file)
    extractor.run()


if __name__ == '__main__':
    main()


