def getContent(fileName):
    try:
        with open(fileName, 'r') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        return "File not found."
    except Exception as e:
        return f"An error occurred: {e}"

def getFileLines(filename):
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
        return [line.strip() for line in lines]
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def writeToFile(filename, content):
    try:
        with open(filename, 'w') as file:
            file.write(content)
        print(f"Content successfully written to {filename}")
    except Exception as e:
        print(f"An error occurred: {e}")

