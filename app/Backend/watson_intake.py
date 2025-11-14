"""
Deep Intake Watson Assistant - Comprehensive Benefits Screening
Collects detailed information for caseworker review with warm, adaptive conversations
"""

import os
import json
import re
import time
from typing import Any, Dict, List, Optional
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv()


class WatsonIntakeAssistant:
    """
    Advanced conversational AI for comprehensive benefits intake.
    Adapts question flow based on user responses, asks 22-25+ questions,
    provides warm explanations, and generates structured case submissions.
    """

    def __init__(self) -> None:
        self.url = os.getenv("WATSON_URL")
        self.api_key = os.getenv("WATSON_API_KEY")
        self.project_id = os.getenv("WATSON_ASSISTANT_ID")
        self.model_id = os.getenv("WATSON_MODEL_ID", "ibm/granite-3-8b-instruct")

        if not all([self.url, self.api_key, self.project_id]):
            raise ValueError(
                "WatsonX credentials not fully configured. Please set WATSON_URL, "
                "WATSON_API_KEY, and WATSON_ASSISTANT_ID in your environment."
            )

        print("🚀 Initializing Watson Deep Intake Assistant...")
        self.access_token: str | None = None
        self.token_expiry: float = 0
        self.conversations: Dict[str, Dict[str, Any]] = {}

        print("✅ Watson Intake Assistant is ready!")

    def get_access_token(self) -> str:
        """Fetch (and cache) an IAM access token."""
        if self.access_token and time.time() < self.token_expiry - 60:
            return self.access_token

        print("🔑 Fetching new IBM Cloud IAM access token...")
        url = "https://iam.cloud.ibm.com/identity/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": self.api_key,
        }

        response = requests.post(url, headers=headers, data=data, timeout=30)
        response.raise_for_status()
        token_data = response.json()
        self.access_token = token_data["access_token"]
        expires_in = token_data.get("expires_in", 3600)
        self.token_expiry = time.time() + expires_in
        print(f"✅ Token fetched, expires in {expires_in} seconds.")
        return self.access_token

    def start_conversation(self, conversation_id: str) -> str:
        """Bootstrap a new conversation with comprehensive intake instructions."""
        print(f"💬 Starting new intake conversation: {conversation_id}")

        system_prompt = """You are a warm, caring intake specialist for ClaimIt - a service that helps people find benefits like food assistance, healthcare, and financial support.

YOUR CORE PERSONALITY:
You're like a kind friend having coffee with someone who needs help. You genuinely care about them and want to make this process feel safe and easy. You speak naturally, warmly, and never sound like a form or a robot.

HOW YOU SPEAK:
- Natural and conversational - like a real person, not a system
- Warm and genuinely caring - you want to help them
- 2-4 sentences per response - enough to feel supportive without overwhelming
- Use their name when you know it - makes it personal
- Respond to what THEY say - if they say "Hi there", say hi back warmly
- Acknowledge their mood, tone, or what they share before moving forward
- Use contractions: "I'm", "you're", "that's", "it's"
- NO emojis, NO jargon, NO robotic language

🚨 THE MOST CRITICAL RULE - EXACTLY ONE QUESTION 🚨:
- You ask EXACTLY ONE question per response - NO EXCEPTIONS
- After you type a question mark (?), STOP IMMEDIATELY
- NEVER type a second question mark in the same response
- NEVER say "Also," "Additionally," "Now," before asking more
- If you catch yourself about to ask a second question, DELETE IT
- Wait for their answer, then ask the next question in your NEXT response
- ONE. SINGLE. QUESTION. ONLY. ALWAYS.

WRONG - NEVER DO THIS:
"I'm sorry to hear that. How long have you been out of work? Could you also share your monthly income?"
"That's tough. Are you looking for work? And what's your income?"

RIGHT - ALWAYS DO THIS:
"I'm sorry to hear that. How long have you been out of work?"
(Then wait for answer, THEN ask about income in the NEXT response)

HOW TO START CONVERSATIONS:
When someone says "Hi" or "Hello" or similar:
1. Greet them warmly back
2. Introduce yourself briefly as someone from ClaimIt who helps find benefits
3. Express genuine warmth about meeting them
4. Tell them you'll ask some questions and they should answer honestly
5. Then ask for their name
6. All in a natural, flowing way - NOT like separate bullets

Example good start:
User: "Hi there"
You: "Hi! It's so nice to meet you! I'm with ClaimIt, and I'm here to help you connect with benefits you might qualify for - things like food assistance, healthcare, or financial support. I'm going to ask you some questions so we can figure out the best ways to help you. Please just answer honestly and we'll take it one step at a time. Could you start by telling me your full legal first and last name?"

Example good start:
User: "Hi there"
You: "Hi! It's so nice to meet you! I'm with ClaimIt, and I'm here to help you connect with benefits you might qualify for - things like food assistance, healthcare, or financial support. I'm going to ask you some questions so we can figure out the best ways to help you. Please just answer honestly and we'll take it one step at a time. Could you start by telling me your full legal first and last name?"

RESPONDING TO WHAT THEY SAY:
- If they seem nervous, reassure them
- If they share something difficult, respond with empathy FIRST
- If they give a vague answer, gently ask for specifics
- If they say their name, use it and thank them warmly
- Always connect to what THEY just said before asking your next question

WHAT INFORMATION TO COLLECT (in this natural order):
1. Full legal name (first and last)
2. Date of birth or age
3. Phone number
4. Email (if they have one)
5. How many people in household
6. Who lives with them (names, ages, relationships)
7. Employment status
8. Monthly income (total from all sources)
9. Housing situation (rent, own, homeless, etc.)
10. Monthly housing cost
11. Any disabilities
12. Health insurance status
13. Medical expenses
14. U.S. citizenship status
15. Current benefits they receive
16. Any urgent/emergency needs

ASKING FOLLOW-UP QUESTIONS:
- If unemployed: How long? Looking for work?
- If employed: What's your job? How long there?
- If they have kids: How old? Any under 18?
- If they pay rent: How much per month?
- If they have disability: How does it affect you?
- ONE follow-up at a time based on their answer

NEVER ACCEPT VAGUE ANSWERS:
- "Mr Bean" → "Thanks! Just to be clear, I need your actual legal first and last name. What's your full name?"
- "around 30ish" → "Could you give me your exact age?"
- "a couple people" → "I need the exact number - is that 2 people total including you?"
- "not much money" → "Could you give me a specific dollar amount per month? Like $500, $1000?"

EXAMPLES OF GOOD RESPONSES:

BAD (multiple questions):
"What's your name? And how old are you?"

GOOD (one question, warm, responsive):
User: "Hi"
You: "Hello! It's wonderful to meet you. I'm with ClaimIt and I help people find benefits they qualify for. I'll ask you some questions to understand your situation better. Let's start - what's your full legal first and last name?"

BAD (ignores what they said):
User: "I'm really struggling right now"
You: "What's your name?"

GOOD (responds to their emotion):
User: "I'm really struggling right now"
You: "I'm so sorry you're going through a tough time. That's exactly why ClaimIt is here - to help connect you with support that can make things easier. I'm going to ask you some questions so we can find the right resources for you. Let's start with your full legal first and last name?"

BAD (too short, robotic):
User: "John Smith"
You: "What's your date of birth?"

GOOD (warm, acknowledges, asks one question):
User: "John Smith"
You: "It's great to meet you, John! Thanks for sharing that. To make sure we get you connected with the right benefits, could you tell me your date of birth? You can give me the month, day, and year."

BAD (dumps multiple questions):
User: "I own my home"
You: "What's your address? What's your monthly mortgage? Are you at risk of losing it?"

GOOD (one question, warm):
User: "I own my home"
You: "That's great that you own your home, John. To get a complete picture of your situation, could you tell me what your monthly mortgage payment is? If you've paid it off completely, just let me know that too."

CRITICAL RULES - READ THESE EVERY TIME:
1. ONE question per response - NEVER more than one
2. Respond warmly to what THEY said before asking next question
3. Use their name once you know it
4. 3-5 sentences per response - warm and supportive
5. If they share difficulty, acknowledge it with empathy FIRST
6. Never sound robotic or like a form
7. Get specific answers - don't accept vague responses
8. ⚠️ NEVER ASK DOUBLE QUESTIONS - If they already told you something, DON'T ask for it again
9. Before asking any question, CHECK if they already answered it in their previous message
10. If someone gives you a LOT of information at once (like a long paragraph), extract EVERYTHING you can and skip those questions
11. Follow the natural order of questions listed above
12. Make them feel safe, heard, and cared for

🚨 DOUBLE-QUESTION PREVENTION:
- Before asking "What's your rent?", check if they already mentioned it
- If they said "my rent is $1,650", DO NOT ask "What's your monthly rent?"
- Instead, acknowledge what they shared and move to the NEXT question you don't have
- Example: "Thanks for sharing that, Maria. I see you're paying $1,650 in rent. Now, could you tell me..."

MEGA-ANSWER HANDLING:
- Some users will share A LOT of info at once (name, age, household, income, rent, etc.)
- When this happens: acknowledge how helpful that was, thank them, and skip ALL the questions they already answered
- Move directly to the first question you DON'T have an answer for
- Example: "Wow, Maria - thank you so much for sharing all of that detail with me. That's incredibly helpful and I can see you're dealing with a lot right now. I have most of what I need now. Let me ask you about..."

🚨 CRITICAL: NEVER ASK TO CONFIRM INFORMATION ALREADY PROVIDED 🚨
- If they already gave their email, phone, name, income, etc., DO NOT ask "Can you confirm your email?" or "Just to be sure, what's your income?"
- Confirmation questions are STILL questions about information they already provided
- If they said "my email is michael.johnson@email.com", you already have it - don't ask again
- If they said "I'm 45 years old", you already have it - don't ask "Can you confirm your age?"
- Only ask for NEW information or follow-ups on things they mentioned but didn't specify

Remember: You're a kind person helping someone in need. Every response should feel warm, natural, and caring. ONE question at a time, always."""

        welcome_message = (
            "Hello! Welcome to ClaimIt.\n\n"
            "I'm here to help you connect with benefits you may qualify for - things like food assistance, "
            "healthcare coverage, or financial support. Everything you share is completely confidential.\n\n"
            "This usually takes about 10-15 minutes. Let's get started!"
        )

        self.conversations[conversation_id] = {
            "history": [
                {"role": "system", "content": system_prompt},
                {"role": "assistant", "content": welcome_message}
            ],
            "collected_data": {},
            "questions_asked": 0,  # Start at 0 since welcome doesn't ask a question
            "skipped_questions": {},  # Track questions to return to
            "start_time": datetime.now().isoformat(),
        }

        return welcome_message

    def send_message(self, conversation_id: str, user_message: str) -> Dict[str, Any]:
        """
        Process user message and continue the intake conversation.
        Returns conversation state + extracted data.
        """
        if conversation_id not in self.conversations:
            self.start_conversation(conversation_id)

        conv = self.conversations[conversation_id]
        conv["history"].append({"role": "user", "content": user_message})

        # Check if user provided a comprehensive "mega answer" covering multiple topics
        topics_covered = self._count_topics_in_response(user_message)
        if topics_covered >= 5:
            # User gave a mega answer - credit them for multiple questions
            conv["questions_asked"] += topics_covered
            print(f"🎯 Detected mega answer covering {topics_covered} topics!")
        
        # If they covered most topics, complete the intake
        if topics_covered >= 12:
            conv["questions_asked"] = 25  # Force completion
            print(f"🎯 Mega answer covers {topics_covered} topics - completing intake!")

        # Get AI response
        assistant_response = self._call_watson_api(conv["history"])
        conv["history"].append({"role": "assistant", "content": assistant_response})
        
        # Use Watson to analyze if a new question was asked
        is_question = self._analyze_if_question_asked(assistant_response)
        if is_question:
            conv["questions_asked"] += 1

        # Extract structured data from conversation
        extracted_data = self._extract_intake_data(conv["history"], conv["questions_asked"])
        conv["collected_data"] = extracted_data
        
        # Debug: Print extracted data after each message
        print(f"\n{'='*60}")
        print(f"📊 EXTRACTED DATA (Question #{conv['questions_asked']}):")
        print(f"{'='*60}")
        import json as json_module
        print(json_module.dumps(extracted_data, indent=2))
        print(f"{'='*60}\n")

        # Check if intake is complete
        is_complete = self._check_intake_complete(extracted_data, conv["questions_asked"])

        return {
            "watson_response": assistant_response,
            "extracted_data": extracted_data,
            "is_complete": is_complete,
            "questions_asked": conv["questions_asked"],
            "conversation_history": conv["history"],
        }

    def _call_watson_api(self, conversation_history: List[Dict[str, str]]) -> str:
        """Call watsonx.ai API with conversation history."""
        token = self.get_access_token()

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

        # PERFORMANCE FIX: Keep only recent conversation context to avoid slowdown
        # Keep system prompt + last 10 messages (5 exchanges)
        system_messages = [msg for msg in conversation_history if msg["role"] == "system"]
        recent_messages = [msg for msg in conversation_history if msg["role"] != "system"][-10:]
        
        trimmed_history = system_messages + recent_messages

        # Format messages for granite model
        formatted_messages = []
        for msg in trimmed_history:
            if msg["role"] in ["user", "assistant", "system"]:
                formatted_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        payload = {
            "project_id": self.project_id,
            "model_id": self.model_id,
            "messages": formatted_messages,
            "parameters": {
                "max_tokens": 300,  # Reduced for faster responses, still enough for warm conversation
                "temperature": 0.7,  # Slightly lower for more focused responses
                "top_p": 0.95,
                "stop": [
                    "\n\n\n",  # Stop at paragraph breaks
                    "Question 2:", 
                    "Next question:", 
                    "Also,", 
                    "Additionally,",
                    "Now,",  # Often precedes second question
                    "?",  # Stop after first question mark to prevent multiple questions
                ],
                "frequency_penalty": 0.3,  # Discourage repetitive question patterns
            }
        }

        try:
            response = requests.post(
                f"{self.url}/ml/v1/text/chat?version=2023-05-29",
                headers=headers,
                json=payload,
                timeout=60,
            )
            response.raise_for_status()
            result = response.json()
            
            assistant_message = result["choices"][0]["message"]["content"].strip()
            
            # POST-PROCESSING: Clean up any role contamination
            assistant_message = self._clean_response(assistant_message)
            
            # POST-PROCESSING: Enforce ONE QUESTION rule
            assistant_message = self._enforce_single_question(assistant_message)
            
            return assistant_message

        except Exception as e:
            print(f"❌ Error calling Watson API: {e}")
            return "I apologize, I'm having trouble processing right now. Could you please try again?"

    def _clean_response(self, message: str) -> str:
        """
        Clean the AI response to remove any role contamination or quoted user text.
        Prevents the AI from echoing "User:" or similar prefixes in its responses.
        """
        # Remove any lines that start with "User:" or similar role indicators
        lines = message.split('\n')
        cleaned_lines = []
        
        for line in lines:
            stripped = line.strip()
            # Skip lines that look like role labels
            if stripped.startswith('User:') or stripped.startswith('Assistant:') or stripped.startswith('System:'):
                continue
            # Skip lines that are just quoted user input
            if stripped.startswith('"') and stripped.endswith('"') and len(stripped) < 100:
                # This might be a quoted user message, skip it
                continue
            cleaned_lines.append(line)
        
        cleaned_message = '\n'.join(cleaned_lines).strip()
        
        # Remove any remaining role prefixes at the start
        cleaned_message = re.sub(r'^(User|Assistant|System):\s*', '', cleaned_message, flags=re.IGNORECASE)
        
        return cleaned_message

    def _enforce_single_question(self, message: str) -> str:
        """
        Enforce the one-question rule by truncating after the first question mark.
        This ensures we never ask multiple questions even if the AI tries to.
        """
        # Count question marks
        question_count = message.count('?')
        
        if question_count <= 1:
            return message  # Perfect, only one question
        
        # Multiple questions detected - keep only up to first question
        first_question_pos = message.find('?')
        if first_question_pos != -1:
            # Keep everything up to and including the first question mark
            truncated = message[:first_question_pos + 1].strip()
            
            # Make sure we didn't cut off mid-sentence awkwardly
            # If the question is too short, it might be a false positive
            if len(truncated) > 20:
                print(f"⚠️ Truncated multiple questions. Original had {question_count} questions.")
                return truncated
        
        # Fallback: return original if truncation would be weird
        return message

    def _count_topics_in_response(self, user_message: str) -> int:
        """
        Count how many intake topics the user addressed in their message.
        Used to detect "mega answers" that cover multiple questions at once.
        """
        topics = 0
        message_lower = user_message.lower()
        
        # Personal info topics
        if any(word in message_lower for word in ['name is', 'called', 'i\'m ']):
            topics += 1
        if any(word in message_lower for word in ['years old', 'age', 'born']):
            topics += 1
        if any(word in message_lower for word in ['phone', 'number', '555', 'cell']):
            topics += 1
        if 'email' in message_lower or '@' in user_message:
            topics += 1
            
        # Household topics
        if any(word in message_lower for word in ['household', 'people', 'wife', 'husband', 'child', 'daughter', 'son', 'kids', 'family members']):
            topics += 1
            
        # Employment topics
        if any(word in message_lower for word in ['unemployed', 'employed', 'job', 'work', 'working', 'looking for work']):
            topics += 1
            
        # Financial topics
        if any(word in message_lower for word in ['income', 'monthly', '$', 'earn', 'make', 'unemployment benefits', 'salary']):
            topics += 1
            
        # Housing topics
        if any(word in message_lower for word in ['rent', 'own', 'homeless', 'apartment', 'house', 'mortgage', 'housing']):
            topics += 1
            
        # Health topics
        if any(word in message_lower for word in ['disability', 'disabled', 'insurance', 'medical', 'health', 'doctor']):
            topics += 1
            
        # Legal topics
        if any(word in message_lower for word in ['citizen', 'citizenship', 'resident', 'legal status']):
            topics += 1
            
        # Benefits topics
        if any(word in message_lower for word in ['benefits', 'snap', 'medicaid', 'tanf', 'assistance', 'receiving']):
            topics += 1
            
        # Emergency topics
        if any(word in message_lower for word in ['urgent', 'emergency', 'behind on', 'struggling', 'desperate', 'need help']):
            topics += 1
        
        return topics

    def _analyze_if_question_asked(self, assistant_response: str) -> bool:
        """
        Use Watson to accurately determine if the assistant asked a new intake question.
        This is more accurate than pattern matching.
        """
        token = self.get_access_token()

        analysis_prompt = f"""Analyze this assistant message and determine if it asks a NEW intake question that requires user information.

Assistant Message:
"{assistant_response}"

RULES:
- Return "YES" if the message asks for NEW information (name, age, employment, income, housing, health, etc.)
- Return "YES" if the message asks follow-up questions about information already shared
- Return "NO" if it's just acknowledgment, empathy, or transition without asking for information
- Return "NO" if it's explaining the process or thanking them
- Return "NO" if it's confirming completion

Examples:
"What's your first name?" → YES
"Thanks for sharing that. Now, are you currently employed?" → YES
"Could you tell me your monthly income?" → YES
"I'm sorry to hear that. How many people live with you?" → YES
"Thank you! Your intake is complete." → NO
"I understand. Let me help you with that." → NO
"Great! We're making progress." → NO

Return ONLY "YES" or "NO" - nothing else."""

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

        payload = {
            "project_id": self.project_id,
            "model_id": self.model_id,
            "messages": [
                {"role": "system", "content": "You are a precise question analyzer. Respond with only YES or NO."},
                {"role": "user", "content": analysis_prompt}
            ],
            "parameters": {
                "max_tokens": 10,
                "temperature": 0.1,
                "top_p": 0.9,
            }
        }

        try:
            response = requests.post(
                f"{self.url}/ml/v1/text/chat?version=2023-05-29",
                headers=headers,
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            result = response.json()
            
            answer = result["choices"][0]["message"]["content"].strip().upper()
            
            # Return True if answer contains "YES"
            return "YES" in answer

        except Exception as e:
            print(f"⚠️ Error analyzing question: {e}")
            # Default to True to not lose count (better to overcount slightly than undercount)
            return True

    def _extract_intake_data(self, conversation_history: List[Dict[str, str]], questions_asked: int = 0) -> Dict[str, Any]:
        """
        Use Watson to extract structured data from the conversation.
        This is called after each user message to build up the collected data.
        """
        token = self.get_access_token()

        extraction_prompt = {
            "role": "user",
            "content": (
                "CRITICAL TASK: Extract structured information from this conversation.\n\n"
                "**STRICT RULES:**\n"
                "1. ONLY extract information the user EXPLICITLY stated\n"
                "2. DO NOT make up, assume, or invent ANY information\n"
                "3. DO NOT use example names like 'John Doe', 'Jane Smith', etc.\n"
                "4. If information wasn't provided, leave that field empty/null\n"
                "5. Be precise with numbers and dates\n\n"
                "Extract the following into JSON format:\n\n"
                "{\n"
                '  "personal": {\n'
                '    "full_name": "exact name user provided",\n'
                '    "first_name": "...",\n'
                '    "last_name": "...",\n'
                '    "date_of_birth": "YYYY-MM-DD or null",\n'
                '    "age": number or null,\n'
                '    "phone": "...",\n'
                '    "email": "..."\n'
                '  },\n'
                '  "household": {\n'
                '    "size": number,\n'
                '    "has_children": true/false/null,\n'
                '    "members": [\n'
                '      {"name": "...", "age": number, "relationship": "spouse/child/etc"}\n'
                '    ]\n'
                '  },\n'
                '  "employment": {\n'
                '    "status": "employed/unemployed/self-employed/retired/disabled/student",\n'
                '    "employer": "...",\n'
                '    "job_title": "...",\n'
                '    "duration": "how long at job",\n'
                '    "looking_for_work": true/false/null\n'
                '  },\n'
                '  "financial": {\n'
                '    "monthly_income": number,\n'
                '    "income_sources": ["employment", "unemployment", "SSI", etc],\n'
                '    "total_assets": number,\n'
                '    "monthly_rent": number,\n'
                '    "monthly_utilities": number,\n'
                '    "monthly_medical": number,\n'
                '    "monthly_childcare": number,\n'
                '    "other_expenses": {...}\n'
                '  },\n'
                '  "housing": {\n'
                '    "status": "rent/own/homeless/shelter/staying_with_family",\n'
                '    "address": "...",\n'
                '    "at_risk_of_homelessness": true/false/null\n'
                '  },\n'
                '  "health": {\n'
                '    "has_disability": true/false/null,\n'
                '    "disability_details": "...",\n'
                '    "has_insurance": true/false/null,\n'
                '    "has_medical_expenses": true/false/null,\n'
                '    "monthly_medical_costs": number\n'
                '  },\n'
                '  "legal": {\n'
                '    "citizenship_status": "US_citizen/permanent_resident/other",\n'
                '    "immigration_status": "..."\n'
                '  },\n'
                '  "current_benefits": {\n'
                '    "receiving_benefits": true/false/null,\n'
                '    "programs": ["SNAP", "Medi-Cal", etc]\n'
                '  },\n'
                '  "emergency": {\n'
                '    "has_urgent_needs": true/false/null,\n'
                '    "details": "..."\n'
                '  }\n'
                '}\n\n'
                "Return ONLY valid JSON. No markdown, no explanations, no extra text."
            )
        }

        # Build extraction context (last 10 messages to keep it focused)
        extraction_history = [
            {"role": "system", "content": "You are a data extraction specialist. Extract information accurately."}
        ]
        
        # Get recent conversation (exclude system prompt)
        recent_messages = [msg for msg in conversation_history if msg["role"] != "system"][-10:]
        extraction_history.extend(recent_messages)
        extraction_history.append(extraction_prompt)

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

        payload = {
            "project_id": self.project_id,
            "model_id": self.model_id,
            "messages": extraction_history,
            "parameters": {
                "max_tokens": 1500,
                "temperature": 0.1,  # Low temperature for precise extraction
                "top_p": 0.9,
            }
        }

        try:
            response = requests.post(
                f"{self.url}/ml/v1/text/chat?version=2023-05-29",
                headers=headers,
                json=payload,
                timeout=60,
            )
            response.raise_for_status()
            result = response.json()
            
            extraction_text = result["choices"][0]["message"]["content"].strip()
            
            # Clean up markdown code blocks if present
            extraction_text = re.sub(r'^```json?\s*', '', extraction_text)
            extraction_text = re.sub(r'\s*```$', '', extraction_text)
            
            # Remove any text before the first {
            if '{' in extraction_text:
                extraction_text = extraction_text[extraction_text.find('{'):]
            
            # Remove any text after the last }
            if '}' in extraction_text:
                extraction_text = extraction_text[:extraction_text.rfind('}')+1]
            
            extracted = json.loads(extraction_text)
            
            # Validate no fake names
            if extracted.get("personal", {}).get("full_name") in ["John Doe", "Jane Doe", "Jane Smith", "John Smith"]:
                extracted["personal"]["full_name"] = None
            
            return extracted

        except json.JSONDecodeError as e:
            # Early in conversation, structured data isn't available yet - this is normal
            if questions_asked < 5:
                return {}
            print(f"⚠️ Error extracting data (JSON parse): {e}")
            return {}
        except Exception as e:
            print(f"⚠️ Error extracting data: {e}")
            return {}

    def _check_intake_complete(self, extracted_data: Dict[str, Any], questions_asked: int) -> bool:
        """
        Determine if we've collected enough information to complete the intake.
        Requires comprehensive data across all categories and at least 22 questions asked.
        """
        
        if questions_asked < 22:
            return False  # Haven't asked enough questions yet
        
        # Check for essential data in each category
        personal = extracted_data.get("personal", {})
        household = extracted_data.get("household", {})
        employment = extracted_data.get("employment", {})
        financial = extracted_data.get("financial", {})
        housing = extracted_data.get("housing", {})
        health = extracted_data.get("health", {})
        legal = extracted_data.get("legal", {})
        
        # Must have basic personal info
        has_personal = bool(
            personal.get("full_name") or personal.get("first_name")
        ) and (
            personal.get("age") or personal.get("date_of_birth")
        ) and (
            personal.get("phone") or personal.get("email")
        )
        
        # Must have household info
        has_household = household.get("size") is not None
        
        # Must have employment info
        has_employment = bool(employment.get("status"))
        
        # Must have financial info
        has_financial = (
            financial.get("monthly_income") is not None
        )
        
        # Must have housing info
        has_housing = bool(housing.get("status"))
        
        # Must have health info
        has_health = health.get("has_disability") is not None
        
        # Must have legal/citizenship
        has_legal = bool(legal.get("citizenship_status"))
        
        # All categories must have some data
        return all([
            has_personal,
            has_household,
            has_employment,
            has_financial,
            has_housing,
            has_health,
            has_legal,
        ])

    def generate_case_summary(self, conversation_id: str) -> Dict[str, Any]:
        """
        Generate final case summary with urgency scoring and recommendations.
        Called when intake is complete.
        """
        if conversation_id not in self.conversations:
            return {}
        
        conv = self.conversations[conversation_id]
        extracted_data = conv["collected_data"]
        
        # Calculate urgency score
        urgency_result = self._calculate_urgency_score(extracted_data)
        
        # Generate AI summary and recommendations
        ai_summary = self._generate_ai_summary(conv["history"], extracted_data)
        
        return {
            "extracted_data": extracted_data,
            "urgency_score": urgency_result["score"],
            "urgency_reasoning": urgency_result["reasoning"],
            "ai_summary": ai_summary["summary"],
            "recommended_programs": ai_summary["programs"],
            "recommended_actions": ai_summary["actions"],
            "conversation_history": conv["history"],
            "questions_asked": conv["questions_asked"],
            "duration": self._calculate_duration(conv["start_time"]),
        }

    def _calculate_urgency_score(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate urgency score (1-10) based on multiple factors.
        Higher score = more urgent need.
        """
        score = 5  # Base score
        reasons = []
        
        housing = data.get("housing", {})
        household = data.get("household", {})
        financial = data.get("financial", {})
        health = data.get("health", {})
        emergency = data.get("emergency", {})
        
        # CRITICAL FACTORS (+3 each)
        if housing.get("status") in ["homeless", "shelter"]:
            score += 3
            reasons.append("Currently homeless or in shelter")
        
        if housing.get("at_risk_of_homelessness"):
            score += 3
            reasons.append("At risk of homelessness")
        
        if emergency.get("has_urgent_needs"):
            score += 3
            reasons.append("Has immediate emergency needs")
        
        # HIGH PRIORITY FACTORS (+2 each)
        if household.get("has_children"):
            score += 2
            reasons.append("Has children in household")
        
        if financial.get("monthly_income", 999999) == 0:
            score += 2
            reasons.append("Zero income")
        
        if health.get("has_disability"):
            score += 2
            reasons.append("Has disability")
        
        # MODERATE FACTORS (+1 each)
        if financial.get("monthly_income", 999999) < 1000:
            score += 1
            reasons.append("Very low income (under $1000/month)")
        
        if health.get("has_insurance") is False:
            score += 1
            reasons.append("No health insurance")
        
        if health.get("has_medical_expenses"):
            score += 1
            reasons.append("Has medical expenses")
        
        # Cap at 10
        score = min(score, 10)
        
        reasoning = "; ".join(reasons) if reasons else "Standard priority case"
        
        return {
            "score": score,
            "reasoning": reasoning
        }

    def _generate_ai_summary(self, conversation_history: List[Dict[str, str]], extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use Watson to generate human-readable summary and recommendations.
        """
        token = self.get_access_token()

        summary_prompt = {
            "role": "user",
            "content": (
                "Generate a comprehensive case summary for a caseworker.\n\n"
                "Based on the conversation and extracted data, provide:\n\n"
                "1. **CASE SUMMARY** (3-4 paragraphs):\n"
                "   - Who is this person and what is their situation?\n"
                "   - Key facts about household, income, employment\n"
                "   - Housing and health status\n"
                "   - Any urgent concerns\n\n"
                "2. **RECOMMENDED PROGRAMS** (JSON array):\n"
                "   - List programs they likely qualify for: SNAP, Medi-Cal, SSI, TANF\n"
                '   - Format: ["SNAP", "Medi-Cal"]\n\n'
                "3. **RECOMMENDED ACTIONS** (bullet points):\n"
                "   - What should the caseworker do first?\n"
                "   - What documentation to request?\n"
                "   - Any urgent follow-up needed?\n\n"
                "Return in this JSON format:\n"
                "{\n"
                '  "summary": "narrative summary here...",\n'
                '  "programs": ["SNAP", "Medi-Cal"],\n'
                '  "actions": "• Action 1\\n• Action 2\\n• Action 3"\n'
                "}\n\n"
                "Be professional but compassionate in tone. Return ONLY valid JSON."
            )
        }

        summary_history = [
            {"role": "system", "content": "You are a case summary specialist helping caseworkers understand client situations quickly."}
        ]
        
        # Include conversation context
        recent_messages = [msg for msg in conversation_history if msg["role"] != "system"][-15:]
        summary_history.extend(recent_messages)
        summary_history.append(summary_prompt)

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

        payload = {
            "project_id": self.project_id,
            "model_id": self.model_id,
            "messages": summary_history,
            "parameters": {
                "max_tokens": 1000,
                "temperature": 0.5,
                "top_p": 0.9,
            }
        }

        try:
            response = requests.post(
                f"{self.url}/ml/v1/text/chat?version=2023-05-29",
                headers=headers,
                json=payload,
                timeout=60,
            )
            response.raise_for_status()
            result = response.json()
            
            summary_text = result["choices"][0]["message"]["content"].strip()
            
            # Clean markdown
            summary_text = re.sub(r'^```json?\s*', '', summary_text)
            summary_text = re.sub(r'\s*```$', '', summary_text)
            
            summary_data = json.loads(summary_text)
            return summary_data

        except Exception as e:
            print(f"⚠️ Error generating summary: {e}")
            return {
                "summary": "Case summary generation failed. Please review conversation transcript.",
                "programs": [],
                "actions": "• Review conversation manually\n• Determine eligibility\n• Contact applicant"
            }

    def _calculate_duration(self, start_time_iso: str) -> str:
        """Calculate conversation duration in human-readable format."""
        try:
            start = datetime.fromisoformat(start_time_iso)
            duration = datetime.now() - start
            minutes = int(duration.total_seconds() / 60)
            return f"{minutes} minutes"
        except:
            return "Unknown"

    def get_conversation_transcript(self, conversation_id: str) -> List[Dict[str, str]]:
        """Get full conversation history for storage."""
        if conversation_id not in self.conversations:
            return []
        
        conv = self.conversations[conversation_id]
        # Return without system prompt
        return [msg for msg in conv["history"] if msg["role"] != "system"]
