import os
import json
from pathlib import Path 
def generate_manifest(root_dir="data", output_file="manifest.json"):
    """
    Scans a directory for subfolders and JSON files, creating a manifest.json.
    """
    projects = {}
    
    # Check if the root directory exists
    if not os.path.isdir(root_dir):
        print(f"Error: Directory '{root_dir}' not found. Please create it and add your project folders.")
        return

    # Walk through the directory structure
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # We only care about the top-level folders inside the root directory
        if dirpath == root_dir:
            for dirname in sorted(dirnames):
                projects[dirname] = []
            continue

        # Get the current folder name
        current_project = str(Path(dirpath).parent.name) + '/' + os.path.basename(dirpath)

        # Add JSON files from the current folder to the manifest
        json_files = sorted([f for f in filenames if f.endswith('.json')])
        if json_files:
            projects[current_project] = [os.path.join(dirpath, f).replace('\\', '/') for f in json_files]
    for project in list(projects.keys()):
        if not projects[project]:
            del projects[project]
    # Write the manifest to a JSON file
    with open(output_file, 'w') as f:
        json.dump(projects, f, indent=2)

    print(f"Successfully generated '{output_file}' with {len(projects)} projects.")
    
# Run the script
if __name__ == "__main__":
    generate_manifest()


    
