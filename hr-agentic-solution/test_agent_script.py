import sys
import os
import asyncio

sys.path.insert(0, os.path.abspath("."))
from app.agent import app
from google.adk.runners import Runner

async def main():
    print("Initializing runner...")
    runner = Runner(app=app)
    print("Sending query to agent...")
    response = await runner.run("What is the bereavement policy?")
    print("Agent response:")
    print(response.message.content)

if __name__ == "__main__":
    asyncio.run(main())
