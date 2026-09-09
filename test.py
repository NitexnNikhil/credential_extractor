from deepgram import DeepgramClient  
from deepgram.core.api_error import ApiError  
  
def test_deepgram_api_key(api_key: str) -> bool:  
    """Test if a Deepgram API key is valid by transcribing a sample audio URL."""  
    try:  
        # Initialize client with explicit API key  
        client = DeepgramClient(api_key=api_key)  
          
        # Test with a known audio URL  
        response = client.listen.v1.media.transcribe_url(  
            url="https://dpgr.am/spacewalk.wav",  
            model="nova-3"  
        )  
          
        # Check if we got a valid response  
        if response and response.results and response.results.channels:  
            transcript = response.results.channels[0].alternatives[0].transcript  
            print(f"✅ Key works! Transcript: {transcript}")  
            return True  
        else:  
            print("❌ Key failed: Invalid response structure")  
            return False  
              
    except ApiError as e:  
        print(f"❌ Key failed: API Error {e.status_code}: {e.body}, api_key: {api_key}")  
        return False  
    except Exception as e:  
        print(f"❌ Key failed: {e}")  
        return False  
  
if __name__ == "__main__":  
    # Test with environment variable or replace with your key  
    # import os  
      
    api_key = "e204fade2b754ea9f3b79acee4974135dd289e2b"
    if not api_key:  
        print("Please set DEEPGRAM_API_KEY environment variable or modify the script")  
        exit(1)  
      
    test_deepgram_api_key(api_key)


