import re

# Regex patterns to identify changes
file_change_start = re.compile(r'^Index: (.+)')
change_block_start = re.compile(r'^@@')
method_signature = re.compile(r'^[\+\-]\s*(public|private|protected|internal)(\s+(static))?[\s\S]+?\)')
method_name = re.compile(r'\b(\w+)\s*\(')


def categorize_method_changes(patch_lines):
    new_methods = []
    updated_methods = []
    deleted_methods = []
    current_file = None

    # Temporary storage for methods before deciding if they are new, updated, or deleted
    possible_updates = {}

    for line in patch_lines:
        if file_change_start.match(line):
            current_file = file_change_start.match(line).group(1)
        elif change_block_start.match(line):
            pass  # Skip the change block lines
        elif method_signature.match(line):
            signature = line[1:].strip()  # Remove the leading +/-
            method_match = method_name.search(signature)
            if method_match:
                method = method_match.group(1)

                if line.startswith('+'):
                    if method in possible_updates:
                        # If the method was removed and now added, it's an update
                        updated_methods.append((current_file, signature))
                        del possible_updates[method]
                    else:
                        # Otherwise, it's a new method
                        new_methods.append((current_file, signature))
                elif line.startswith('-'):
                    possible_updates[method] = (current_file, signature)

    # Whatever left in possible_updates are deleted methods
    deleted_methods.extend(possible_updates.values())

    return new_methods, updated_methods, deleted_methods


# Parse the provided patch content
patch_file_path = 'v13.patch'

# Read the contents of the patch file
with open(patch_file_path, 'r') as file:
    patch_content = file.read()

# Split the content into lines
patch_lines = patch_content.splitlines()

# Get categorized changes
new_methods, updated_methods, deleted_methods = categorize_method_changes(patch_lines)

# Display categorized changes
print("New Methods:")
for file, method in new_methods:
    print(f"{file}: {method}")

print("\nUpdated Methods:")
for file, method in updated_methods:
    print(f"{file}: {method}")

print("\nDeleted Methods:")
for file, method in deleted_methods:
    print(f"{file}: {method}")
