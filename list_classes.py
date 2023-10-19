# list_classes.py
import weaviate
from weaviate import Config
import weaviate.classes as wvc
from weaviate_init import client

def list_weaviate_classes():
    """
    Returns a list of class names in the Weaviate instance.

    Returns:
    - classes: List of class names.
    """
    # Ensure Weaviate client is initialized and ready
    if not client.is_ready():
        raise Exception("Weaviate is not ready!")

    # Get the schema from Weaviate
    schema = client.schema.get()

    # Extract class names from the schema
    classes = [clazz["class"] for clazz in schema["classes"]]

    return classes

# Test the function
if __name__ == "__main__":
    print(list_weaviate_classes())
