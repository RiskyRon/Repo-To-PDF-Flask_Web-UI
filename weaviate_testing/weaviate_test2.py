import weaviate

def main():
    # Initialize Weaviate client
    weaviate_client = weaviate.Client(
        url="https://repotopdf-5nn382pn.weaviate.network",
        auth_client_secret=weaviate.AuthApiKey(
            api_key="KgxwUxGHKMT0T3Y27iiygBLDpiBi1hyMYkTV"
        ),
        additional_headers={
            "X-OpenAI-Api-Key": "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"
        }
    )

    # Get and list available classes
    schema = weaviate_client.schema.get()
    classes = schema['classes']
    print("Available classes:")
    for i, class_info in enumerate(classes, 1):
        print(f"{i}. {class_info['class']}")

    # Prompt user to select a class
    selected_class_index = int(input("Select a class by entering its number: ")) - 1
    selected_class = classes[selected_class_index]['class']

    # Prompt user to enter a search term
    search_term = input(f"Enter a search term for semantic search in class {selected_class}: ")

    # Perform semantic search
    search_results = weaviate_client.query().text({
        "class": selected_class,
        "text": search_term
    }).do()

    # Output search results
    print(f"Search results for '{search_term}' in class {selected_class}:")
    for result in search_results['data'][selected_class]['results']:
        print(f"- {result['beacon']} (confidence: {result['certainty']})")

if __name__ == "__main__":
    main()
