import os
import shutil

SCHEDULE_DIR = "schedules"

# This is a whitelist of subfolders that should not be deleted.
# PLEASE ADD YOUR SUBFOLDERS HERE.
WHITELIST = {""}

# I've literally accidentally deleted all my schedules before, so be careful with this script.

def delete_nonwhitelist_subfolders(schedule_dir, whitelist):
    schedule_path = os.path.abspath(schedule_dir)
    folders_to_delete = []
    for folder_name in os.listdir(schedule_path):
        full_folder_path = os.path.join(schedule_path, folder_name)
        if os.path.isdir(full_folder_path) and folder_name not in whitelist:
            folders_to_delete.append(full_folder_path)

    if not folders_to_delete:
        print("Nothing to delete.")
        return

    print("The following folders will be DELETED:")
    for folder in folders_to_delete:
        print(f"  - {folder}")

    confirm = input("\nAre you sure you want to delete these folders? (y/N): ").strip().lower()
    if confirm == 'y':
        for folder in folders_to_delete:
            shutil.rmtree(folder)
            print(f"Deleted: {folder}")
        print("Done.")
    else:
        print("Aborted. No folders were deleted.")

if __name__ == "__main__":
    delete_nonwhitelist_subfolders(SCHEDULE_DIR, WHITELIST)

# there's a chance people will run the program a lot and generate many unwanted subfolders