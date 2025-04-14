import mysql.connector

class PublicationSaver:
    """
    A class to handle saving and retrieving publication data from a MySQL database.
    """
    def __init__(self):
        """
        Initializes the database connection and cursor.
        Assumes the MySQL service is running with the provided host, port, user, and database.
        """
        self.conn = mysql.connector.connect(
            host="mysql",
            port=3306,
            user="myuser",
            password="mypassword",
            database="mydatabase"
        )
        self.cursor = self.conn.cursor()

    def save_publication(self, publication: dict):
        """
        Saves a publication entry into the `publications` table in the database.

        Args:
            publication (dict): A dictionary containing the following keys:
                - "id_campaign" (str): The campaign ID.
                - "id_publication" (str): The publication ID.
                - "image_prompt" (str): The text used to describe the image prompt.
                - "caption" (str): The social media caption.
                - "image" (str): The base64-encoded image or image data.

        Returns:
            None
        """
        sql = """
        INSERT INTO publications (id_campaign, id_publication, image_prompt, caption, image)
        VALUES (%s, %s, %s, %s, %s)
        """
        values = (
            publication.get("id_campaign"),
            publication.get("id_publication"),
            publication.get("image_prompt"),
            publication.get("caption"),
            publication.get("image")
        )

        self.cursor.execute(sql, values)
        self.conn.commit()
    
    def get_publications(self):
        """
        Retrieves all publications stored in the database.

        Returns:
            list: A list of dictionaries, each representing a publication with:
                - "id_campaign"
                - "id_publication"
                - "image_prompt"
                - "caption"
                - "image"
        """
        sql = "SELECT id_campaign, id_publication, image_prompt, caption, image FROM publications"
        self.cursor.execute(sql)
        rows = self.cursor.fetchall()
        
        publications = []
        for row in rows:
            publication = {
                "id_campaign": row[0],
                "id_publication": row[1],
                "image_prompt": row[2],
                "caption": row[3],
                "image": row[4]
            }
            publications.append(publication)

        return publications

    def close(self):
        """
        Closes the database connection and cursor.

        Returns:
            None
        """
        self.cursor.close()
        self.conn.close()