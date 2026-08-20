import asyncio
import sys
import os

sys.path.insert(0, "/usr/local/google/home/anujshaunj/hr-agentic-solution/hr-agentic-solution")
from app.agent import app
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

async def main():
    # Set Vertex AI environment variables
    os.environ["GOOGLE_CLOUD_PROJECT"] = "geap-poc"
    os.environ["GOOGLE_CLOUD_LOCATION"] = "us-east1"
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"
    
    if "GEMINI_API_KEY" in os.environ:
        del os.environ["GEMINI_API_KEY"]
        
    session_service = InMemorySessionService()
    runner = Runner(app=app, session_service=session_service)
    
    # Create the session first
    await session_service.create_session(session_id="test_session", user_id="test_user", app_name="hr_agentic_solution")
    
    message = types.Content(role="user", parts=[types.Part.from_text(text="What is the bereavement policy according to the Altostrat handbook?")])
    
    # Try to consume the generator completely before exiting
    events = runner.run(user_id="test_user", session_id="test_session", new_message=message)
    for event in events:
        if event.type == "message":
            print(event.content.parts[0].text)
            
    # Add a small sleep to allow background tasks to complete
    await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
