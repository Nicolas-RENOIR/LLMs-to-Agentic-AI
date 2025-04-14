import json
import aiohttp
import os
from datetime import datetime
from langchain_mistralai import ChatMistralAI

class CalendarTool:
    def __init__(self):
        self.name = "calendar"

        self.llm = ChatMistralAI(
            model="mistral-large-latest",
            temperature=0,
        )

    def build_prompt(self, input_data: str) -> str:
        base_prompt = """
        You are a marketing AI assistant.

        Your task is to generate an advertising campaign schedule based on the following creative assets. Each item includes:
        - An image prompt (describing the content)
        - A caption (for social media)
        - A unique ID
        - A campaign start and end date

        Instructions:
        - Analyze the image and caption to determine the ad’s theme (e.g. morning routine, fitness, weekend relaxation, luxury fashion).
        - Schedule exactly **one publication per ad**.
        - Ensure the post is scheduled **within the campaign’s start and end date**.
        - Choose the **most effective date and time** for the target audience based on standard social media engagement patterns:
          - **Weekdays**: 08:00–10:00 (morning), 12:00–14:00 (lunch), 18:00–21:00 (evening)
          - **Weekends**: 09:00–11:00 (morning), 15:00–18:00 (afternoon)
        - Match the time slot to the ad theme and audience behavior (e.g. fitness in the morning, luxury in the evening, kids’ products on weekends).
        - Return only the JSON with **no explanation or extra text**.
        - The output must be a list with the following format:

        [
          {
            "id_campaign": "ad_001",
            "id_publication": "ad_001",
            "datetime": "2025-04-08 08:30"
          },
          ...
        ]

        Here is the campaign data:
        """
        return base_prompt + str(input_data)

    def run(self, input_data: dict) -> dict:

        """
        Generates a publication schedule for a list of ads using the language model.

        Args:
            input_data (dict): A dictionary containing campaign details (e.g., image prompts, captions, IDs, start/end dates).

        Returns:
            dict: A dictionary representing the generated schedule, where each item includes:
                - "id_campaign": Campaign ID
                - "id_publication": Publication ID (same as campaign ID)
                - "datetime": Suggested posting datetime
        """

        prompt = self.build_prompt(input_data)
        messages = [
            ("human", prompt),
        ]
        
        ai_msg = self.llm.invoke(messages)

        raw = ai_msg.content

        try:
            results = json.loads(raw)
        except json.JSONDecodeError:
            cleaned = raw.strip("```json").strip("```").strip()
            results = json.loads(cleaned)
        return results