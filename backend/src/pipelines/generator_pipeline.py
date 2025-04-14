from agents.orchestrator.orchestrator import Orchestrator
from agents.calendar.calendar_tool import CalendarTool
from agents.static_post.post_tool import PostTool
from agents.RAG.rag_tool import RAGTool
from db.saver import PublicationSaver
from agents.publisher.publisher_tool import Publisher

def run_calendar_tool(args):
    """
    Executes the CalendarTool to generate a publication calendar.

    Args:
        args (dict): A list of campaign items to schedule (each item includes image prompt, caption, dates, etc.).

    Returns:
        list: A list of publication entries, each containing:
              - "id_campaign"
              - "id_publication"
              - "datetime"
    """
    cal = CalendarTool()
    return cal.run(args)

def run_static_post_tool(args, image):
    """
    Executes the PostTool to generate an advertising image based on input arguments and an image.

    Args:
        args (dict): Dictionary containing image_prompt, id_publication, etc.
        image (str): Base64-encoded image of the product.

    Returns:
        dict: The updated publication dictionary with the generated image.
    """
    args["image"] = image
    post_tool = PostTool()
    return post_tool.run(args)

def run_pipeline(prompt: str, image: str):
    """
    Runs the full content generation pipeline, from prompt to publication saving.

    Steps:
    1. Uses the RAGTool to augment the prompt using contextual documents.
    2. Generates a publication plan using the Orchestrator.
    3. Schedules posts using CalendarTool.
    4. Creates visuals using PostTool.
    5. Combines and saves final publication data into the database.

    Args:
        prompt (str): A user-provided prompt describing the campaign idea.
        image (str): A base64-encoded image of the product to be used in generated visuals.

    Returns:
        int: Always returns 0 after successful execution.
    """
    
    saver = PublicationSaver()
    publisher = Publisher()

    rag_tool = RAGTool()
    aug_prompt = rag_tool.run(prompt)
    
    orchestrator = Orchestrator()
    plan = orchestrator.plan(aug_prompt)

    edito_cal = []
    publications = []


    for step in plan:
        tool_name = step["tool"]
        args = step["args"]

        if tool_name == "calendar":
            edito_cal = run_calendar_tool(args)

        elif tool_name == "static_post":
            post = run_static_post_tool(args, image)
            publications.append(post)

    for post in publications:
        post_id = post.get("id_publication")
        publication_date = next(
            (entry["date"] for entry in edito_cal if entry["id_publication"] == post_id), 
            None
        )
        
        if publication_date:
            post["publication_date"] = publication_date
        print("POST", post)
        saver.save_publication(post)
        print("SAVED")
        publisher.run(post)
    
    saver.close()
    
    return 0