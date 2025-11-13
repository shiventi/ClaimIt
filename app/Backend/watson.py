import os
import json
import re
import time
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv

load_dotenv()


class WatsonAssistantSimple:
    """Thin wrapper around the watsonx.ai REST API for conversational flows."""

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

        print("Setting up WatsonX REST API integration...")
        self.access_token: str | None = None
        self.token_expiry: float = 0
        self.conversations: Dict[str, Dict[str, Any]] = {}

        self.field_order: List[str] = [
            "name",
            "household_size",
            "monthly_income",
            "age",
            "is_employed",
            "assets",
            "has_children",
            "has_disability",
            "housing_costs",
            "medical_expenses",
            "utility_costs",
            "citizenship_status",
            "has_health_insurance",
        ]
        self.bool_fields = {
            "is_employed", 
            "has_children", 
            "has_disability",
            "has_health_insurance",
        }

        print("WatsonX REST API is ready!")

    def get_access_token(self) -> str:
        """Fetch (and cache) an IAM access token."""
        if self.access_token and time.time() < self.token_expiry - 60:
            return self.access_token

        print("Fetching new IBM Cloud IAM access token...")
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
        print("Token fetched, expires in", expires_in, "seconds.")
        return self.access_token

    def start_conversation(self, conversation_id: str) -> str:
        """Bootstrap a new conversation with a system primer."""
        print(f"Starting new conversation: {conversation_id}")

        system_prompt = (
            "You are a warm, compassionate benefits application assistant for ClaimIt. 🤝\n\n"
            
            "YOUR MISSION:\n"
            "You're here to help people access the support they deserve - whether it's food assistance (SNAP/CalFresh) "
            "or healthcare (Medi-Cal). Many of the people you'll help may be seniors, people with disabilities, "
            "or folks going through tough times. Treat everyone with dignity, patience, and genuine care.\n\n"
            
            "**AVAILABLE BENEFIT PROGRAMS:**\n"
            "We help screen for these California benefit programs:\n\n"
            "1. **SNAP/CalFresh** - Food assistance for groceries\n"
            "2. **Medi-Cal** - Free or low-cost healthcare coverage\n"
            "3. **SSI** - Supplemental Security Income for elderly/disabled\n"
            "4. **CalWORKs/TANF** - Cash assistance for families with children\n\n"
            "If someone asks what forms/programs you offer, list these programs with brief descriptions.\n\n"
            
            "YOUR PERSONALITY:\n"
            "- Warm and empathetic, like a caring friend or family member\n"
            "- Patient and understanding - never rush anyone\n"
            "- Respectful and encouraging - celebrate their courage in seeking help\n"
            "- Clear and simple - avoid jargon, use plain language\n"
            "- Reassuring - let them know this process is manageable and you're here to help every step\n"
            "- **HONEST** - Never make up information. Only use what the user actually tells you.\n\n"
            
            "INFORMATION YOU NEED TO GATHER:\n"
            "Ask about these in a natural, conversational way:\n\n"
            
            "1. **Basic Information:**\n"
            "   - Name (so you can personalize your help)\n"
            "   - Age (affects program eligibility)\n"
            "   - Household size (if they say 'nobody', 'alone', 'just me', 'by myself' = 1 person)\n\n"
            
            "2. **Financial Situation:**\n"
            "   - Monthly income (if unemployed/no job = $0, and that's completely okay)\n"
            "   - Employment status (no judgment either way)\n"
            "   - Assets/savings (be gentle with this topic)\n"
            "   - Monthly housing costs (rent/mortgage)\n"
            "   - Monthly utility costs (electric, gas, water)\n"
            "   - Monthly medical expenses (if any)\n\n"
            
            "3. **Household Composition:**\n"
            "   - Whether they have children\n"
            "   - Whether they have any disabilities (optional, but helps with benefits)\n\n"
            
            "4. **Health & Status:**\n"
            "   - Whether they have health insurance\n"
            "   - U.S. citizenship or legal status (for program eligibility)\n\n"
            
            "HOW TO COMMUNICATE:\n"
            "✓ Ask ONE question at a time - don't overwhelm them\n"
            "✓ Use warm, conversational language: 'Thanks for sharing that with me' instead of 'Acknowledged'\n"
            "✓ LISTEN carefully - if they share multiple things at once, acknowledge EVERYTHING they said\n"
            "✓ NEVER ask twice - if they already told you something, use it!\n"
            "✓ If they remind you they already answered, apologize warmly: 'I'm so sorry, you're absolutely right. Let's move on...'\n"
            "✓ Validate their situation: 'I understand' or 'That makes sense' or 'Thank you for sharing'\n"
            "✓ Show empathy for difficult situations: 'I can imagine that's challenging' or 'You're doing the right thing by seeking help'\n\n"
            
            "IMPORTANT UNDERSTANDING:\n"
            "- When someone says they're unemployed or have no income, acknowledge that kindly and mark income as $0\n"
            "- Don't ask redundant follow-ups like 'Are you employed?' after they just said they're unemployed\n"
            "- Move gracefully to the next needed information\n\n"
            
            "**FORM RECOMMENDATION LOGIC:**\n"
            "Once you have enough information (name, age, household, income, basic expenses), determine eligibility:\n\n"
            
            "**CRITICAL: NOT EVERYONE IS ELIGIBLE**\n"
            "- Only recommend forms if the person actually qualifies based on income, age, status, etc.\n"
            "- If income is too high for all programs, explain they may not qualify\n"
            "- If citizenship status is an issue, explain limitations compassionately\n"
            "- If they don't meet criteria, provide alternative resources or suggestions\n\n"
            
            "**SNAP (CalFresh) - Food Assistance:**\n"
            "- Income limit: ~$2,266 + $814 per additional household member (gross monthly)\n"
            "- Work requirements for able-bodied adults 18-49 without dependents\n"
            "- Generally requires U.S. citizenship or legal status\n\n"
            
            "**Medi-Cal (MEDICAL) - Healthcare Coverage:**\n"
            "- For uninsured, low income, elderly 65+, disabled, pregnant\n"
            "- Income limit: ~$1,732 + $600 per additional household member\n"
            "- Citizens and qualified immigrants eligible\n\n"
            
            "**SSI (Supplemental Security Income):**\n"
            "- For elderly (65+) OR disabled individuals only\n"
            "- Very strict: Monthly income must be under ~$1,000\n"
            "- Asset limits apply\n"
            "- U.S. citizens or qualifying immigrants\n\n"
            
            "**TANF/CalWORKs - Cash Assistance:**\n"
            "- Must have children under 18\n"
            "- Very low income required\n"
            "- Work requirements and time limits apply\n\n"
            
            "**When NOT eligible:**\n"
            "- Be compassionate but honest: 'Based on what you've shared, you may not qualify for these programs right now...'\n"
            "- Suggest alternatives: food banks, community resources, 211 helpline, local charities\n"
            "- Explain that eligibility can change if circumstances change\n"
            "- Provide encouragement and other options\n\n"
            
            "**Multiple forms may be appropriate:**\n"
            "- Many people qualify for multiple programs (e.g., SNAP + Medi-Cal + SSI)\n"
            "- Recommend ALL applicable forms they qualify for\n\n"
            
            "**IMPORTANT: Use markdown formatting in your responses:**\n"
            "- Use **bold** for emphasis\n"
            "- Use bullet points (- or *) for lists\n"
            "- Use ## for section headers when providing final recommendations\n"
            "- Use > for important callouts or quotes\n"
            "- Make your responses visually engaging and easy to read\n\n"
            
            "When recommending forms (or explaining non-eligibility), warmly explain WHY based on their specific situation. "
            "Use markdown to make the recommendation clear and easy to understand. "
            "Always be supportive and provide next steps, whether they qualify or not. "
            "Remember: these programs exist to help, but not everyone qualifies - be honest but kind."
        )

        self.conversations[conversation_id] = {
            "history": [{"role": "system", "content": system_prompt}],
            "collected_data": {},
            "message_count": 0,
        }
        return conversation_id

    def send_message(self, conversation_id: str, user_message: str) -> Dict[str, Any]:
        if conversation_id not in self.conversations:
            self.start_conversation(conversation_id)

        conv = self.conversations[conversation_id]
        conv["message_count"] += 1
        conv["history"].append({"role": "user", "content": user_message})
        print(f"\nUser: {user_message}")

        previous_data = conv["collected_data"].copy()

        guidance = self._build_guidance_instruction(conv["collected_data"])
        history_payload = conv["history"][:]
        if guidance:
            history_payload.append({"role": "system", "content": guidance})
            print(f"\nGuidance sent to Watson:\n{guidance}\n")

        watson_text = self._invoke_watson(history_payload, max_tokens=2000)
        conv["history"].append({"role": "assistant", "content": watson_text})

        extracted_data = self._extract_data_with_watson(conv["history"])
        self._apply_updates(conv["collected_data"], extracted_data)

        new_information = {
            key: conv["collected_data"].get(key)
            for key in self.field_order
            if conv["collected_data"].get(key) is not None
            and conv["collected_data"].get(key) != previous_data.get(key)
        }
        if new_information:
            print(f"New information captured: {new_information}")
        print(f"Total data collected so far: {conv['collected_data']}")

        is_complete = self.check_if_complete(conv["collected_data"])
        selected_form = self._select_form(conv["collected_data"]) if is_complete else None

        print(f"Assistant: {watson_text}")

        return {
            "watson_response": watson_text,
            "collected_data": conv["collected_data"].copy(),
            "is_complete": is_complete,
            "selected_form": selected_form,
        }

    def _invoke_watson(self, messages: List[Dict[str, str]], *, max_tokens: int) -> str:
        body = {
            "messages": messages,
            "project_id": self.project_id,
            "model_id": self.model_id,
            "frequency_penalty": 0,
            "max_tokens": max_tokens,
            "presence_penalty": 0,
            "temperature": 0,
            "top_p": 1,
        }

        token = self.get_access_token()
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

        response = requests.post(self.url, headers=headers, json=body, timeout=60)
        response.raise_for_status()
        data = response.json()
        return self._get_watsonx_text(data)

    def _get_watsonx_text(self, watsonx_response: Dict[str, Any]) -> str:
        try:
            choices = watsonx_response.get("choices", [])
            if choices and "message" in choices[0]:
                return choices[0]["message"].get("content", "I understand.")
        except Exception as exc:  # pragma: no cover - defensive log
            print(f"Failed to parse WatsonX response: {exc}")
        return "I understand."

    def _extract_data_with_watson(self, conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
        extraction_prompt = {
            "role": "system",
            "content": (
                "CRITICAL: Analyze ONLY the actual conversation and extract information that the user EXPLICITLY provided. "
                "DO NOT make up or invent ANY information. DO NOT use example names like 'John Doe'. "
                "If information was not provided, use null.\n\n"
                "Extract these fields ONLY if explicitly mentioned:\n"
                "- name: Full name (ONLY if user stated it, otherwise null)\n"
                "- age: Age in years (ONLY if stated, otherwise null)\n"
                "- household_size: Number of people (ONLY if stated, otherwise null). If they say 'alone', 'by myself' = 1.\n"
                "- monthly_income: Monthly income in dollars (ONLY if stated, otherwise null). If unemployed/no job mentioned = 0.\n"
                "- is_employed: Employment status (ONLY if stated, otherwise null)\n"
                "- assets: Savings/assets in dollars (ONLY if stated, otherwise null)\n"
                "- has_children: Whether they have children (ONLY if stated, otherwise null)\n"
                "- has_disability: Whether they have disability (ONLY if stated, otherwise null)\n"
                "- has_health_insurance: Whether they have insurance (ONLY if stated, otherwise null)\n\n"
                "IMPORTANT: Return ONLY actual information from the conversation. DO NOT use placeholder data.\n"
                "Return a valid JSON object with ONLY the fields that were actually mentioned.\n"
                "Example of correct output when user only said 'I'm Sarah':\n"
                "{\"name\": \"Sarah\"}\n\n"
                "Example when user said nothing useful:\n"
                "{}"
            ),
        }

        extraction_messages = conversation_history[:] + [extraction_prompt]

        try:
            extraction_text = self._invoke_watson(extraction_messages, max_tokens=600)
            extraction_text = extraction_text.strip()
            if extraction_text.startswith("```"):
                lines = extraction_text.split("\n")
                extraction_text = "\n".join(lines[1:-1])
            
            extracted = json.loads(extraction_text)
            
            # Validate that we're not getting fake data
            if extracted.get('name') in ['John Doe', 'Jane Doe', 'null', 'None', 'example']:
                extracted['name'] = None
            
            return extracted
        except Exception as exc:
            print(f"Watson extraction error: {exc}")
            return {}

    def _apply_updates(self, collected_data: Dict[str, Any], updates: Dict[str, Any]) -> None:
        for key, value in updates.items():
            if key not in self.field_order:
                continue
            normalized = self._normalize_value(key, value)
            if normalized is None:
                continue
            collected_data[key] = normalized

    def _normalize_value(self, field: str, value: Any):
        if value is None:
            return None

        if isinstance(value, str):
            value = value.strip()
            if value == "":
                return None

        if field in {"household_size", "age"}:
            number = self._parse_float(value)
            if number is None:
                return None
            return int(round(number))

        if field in {"monthly_income", "assets"}:
            number = self._parse_float(value)
            if number is None:
                return None
            return float(number)

        if field in self.bool_fields:
            if isinstance(value, bool):
                return value
            if isinstance(value, (int, float)):
                return bool(value)
            if isinstance(value, str):
                lowered = value.lower()
                if lowered in {"yes", "y", "true", "t"}:
                    return True
                if lowered in {"no", "n", "false", "f"}:
                    return False
            return None

        if field == "name":
            return str(value).strip()

        return value

    def _parse_float(self, value: Any) -> float | None:
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            cleaned = value.lower().replace("usd", "").replace(",", "").replace("$", " ").strip()
            multiplier = 1.0
            if cleaned.endswith("k"):
                multiplier = 1000.0
                cleaned = cleaned[:-1]
            match = re.search(r"-?\d+(\.\d+)?", cleaned)
            if not match:
                return None
            try:
                return float(match.group()) * multiplier
            except ValueError:
                return None
        return None

    def check_if_complete(self, data: Dict[str, Any]) -> bool:
        """Check if we have enough information to make a recommendation"""
        # Core required fields that we MUST have
        required_fields = ["name", "household_size", "monthly_income", "age"]
        for field in required_fields:
            value = data.get(field)
            if value is None:
                return False
            if isinstance(value, str) and not value.strip():
                return False

        # Important fields for eligibility determination - ask explicitly
        # Don't auto-complete until we have employment status
        if "is_employed" not in data or data.get("is_employed") is None:
            return False
        
        # Set defaults for optional fields
        data.setdefault("assets", 0)
        data.setdefault("has_children", False)
        data.setdefault("has_disability", False)
        data.setdefault("has_health_insurance", False)
        
        return True

    def _build_guidance_instruction(self, data: Dict[str, Any]) -> str:
        if not data:
            return (
                "You are helping someone apply for government benefits. Ask friendly questions to collect: "
                "name, household size, monthly income, age, employment status, assets/savings, children, and disability status. "
                "Ask ONE question at a time. Be conversational and supportive."
            )

        lines = ["IMPORTANT: Here is what you have ALREADY learned about the user:"]
        label_map = {
            "name": "Name",
            "age": "Age",
            "household_size": "Household size",
            "monthly_income": "Monthly income",
            "is_employed": "Employment status",
            "assets": "Assets/savings",
            "has_children": "Has children",
            "has_disability": "Has disability",
        }

        collected_labels = []
        for key, label in label_map.items():
            if key in data and data[key] is not None:
                value = data[key]
                if key in {"monthly_income", "assets"}:
                    value = self._format_currency(value)
                elif isinstance(value, bool):
                    value = "Yes" if value else "No"
                lines.append(f"\u2713 {label}: {value}")
                collected_labels.append(label)

        if collected_labels:
            lines.append("")
            lines.append(f"DO NOT ask about: {', '.join(collected_labels)}")
            lines.append("These have been provided already. Never ask for them again.")
            lines.append("")

        required_fields = ["name", "household_size", "monthly_income", "age"]
        missing_labels = [label_map[f] for f in required_fields if data.get(f) in (None, "")]
        if missing_labels:
            lines.append(
                f"Still needed: {', '.join(missing_labels)}.\n"
                f"Ask ONLY for: {missing_labels[0]}.\n"
                "Do NOT repeat questions for information already collected."
            )
        else:
            lines.append(
                "You have all required information! Thank the user, summarize what you collected, "
                "recommend SNAP or MEDICAL form, and explain why."
            )

        return "\n".join(lines)

    def _select_form(self, data: Dict[str, Any]) -> str:
        # Placeholder logic; refine as program rules evolve.
        return "SNAP"

    def _format_currency(self, value: Any) -> str:
        try:
            number = float(value)
        except (TypeError, ValueError):
            return str(value)
        if number.is_integer():
            return f"${int(number):,}"
        return f"${number:,.2f}"

    def end_conversation(self, conversation_id: str) -> None:
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            print(f"Ended conversation: {conversation_id}")


def test() -> None:
    """Simple CLI smoke test for manual debugging."""
    try:
        assistant = WatsonAssistantSimple()
    except ValueError as exc:
        print(exc)
        return

    conversation_id = "debug"
    assistant.start_conversation(conversation_id)
    for message in [
        "Hi",
        "My name is Alex Smith",
        "There are 2 people in my household",
        "We earn about $1400 a month",
        "I'm 48",
    ]:
        result = assistant.send_message(conversation_id, message)
        print("\n--- Result ---")
        print("Assistant:", result["watson_response"])
        print("Collected:", json.dumps(result["collected_data"], indent=2))
        if result["is_complete"]:
            print("Selected form:", result["selected_form"])
            break

    assistant.end_conversation(conversation_id)


if __name__ == "__main__":
    test()
