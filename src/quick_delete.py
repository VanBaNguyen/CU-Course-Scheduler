import os
import shutil

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEDULE_DIR = os.path.join(SCRIPT_DIR, "schedules")

WHITELIST = {""}

def delete_nonwhitelist_subfolders(schedule_dir, whitelist):
    print(f"Looking in: {schedule_dir}")
    if not os.path.exists(schedule_dir):
        print("Directory does not exist!")
        return

    print("Contents of the directory:")
    for folder_name in os.listdir(schedule_dir):
        print(f"  - {folder_name} (isdir: {os.path.isdir(os.path.join(schedule_dir, folder_name))})")

    folders_to_delete = []
    for folder_name in os.listdir(schedule_dir):
        full_folder_path = os.path.join(schedule_dir, folder_name)
        if os.path.isdir(full_folder_path) and folder_name not in whitelist:
            folders_to_delete.append(full_folder_path)

    if not folders_to_delete:
        print("Nothing to delete.")
        return

    print("The following folders will be DELETED:")
    for folder in folders_to_delete:
        print(f"  - {folder}")

    confirm = input("\nAre you sure you want to delete these folders? (y/N): ").strip().lower()
    if confirm in {'y', 'yes'}:
        for folder in folders_to_delete:
            print(f"Deleting: {folder} ...", end="")
            shutil.rmtree(folder)
            print(" Done.")
        print("All selected folders deleted.")
    else:
        print("Aborted. No folders were deleted.")

if __name__ == "__main__":
    delete_nonwhitelist_subfolders(SCHEDULE_DIR, WHITELIST)
