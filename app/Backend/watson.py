
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()


import time

class WatsonAssistantSimple:
    def __init__(self):
        print("Setting up WatsonX REST API integration...")
        self.url = os.getenv("WATSON_URL")
        self.api_key = os.getenv("WATSON_API_KEY")
        self.project_id = os.getenv("WATSON_ASSISTANT_ID")
        self.model_id = "ibm/granite-3-8b-instruct"  # You can make this configurable
        if not self.url or not self.api_key or not self.project_id:
            raise ValueError("Missing WatsonX credentials in .env file")
        self.access_token = None
        self.token_expiry = 0
        self.conversations = {}
        print("WatsonX REST API is ready!")

    def get_access_token(self):
        # Only fetch if missing or expired
        if self.access_token and time.time() < self.token_expiry - 60:
            return self.access_token
        print("Fetching new IBM Cloud IAM access token...")
        url = "https://iam.cloud.ibm.com/identity/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": self.api_key
        }
        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            token_data = response.json()
            self.access_token = token_data["access_token"]
            expires_in = token_data.get("expires_in", 3600)
            self.token_expiry = time.time() + expires_in
            print("Token fetched, expires in", expires_in, "seconds.")
            return self.access_token
        except Exception as e:
            print("Failed to fetch IAM token:", e)
            raise
    
    def start_conversation(self, conversation_id):
        print(f"Starting new conversation: {conversation_id}")
        self.conversations[conversation_id] = {
            'history': [],
            'collected_data': {},
            'message_count': 0
        }
        return conversation_id
    
    def send_message(self, conversation_id, user_message):
        if conversation_id not in self.conversations:
            self.start_conversation(conversation_id)
        conv = self.conversations[conversation_id]
        conv['message_count'] += 1
        conv['history'].append({"role": "user", "content": user_message})
        print(f"\nUser: {user_message}")

        # Prepare payload for WatsonX REST API
        body = {
            "messages": conv['history'],
            "project_id": self.project_id,
            "model_id": self.model_id,
            "frequency_penalty": 0,
            "max_tokens": 2000,
            "presence_penalty": 0,
            "temperature": 0,
            "top_p": 1
        }
        token = self.get_access_token()
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        watson_text = None
        try:
            response = requests.post(self.url, headers=headers, json=body)
            response.raise_for_status()
            data = response.json()
            # Extract response text
            watson_text = self._get_watsonx_text(data)
        except Exception as error:
            print(f"WatsonX API error: {error}")
            watson_text = self._generate_local_response(user_message, conv['collected_data'])

        print(f"Assistant: {watson_text}")
        new_data = self._extract_data_from_message(user_message)
        conv['collected_data'].update(new_data)
        print(f"Data collected: {conv['collected_data']}")
        is_complete = self.check_if_complete(conv['collected_data'])
        if is_complete:
            print("All data collected!")
        return {
            'watson_response': watson_text,
            'collected_data': conv['collected_data'].copy(),
            'is_complete': is_complete
        }
    

    def _get_watsonx_text(self, watsonx_response):
        # Extracts the text from WatsonX REST API response
        try:
            choices = watsonx_response.get('choices', [])
            if choices and 'message' in choices[0]:
                return choices[0]['message'].get('content', "I understand.")
        except Exception as e:
            print(f"Failed to parse WatsonX response: {e}")
        return "I understand."
    
    def _generate_local_response(self, user_message, collected_data):
        """Generate a response locally when Watson API is not available"""
        
        # Simple response generation based on what data we still need
        missing = []
        
        if 'household_size' not in collected_data:
            missing.append("household size")
        if 'monthly_income' not in collected_data:
            missing.append("monthly income")
        if 'age' not in collected_data:
            missing.append("age")
        
        if missing:
            return f"Thank you. Could you also tell me your {missing[0]}?"
        else:
            return "Thank you for providing that information. I have everything I need."
    
    def _extract_data_from_message(self, user_message):

        """Extract data from user message (no regex version)"""
        found_data = {}
        text = user_message.lower()

    
    #  Household size extraction
        words = text.split()
        for i, w in enumerate(words):
            if w.isdigit():
                if any(k in words[i+1:i+3] for k in ['people', 'person', 'members', 'member']):
                    found_data['household_size'] = int(w)
                    print(f"  Found household size: {w}")
                    break
            if w in ['family', 'household']:
                next_num = next((n for n in words[i+1:] if n.isdigit()), None)
                if next_num:
                    found_data['household_size'] = int(next_num)
                    print(f"  Found household size: {next_num}")
                    break

        # Income extraction
        income_words = ['income', 'salary', 'make', 'earn', 'pay', 'month', 'weekly', 'per month']
        symbols = ['$', 'usd']
        tokens = text.replace(',', '').split()

        # Try to detect a number after a money symbol or context word
        for i, w in enumerate(tokens):
            # Case 1: "$2000"
            if w.startswith('$') and w[1:].replace('.', '').isdigit():
                found_data['monthly_income'] = float(w[1:])
                print(f"  Found income: ${found_data['monthly_income']}")
                break

            # Case 2: "income 2000" or "earn 3000"
            if w in income_words and i + 1 < len(tokens):
                nxt = tokens[i + 1]
                if nxt.replace('.', '').isdigit():
                    found_data['monthly_income'] = float(nxt)
                    print(f"  Found income: ${found_data['monthly_income']}")
                    break

            # Case 3: "I make 2000 dollars"
            if w.isdigit() and any(k in tokens[i+1:i+3] for k in ['dollar', 'dollars', 'month', 'monthly']):
                found_data['monthly_income'] = float(w)
                print(f"  Found income: ${found_data['monthly_income']}")
                break

        # Age extraction 
        for w in text.split():
            if w.isdigit():
                age = int(w)
                if 10 < age < 120:
                    found_data['age'] = age
                    print(f"  Found age: {age}")
                    break

        # Employment detection
        if any(word in text for word in ['employed', 'working', 'job', 'work full', 'work part']):
            found_data['is_employed'] = True
            print("  Found employment: True")
        elif any(word in text for word in ['unemployed', 'not working', 'no job', "don't work"]):
            found_data['is_employed'] = False
            print("  Found employment: False")

        # Assets/savings detection
        if '$' in text or 'savings' in text or 'saved' in text:
            for t in tokens:
                if t.startswith('$') and t[1:].isdigit():
                    found_data['assets'] = float(t[1:])
                    print(f"  Found assets: ${found_data['assets']}")
                    break
                elif t.isdigit() and 'saving' in text:
                    found_data['assets'] = float(t)
                    print(f"  Found assets: ${found_data['assets']}")
                    break

        # Yes/No responses
        yes_words = ['yes', 'yeah', 'yep', 'sure', 'correct']
        no_words = ['no', 'nope', 'negative']

        if text.strip() in yes_words:
            found_data['_last_yes_no'] = True
        elif text.strip() in no_words:
            found_data['_last_yes_no'] = False

        return found_data

    
    def check_if_complete(self, data):
        """Check if we have all required information"""
        
        required_fields = ['household_size', 'monthly_income', 'age']
        
        for field in required_fields:
            if field not in data or data[field] is None:
                return False
        
        # Set defaults for optional fields
        if 'assets' not in data:
            data['assets'] = 0
        if 'is_employed' not in data:
            data['is_employed'] = False
        if 'has_children' not in data:
            data['has_children'] = data.get('household_size', 1) > 1
        if 'has_disability' not in data:
            data['has_disability'] = False
        
        return True
    
    def end_conversation(self, conversation_id):
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            print(f"Ended conversation: {conversation_id}")


def test():
    """Test Watson Assistant"""
    print(" TESTING WATSON ASSISTANT")
    
    try:
        watson = WatsonAssistantSimple()
    except ValueError as e:
        print(f"\n {e}")
        return
    
    test_messages = [
        "Hi",
        "John",
        "4 people",
        "$2000 a month",
        "Yes I work",
        "About $500 in savings",
        "I am 35",
        "Yes I am a citizen"
    ]
    
    conv_id = "test_conversation_001"
    
    for i, message in enumerate(test_messages, start=1):
        print(f"\n--- Turn {i} ---")
        
        # Send message to Watson
        result = watson.send_message(conv_id, message)
        
        if result['is_complete']:
            print("All data collected!")
            print("Final data:", json.dumps(result['collected_data'], indent=2))
            break
    
    watson.end_conversation(conv_id)
    print("\nTest Complete!")


if __name__ == '__main__':
    test()