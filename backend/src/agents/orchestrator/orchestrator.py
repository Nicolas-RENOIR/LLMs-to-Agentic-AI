from langchain_mistralai import ChatMistralAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import json
import hashlib
import random
import uuid
import os
from dotenv import load_dotenv



class Orchestrator:
    def __init__(self):
        """
        Initializes the Orchestrator by loading environment variables and setting up the language model and prompt.
        """
        load_dotenv() 
        self.llm = ChatMistralAI(
            model="mistral-large-latest",
        )

        self.planner_prompt = """
            Tu es un excellent community manager, ta mission est d'organiser des campagnes de publications sur les réseaux comme Instagram, Facebook... Avec une grande
            expérience dans ton métier, tu es performant dans l'organisation des tâches de création, tu suis toujours 3 étapes :
            1) Tu analyses le travail que ton équipe te fournit : les descriptions des images ainsi que les descriptions à mettre pour chacun des posts.
            2) Organise cette tâche en une série de sous-tâches en attribuant des outils spécifiques à chaque étape.
            Si l'utilisateur a demandé plusieurs publications, assure-toi de générer plusieurs images. (Pour chaque publication tu génères un ID unique pour les poste)

            Utilise ce format JSON, ta réponse doit uniquement contenir un réponse de ce format (aucun commentaire n'est demandé). Si il y a plus ou moins de publication adapte le nombre de steps evidemment :
            {{
                "steps": [
                    {{"tool": "calendar", "args": [{{"id_campagn": value, "prompt_image": value, "caption": value, "start_date": value, "end_date": value}}]}},
                    {{"tool": "static_post", "args": {{"id_campagn": value, "id_publication": value, "image_prompt": "Exemple de texte", "caption": value}}}},
                    ... etc  # X Number of post to do
                ]
            }}

            Voici le travail fourni par ton équipe : 
            {mission}
            """

        self.llm_chain = LLMChain(
            prompt=PromptTemplate(
                input_variables=["mission"], template=self.planner_prompt
            ),
            llm=self.llm,
        )

    def plan(self, task: str) -> list:

        """
        Generates a structured plan of steps for a social media campaign based on input content.

        The function uses a language model to analyze the task description and returns a sequence
        of actions (steps), such as scheduling posts and generating static content. It also injects
        unique identifiers into the plan for consistency across tools.

        Args:
            task (str): A textual description of the campaign content and goals.

        Returns:
            list: A list of step dictionaries. Each step contains:
                - "tool": Name of the tool to be used (e.g., "calendar", "static_post").
                - "args": Parameters required by the tool (e.g., prompt, caption, dates).
        """

        print("TASK", task)
        plan = self.llm_chain.run(mission=task)
        try:
            plan = json.loads(plan)

        except json.JSONDecodeError:
            cleaned = plan.strip("```json").strip("```").strip()
            plan = json.loads(cleaned)
        
        finally:
            steps = plan["steps"]

            id_campaign = str(uuid.uuid4())

            for step in steps:
                print("UN STEP", step)
                if step["tool"] == "calendar":
                    for arg in step["args"]:
                        arg["id_campaign"] = id_campaign

                elif step["tool"] == "static_post":
                    image_prompt = step["args"]["image_prompt"]
                    id_publication = hashlib.sha256(image_prompt.encode()).hexdigest()[:8]
                    step["args"]["id_publication"] = id_publication
                    step["args"]["id_campaign"] = id_campaign
                    print(step["args"]["id_publication"])

            return steps
