import os
import shutil

def create_project_folder_on_desktop(folder_name):
    """
    Create a folder on the desktop with the specified name.
    """
    desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    project_folder_path = os.path.join(desktop_path, folder_name)
    if not os.path.exists(project_folder_path):
        os.makedirs(project_folder_path)
    return project_folder_path

def copy_and_rename_files(source_folder, destination_folder):
    """
    Copy and rename .h, .cpp, and .ino files from the source folder to the destination folder.
    """
    for file_name in os.listdir(source_folder):
        if file_name.endswith(('.h', '.cpp', '.ino')):
            file_path = os.path.join(source_folder, file_name)
            try:
                # Ouverture du fichier avec gestion d'encodage UTF-8 et erreurs ignorées
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                    content = file.read()
                
                # Extraction du nom de base et extension du fichier
                file_base_name, file_extension = os.path.splitext(file_name)
                
                # Nouveau nom de fichier avec le suffixe de l'extension
                new_file_name = f"{file_base_name}_{file_extension[1:]}.txt"
                new_file_path = os.path.join(destination_folder, new_file_name)
                
                # Écriture du contenu dans le nouveau fichier
                with open(new_file_path, 'w', encoding='utf-8') as new_file:
                    new_file.write(content)
                
            except Exception as e:
                print(f"Error processing file {file_name}: {e}")

def copy_and_rename_additional_files(source_folder, destination_folder):
    """
    Recursively copy and rename .py, .md, .env, and .ipynb files from the source folder 
    and its subfolders to the destination folder, excluding __init__.py and files of 0 KB.
    """
    for root, dirs, files in os.walk(source_folder):
        for file_name in files:
            if file_name.endswith(('.py', '.md', '.env', '.ipynb')) and file_name != "__init__.py":
                file_path = os.path.join(root, file_name)
                if os.path.getsize(file_path) > 0:  # Ignore files of size 0 Ko
                    try:
                        # Ouverture du fichier avec gestion d'encodage UTF-8 et erreurs ignorées
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                            content = file.read()
                        
                        # Extraction du nom de base et extension du fichier
                        file_base_name, file_extension = os.path.splitext(file_name)
                        
                        # Nouveau nom de fichier avec le suffixe de l'extension
                        new_file_name = f"{file_base_name}_{file_extension[1:]}.txt"
                        new_file_path = os.path.join(destination_folder, new_file_name)
                        
                        # Écriture du contenu dans le nouveau fichier
                        with open(new_file_path, 'w', encoding='utf-8') as new_file:
                            new_file.write(content)
                    
                    except Exception as e:
                        print(f"Error processing file {file_name}: {e}")

def main():
    """
    Main function to define source and destination folders and execute file copy and rename.
    """

    # source_folder = r"E:/Programmation/GitHub/BIOREACTOR_DESIGN"

    # source_folder = r"E:/Programmation/GitHub/BIOREACTOR/integration/arduino_mega/Main"
    # source_folder = r"E:/Programmation/GitHub/BIOREACTOR/integration/HETEROTROPHIC/XS/teensy/Main"
    # source_folder = r"E:/Programmation/GitHub/Quant_Trading_Framework/src"
    # source_folder = r"E:/Programmation/GitHub/BIOREACTOR/development/communication/MQTT_FreeRTOS_OTA_WebControl_ESP32/MQTT_FreeRTOS_OTA_WebControl_ESP32"
    # source_folder = r"E:/Programmation/GitHub/BIOREACTOR/integration/HETEROTROPHIC/WATER_BATH/main"
    # source_folder = r"E:/Programmation/GitHub/BIOREACTOR/integration/HETEROTROPHIC/XS/teensy/Main"
    source_folder =r"E:/Programmation/GitHub/BIOREACTOR/integration/SERVER/raspberry_pi/ServerFastAPI/ServerFastAPI/frontend/src/components"
    
    #source_folder = r"E:/Programmation/GitHub/BIOREACTOR/integration/PROCESS/WATER_HEATER/WATER_HEATER_ESP32"
    #source_folder = r"E:/Programmation/GitHub/BIOREACTOR"
    
    
    destination_folder = create_project_folder_on_desktop("Project Copy txt")

    copy_and_rename_files(source_folder, destination_folder)
    copy_and_rename_additional_files(source_folder, destination_folder)
    
    print(f"Files have been copied and renamed in {destination_folder}")

if __name__ == "__main__":
    main()
