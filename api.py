"""
import requests

def main():
	url = "https://us-south.ml.cloud.ibm.com/ml/v1/text/chat?version=2023-05-29"
	body = {
		"messages": [{"role": "control", "content": "What is the capital of France?"}],
		"project_id": "WATSON_PROJECT_ID",
		"model_id": "ibm/granite-3-8b-instruct",
		"frequency_penalty": 0,
		"max_tokens": 2000,
		"presence_penalty": 0,
		"temperature": 0,
		"top_p": 1
	}
	headers = {
		"Accept": "application/json",
		"Content-Type": "application/json",
		"Authorization": "Bearer WRITE_THE_ACCESS_TOKEN"
	}
	try:
		response = requests.post(url, headers=headers, json=body)
		response.raise_for_status()
	except requests.RequestException as e:
		print(f"Request failed: {e}")
		return
	try:
		data = response.json()
		print("Response JSON:")
		print(data)
	except Exception as e:
		print(f"Failed to parse JSON: {e}")

if __name__ == "__main__":
	main()
"""