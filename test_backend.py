import requests
import json
import time

url = 'http://127.0.0.1:8000/api/process-audio'

# Use the test.wav we generated earlier
files = {'file': open('test.wav', 'rb')}

# Form data mapping to what the Steampunk UI would send
data = {
    'num_speakers': 2,
    'summary_mode': 'Detailed',
    'remove_fillers': 'false',
    'noise_reduction': 'false',   # We will turn these off for the dummy audio test to save time
    'silence_removal': 'false'
}

print("Sending audio to Jihvaa Backend...")
start_time = time.time()

try:
    response = requests.post(url, files=files, data=data)
    print(f"Request completed in {time.time() - start_time:.2f} seconds.")
    
    if response.status_code == 200:
        print("\nSUCCESS! Backend Output:")
        # We cap the output so it doesn't flood the terminal if it's huge
        output_json = json.dumps(response.json(), indent=2)
        print(output_json[:1500] + ("\n...[truncated]" if len(output_json) > 1500 else ""))
    else:
        print(f"\nERROR {response.status_code}:")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("\nERROR: Connection Refused. Is the Uvicorn server running?")
