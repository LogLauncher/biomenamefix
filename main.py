import time
import json
import zipfile
import streamlit as st


def check_for_biome_folders(zip_file):
    global start
    start = time.time()
    with zipfile.ZipFile(zip_file, 'r') as myzip:
        contents = myzip.namelist()
        data_folders = [f for f in contents if f.startswith('data/') and f.endswith('/')]
        biome_folders = []
        for folder in data_folders:
            folder_contents = myzip.namelist()
            biome_base_folder = folder + "worldgen/biome/"
            # Check if the biome folder exists
            if biome_base_folder in folder_contents and "/tags/" not in folder:
                biome_folders.append(biome_base_folder)
                # Look for subfolders within the biome folder
                for item in contents:
                    if item.startswith(biome_base_folder) and item.endswith('/') and item != biome_base_folder:
                        biome_folders.append(item)
        global end
        end = time.time()
        return biome_folders


def create_json_file(zip_files):
    biome_data = {}

    for zip_file in zip_files:
        with zipfile.ZipFile(zip_file, 'r') as myzip:
            folder_contents = myzip.namelist()
            biome_files = []
            
            # Find all JSON files under biome directories (including subfolders)
            for f in folder_contents:
                if (f.startswith('data/') and 
                    not f.endswith('/') and 
                    f.endswith('.json') and 
                    "worldgen/biome/" in f and 
                    "/tags/" not in f):
                    biome_files.append(f)

            for f in biome_files:
                json_name = f.split("/")[-1].replace(".json", "")
                # Extract path parts
                path_parts = f.split("/")
                namespace_index = path_parts.index("data") + 1
                
                if namespace_index < len(path_parts):
                    namespace_name = path_parts[namespace_index]
                    
                    # Find the biome folder index to extract subfolder structure
                    biome_index = path_parts.index("biome")
                    
                    # Extract subfolder structure (if any) between biome folder and file
                    subfolder_path = "."
                    if len(path_parts) > biome_index + 2:  # biome + filename + at least one subfolder
                        subfolders = path_parts[biome_index+1:-1]  # Everything between biome and filename
                        if subfolders:
                            subfolder_path += ".".join(subfolders) + "/"
                    
                    # Create a key that includes subfolder structure
                    biome_key = f"biome.{namespace_name}{subfolder_path}{json_name}"
                    display_name = json_name.replace("_", " ").title()
                    biome_data[biome_key] = display_name
    return biome_data


def main():
    st.set_page_config(page_title="Biome Name Fix", page_icon="🏝️")
    st.write("""
        # Biome Name Fix Generator
        
        When using datapacks that add new biomes, you may notice that mods such as Xaero's Minimap, Journeymap, and MiniHUD display untranslated biome names as 'biome.namespace.biomename,' which isn't very pretty.

        This tool solves that issue by generating a language file that you can place in a [resource pack](https://minecraft.wiki/w/Resource_pack#Language) or mod.
    """)
    st.image('https://i.postimg.cc/YSZv9z51/bnf.png', width='content')
    files = st.file_uploader("Upload a datapack or mod", type=["zip", "jar"], accept_multiple_files=True)

    biome_folders = []
    if files:
        for file in files:
            if file is not None:
                folders = check_for_biome_folders(file)
                for f in folders:
                    biome_folders.append(f)

        if len(biome_folders) > 0:
            st.info("Biomes were found in the following locations:")
            for folder in biome_folders:
                st.write(folder)
            st.caption("Parsed in " + str(int((end - start)*1000)) + "ms")
            json_data = create_json_file(files)
            st.download_button("Download JSON file", json.dumps(json_data, indent=2), file_name="en_us.json", type="primary")
        else:
            st.error("No biomes were found.")


if __name__ == "__main__":
    main()
