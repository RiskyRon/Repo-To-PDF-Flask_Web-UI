
# This script lists and optionally deletes all classes and data objects in Weaviate, cleaning up any unwanted vectored pdfs.

import weaviate

def list_and_optionally_delete_classes(client):
    # Get the list of all classes in Weaviate
    schema = client.schema.get()
    classes = schema['classes']
    
    for class_info in classes:
        class_name = class_info['class']
        print(f"Class: {class_name}")
        
        # Ask the user if they want to delete this class
        delete_class = input(f"Do you want to delete the class '{class_name}'? (yes/no): ").strip().lower()
        if delete_class == 'yes':
            client.collection.delete(class_name)
            print(f"Deleted class '{class_name}'.")
            continue  # Skip to the next class since this one has been deleted
        
        # List the data objects of this class
        data_objects = client.collection.get(class_name).data.get()
        print(f"Data Objects in '{class_name}':")
        for data_object in data_objects['objects']:
            print(f"  - UUID: {data_object['id']}, Properties: {data_object['properties']}")
            
            # Ask the user if they want to delete this data object
            delete_object = input(f"Do you want to delete this object with UUID {data_object['id']}? (yes/no): ").strip().lower()
            if delete_object == 'yes':
                client.collection.get(class_name).data.delete(data_object['id'])
                print(f"Deleted object with UUID {data_object['id']}.")

if __name__ == "__main__":
    # Connect to the Weaviate instance
    client = weaviate.Client("http://localhost:8080")
    
    list_and_optionally_delete_classes(client)
