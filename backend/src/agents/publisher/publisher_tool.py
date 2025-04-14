import base64
import requests
from datetime import datetime
from langchain_mistralai import ChatMistralAI
from dotenv import load_dotenv
import os

load_dotenv()


class Publisher:
    """
    A class responsible for uploading and publishing image posts to LinkedIn using LinkedIn's API.
    """
    def __init__(self):
        """
        Initializes the Publisher by loading required environment variables for LinkedIn API access.
        """
        self.ACCESS_TOKEN = os.getenv("LK_TOKEN")
        self.PERSON_URN = os.getenv("LK_URN")
        self.URL = os.getenv("LK_URL")

    def run(self, input_data) -> dict:

        headers = {"Authorization": f"Bearer {self.ACCESS_TOKEN}"}

        register_url = self.URL
        
        upload_data = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": self.PERSON_URN,
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent",
                    }
                ],
            }
        }

        register_response = requests.post(
            register_url,
            headers={**headers, "Content-Type": "application/json"},
            json=upload_data,
        )
        register_json = register_response.json()
        upload_url = register_json["value"]["uploadMechanism"][
            "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"
        ]["uploadUrl"]
        asset_urn = register_json["value"]["asset"]
        image = input_data["image"]
        image_bytes = base64.b64decode(image, validate=True)
        upload_image = requests.put(upload_url, headers=headers, data=image_bytes)

        post_url = "https://api.linkedin.com/v2/ugcPosts"

        post_data = {
            "author": self.PERSON_URN,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": input_data["caption"]},
                    "shareMediaCategory": "IMAGE",
                    "media": [
                        {
                            "status": "READY",
                            "description": {
                                "text": input_data["caption"]
                            },
                            "media": asset_urn,
                            "title": {"text": ""},
                        }
                    ],
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        }

        post_response = requests.post(
            post_url,
            headers={
                "Authorization": f"Bearer {self.ACCESS_TOKEN}",
                "X-Restli-Protocol-Version": "2.0.0",
                "Content-Type": "application/json",
            },
            json=post_data,
        )

        print("Post status:", post_response.status_code)
        print("Response:", post_response.json())
