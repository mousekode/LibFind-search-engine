import sys
import json

def process_data(input_string):
    # Perform some logic
    result = {
        "message": f"Python received: {input_string}",
        "status": "success",
        "length": len(input_string)
    }
    # Print the result as a JSON string so JS can parse it easily
    print(json.dumps(result))

if __name__ == "__main__":
    # sys.argv[1] is the first argument passed from JS
    if len(sys.argv) > 1:
        process_data(sys.argv[1])