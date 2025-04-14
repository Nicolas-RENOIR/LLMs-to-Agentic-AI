from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
from PIL import Image
import base64
from io import BytesIO
import PIL.Image
import os
from dotenv import load_dotenv
load_dotenv()

class PostTool:
    """
    A tool that generates professional advertising visuals using a base product image and descriptive prompt,
    leveraging Google's Gemini image generation model.
    """
    def __init__(self):
        """
        Initializes the PostTool by setting the model name and loading the Gemini API key from environment variables.
        """
        self.name = "image_generation"
        self.api_key = os.getenv("GEMINI_KEY")
        self.client = genai.Client(api_key=self.api_key)

    def save_image(self, img, id):
        """
        Saves the generated image to disk using a specified publication ID.

        Args:
            img (PIL.Image.Image): The image to be saved.
            id (str): The publication ID to use as the filename.

        Returns:
            None
        """
        image_path = f"{id}.png"
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        with open(image_path, "wb") as f:
            f.write(buffered.getvalue())
        print(f"Image saved as {image_path}")

    def run(self, input_data: dict) -> dict:
        """
        Generates a high-quality advertising image from a base64-encoded input image and a descriptive image prompt.

        The tool sends the prompt and image to the Gemini model for image generation, saves the result locally,
        and returns the updated input data with the new base64-encoded image.

        Args:
            input_data (dict): A dictionary containing:
                - "image" (str): Base64-encoded original product image.
                - "id_publication" (str): Unique identifier for the publication.
                - "image_prompt" (str): Text describing the product and the visual context to generate.

        Returns:
            dict: The input data dictionary updated with the generated image (base64-encoded).
        """
        output_data = input_data
        image_base64 = input_data.get("image")
        id_p = input_data.get("id_publication")
        prompt_image = input_data.get("image_prompt")
        input_prompt = """
        Create a high-quality advertising visual that showcases the product from the input image with a creative, professional art direction.The product should remain the central focus, but the background must be aesthetic and harmonized with the product’s main colors, material textures, and overall shape — going beyond a plain white setup.Use subtle gradients, color-matching tones, or abstract compositions that reflect or echo elements of the product's design, while keeping the overall composition clean, modern, and visually appealing.The lighting should feel studio-like, but allow for soft shadows, light reflections, or depth that enhances realism and elegance.Do not include any text or human figures.Avoid cluttered environments, logos, or watermark-like elements.The image should look suitable for a premium social media campaign, digital showcase, or lifestyle e-commerce presentation. Here is some context about the product itself :
        """
        input_prompt += "\n" + prompt_image

        image_data = base64.b64decode(image_base64)
        image = Image.open(BytesIO(image_data)).convert("RGB")

        response = self.client.models.generate_content(
            model="gemini-2.0-flash-exp-image-generation",
            contents=[input_prompt, image],
            config=types.GenerateContentConfig(response_modalities=["Text", "Image"]),
        )
        if response.candidates and len(response.candidates)>0:
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    img = Image.open(BytesIO(part.inline_data.data))
                    self.save_image(img, id_p)

                    buffered = BytesIO()
                    img.save(buffered, format="PNG")
                    output_data["image"] = base64.b64encode(buffered.getvalue()).decode(
                        "utf-8"
                    )

        return output_data
