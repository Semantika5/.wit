# Upload 174
import datetime
from distutils.dir_util import copy_tree
import filecmp
from graphviz import Digraph
import os
import random
import shutil
import sys


def init():
    current_path = os.getcwd()
    print(current_path)
    wit_folder = os.path.join(current_path, '.wit')
    images_folder = os.path.join(wit_folder, 'images')
    staging_area_folder = os.path.join(wit_folder, 'staging_area')
    folders = (wit_folder, images_folder, staging_area_folder)
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"New {folder} created.")
        else:
            print(f"{folder} already exists.")
    activated_branch = open(os.path.join(wit_folder, 'activated.txt'), 'w')
    activated_branch.write('master')
    activated_branch.close()


def add(src_path):
    wit_folder = os.path.join(os.getcwd(), '.wit')
    if not os.path.exists(wit_folder):
        print("Wit folder does not exist in current folder.")
    else:
        staging_area = os.path.join(wit_folder, 'staging_area')
        dst_path = os.path.join(staging_area, src_path)
        try:
            shutil.copytree(src_path, dst_path)
        except NotADirectoryError:
            try:
                shutil.copy(src_path, staging_area)
            except Exception as err:
                print(f"An error has occurred: {err}.")
        except FileExistsError:
            if os.path.exists(dst_path):
                shutil.rmtree(dst_path)
                shutil.copytree(src_path, dst_path)
            else:
                print("One of the files (or more) already exists... could not complit the adding action.")
        print(os.listdir(staging_area))


def does_wit_folder_exists():
    path = os.getcwd()
    if os.path.exists(os.path.join(path, '.wit')):
        return os.path.join(path, '.wit')
    else:
        while os.path.exists(path):
            path = os.path.dirname(path)
            if os.path.exists(os.path.join(path, '.wit')):
                return os.path.join(path, '.wit')
        return False


def commit(message):
    wit_folder_path = does_wit_folder_exists()
    if not wit_folder_path:
        print("The folder '.wit' does not exists in any of the parent folders and thus the function can not operate.")
    else:
        commit_id = "".join(random.choice("1234567890abcdef") for _ in range(40))
        commit_id_folder_path = os.path.join(os.path.join(wit_folder_path, 'images'), commit_id)
        commit_id_file_path = commit_id_folder_path + '.txt'
        if not os.path.exists(commit_id_folder_path):
            os.makedirs(commit_id_folder_path)
            txt_file = open(commit_id_file_path, 'w')
            if not os.path.exists(os.path.join(wit_folder_path, "references.txt")):
                txt_file.write("parent=None\n")
            else:
                references = open(os.path.join(wit_folder_path, "references.txt"), 'r')
                references_id_lines = references.readlines()
                previous_id = references_id_lines[0].split('=')[1]
                txt_file.write(f"parent={previous_id}")
                references.close()
            txt_file.write(f"date={datetime.datetime.now()}\n")
            txt_file.write(f"message={message}")
            txt_file.close()
        else:
            print("A folder with this commit ID already exists.")
        # Independently created
        # Same as https://stackoverflow.com/questions/15034151/copy-directory-contents-into-a-directory-with-python
        # By Prosseek- https://stackoverflow.com/users/260127/prosseek
        copy_tree(os.path.join(wit_folder_path, 'staging_area'), commit_id_folder_path)
        if os.path.exists(os.path.join(wit_folder_path, "references.txt")):
            references_file = open(os.path.join(wit_folder_path, "references.txt"), 'r')
            rfr_data = references_file.readlines()
            previous_commit_id = references_id_lines[0].split('=')[1].strip()
            rfr_data[0] = f"HEAD={commit_id}\n"
            if os.path.exists(os.path.join(wit_folder_path, "activated.txt")):
                activated = open(os.path.join(wit_folder_path, "activated.txt"), 'r')
                active_branch = activated.readlines()[0].strip()
                activated.close()
                counter = 0
                for line in rfr_data:
                    if line.split('=')[0].strip() == active_branch:
                        if line.split('=')[1].strip() == previous_commit_id:
                            rfr_data[counter] = f"{active_branch}={commit_id}"
                    counter = counter + 1
            references_file = open(os.path.join(wit_folder_path, "references.txt"), 'w')
            references_file.writelines(rfr_data)
            references_file.close()

        else:
            references_file = open(os.path.join(wit_folder_path, "references.txt"), 'w')
            references_file.write(f"HEAD={commit_id}\n")
            references_file.write(f"master={commit_id}\n")
            references_file.close()



def compare_folders(folder_path, folder_to_compare_with, file_exception=None):
    differences = []
    for file in os.listdir(folder_path):
        if file != file_exception:
            sub_folder_path = os.path.join(folder_path, file)
            sub_folder_to_compare_with_path = os.path.join(folder_to_compare_with, file)
            if os.path.isfile(sub_folder_path):
                file_comp = filecmp.cmp(sub_folder_path, sub_folder_to_compare_with_path, shallow=False)
                if not file_comp:
                    differences.append(file)
            elif os.path.isdir(sub_folder_path):
                sub_folders_differences = compare_folders(sub_folder_path, sub_folder_to_compare_with_path)
                differences.extend(sub_folders_differences)
            else:
                print(f"This file is not supported {sub_folder_path}")
        else:
            print(f"we did not compare the following directory {file}.")
    return differences


def status_prep():
    wit_folder_path = does_wit_folder_exists()
    if not wit_folder_path:
        print("The folder '.wit' does not exists in any of the parent folders and thus the function can not operate.")
    else:
        references = os.path.join(wit_folder_path, "references.txt")
        if not os.path.exists(references):
            print("There is no file that contains the references and thus the function can not operate.")
        else:
            references_file = open(references, 'r')
            references_id_lines = references_file.readlines()
            current_commit_id = references_id_lines[0].split('=')[1].strip()
            references_file.close()
            staging_area_path = os.path.join(wit_folder_path, 'staging_area')
            commit_files_path = os.path.join(os.path.join(wit_folder_path, 'images'), current_commit_id)
            comparison = filecmp.dircmp(staging_area_path, commit_files_path)
            files_before_commit = comparison.left_only
            changes_to_be_committed = ', '.join(files_before_commit)
            if len(changes_to_be_committed) == 0:
                changes_to_be_committed = None
            current_folder = os.getcwd()
            changes_not_staged = compare_folders(staging_area_path, current_folder)
            changes_not_staged_for_commit = ', '.join(changes_not_staged)
            if len(changes_not_staged_for_commit) == 0:
                changes_not_staged_for_commit = None
            parent_folders_comp = filecmp.dircmp(staging_area_path, current_folder)
            untracked_files = parent_folders_comp.right_only
            return(current_commit_id, changes_to_be_committed, changes_not_staged_for_commit, untracked_files)


def status():
    current_commit_id, changes_to_be_committed, changes_not_staged_for_commit, untracked_files = status_prep()
    print(f"commit id: {current_commit_id}")
    print(f"Changes to be committed: {changes_to_be_committed}.")
    print(f"Changes not staged for commit: {changes_not_staged_for_commit}.")
    if len(untracked_files) > 0:
        print(f"Untracked files: {', '.join(untracked_files)}.")
    else:
        print("Untracked files: None.")


def checkout(branch_or_commit_id):
    wit_folder_path = does_wit_folder_exists()
    current_folder = os.getcwd()
    if not wit_folder_path:
        print("The folder '.wit' does not exists in any of the parent folders and thus the function can not operate.")
    else:
        if branch_or_commit_id in get_all_branches_names():
        else:
            commit_id = branch_or_commit_id
        status_info = status_prep()
        to_be_commited = status_info[1]
        not_staged = status_info[2]
        untracked_list = status_info[3]
        if to_be_commited is not None or not_staged is not None:
            print("The folders are not updated and thus the checkout action can not be complitted.")
        else:
            updated_path = os.path.join(os.path.join(wit_folder_path, 'images'), commit_id)
            if os.path.exists(updated_path):
                for file in os.listdir(current_folder):
                    if file not in untracked_list:
                        current_path = os.path.join(current_folder, file)
                        if os.path.isfile(current_path):
                            os.remove(current_path)
                        elif os.path.isdir(current_path):
                            shutil.rmtree(current_path)
                        else:
                            print(f"Unknown file type: {file}.")
                staging_area_path = os.path.join(wit_folder_path, 'staging_area')
                shutil.rmtree(staging_area_path)
                copytree(updated_path, current_folder)  # Using local function 'copy_tree' because the dst foldes isn't empty.
                copy_tree(updated_path, staging_area_path)  # Using the module 'copytree'.
            else:
                print("The commit id that was inserted does not exist.")
            references = os.path.join(wit_folder_path, "references.txt")
            if not os.path.exists(references):
                print("There is no file that contains the references and thus the function can not complete the action.")
            else:
                references_file = open(references, 'r')
                r = references_file.readlines()
                r[0] = f"HEAD={commit_id}\n"
                references_file = open(references, 'w')
                references_file.writelines(r)
                references_file.close()


# Same as https://stackoverflow.com/questions/1868714/how-do-i-copy-an-entire-directory-of-files-into-an-existing-directory-using-pyth
# By atzz- https://stackoverflow.com/users/23252/atzz


def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


if len(sys.argv) == 2:
    if sys.argv[1] == 'init':
        init()
        print("INIT was called successfully.")
    elif sys.argv[1] == 'add':
        print("You must enter a path to backup.")
    elif sys.argv[1] == 'commit':
        print("You must enter a string as a message.")
    elif sys.argv[1] == 'status':
        status()
        print("Status was called successfully.")
    elif sys.argv[1] == 'checkout':
        print("You must enter a commit-id")
    else:
        print("The only arguments can be accepted are either 'init',add' or 'status'.")
elif len(sys.argv) == 3:
    if sys.argv[1] == 'add':
        full_path = os.path.join(os.getcwd(), sys.argv[2])
        if os.path.exists(full_path):
            add(sys.argv[2])
            print("Add was called successfully.")
        else:
            print("The path that was entered does not exist.")
    elif sys.argv[1] == 'commit':
        commit(sys.argv[2])
        print("Commit was called successfully.")
    elif sys.argv[1] == 'checkout':
        checkout(sys.argv[2])
        print("Checkout was called successfully.")
    else:
        print("The only functions can be called with an argument are either 'add', 'commit' or 'checkout'.")
else:
    print("Exactly one argument can be entered if you are calling the 'init' function.")
    print("Exactly one argument can be entered if you are calling the 'status' function.")
    print("Exactly two argument can be entered if you are calling the 'add' function.")
    print("Exactly two argument can be entered if you are calling the 'commit' function.")
    print("Exactly two argument can be entered if you are calling the 'checkout' function.")

def graph():
    wit_folder_path = does_wit_folder_exists()
    if not wit_folder_path:
        print("The folder '.wit' does not exists in any of the parent folders and thus the function can not operate.")
    else:
        commit_id_list = []
        rfr_path = os.path.join(wit_folder_path, 'references.txt')
        rfr = open(rfr_path, 'r')
        rfr_lines = rfr.readlines()
        head = rfr_lines[0].split('=')[1].strip()
        parent_path = head
        while parent_path != 'None':
            path_to_image_file = os.path.join(os.path.join(wit_folder_path, 'images'), parent_path + '.txt')
            if os.path.exists(path_to_image_file):
                commit_id_list.append(parent_path)
                image_file = open(path_to_image_file, 'r')
                r_image_file = image_file.readlines()
                parent_path = r_image_file[0].split('=')[1].strip()
            else: #  The parent file does not exist.
                parent_path = 'None'
        image_file.close()
        print(commit_id_list)
        dot = Digraph('Commit Id Tree', filename='graph_tree', format='png')
        descriptor = ord('A')
        for commit_id in commit_id_list:
            dot.node(chr(descriptor), commit_id)
            descriptor = descriptor + 1
        src = ord('A')
        dst = ord('B')
        edges_list = []
        for _ in range(len(commit_id_list) - 1):
            edges_list.append(f'{chr(src)}{chr(dst)}')
            src = src + 1
            dst = dst + 1
        print(edges_list)
        dot.edges(edges_list)
        dot.fillcolor("Blue")
        dot.view()


def get_all_branches_names():
    rfr_path = os.path.join(os.path.join(os.getcwd(), '.wit'), 'references.txt')
    rfr = open(rfr_path, 'r')
    rfr_file = rfr.readlines()
    all_branches = []
    for line in rfr_file:
        branch_name = line.split('=')[0].strip()
        all_branches.append(branch_name)

        
def branch(NAME):
    wit_folder_path = does_wit_folder_exists()
    if not wit_folder_path:
        print("The folder '.wit' does not exists in any of the parent folders and thus the function can not operate.")
    else:
        rfr_path = os.path.join(wit_folder_path, 'references.txt')
        rfr = open(rfr_path, 'r')
        rfr_lines = rfr.readlines()
        head = rfr_lines[0].split('=')[1].strip()
        rfr = open(rfr_path, 'a')
        rfr.write(f"{NAME}={head}\n")
        rfr.close()
        activated_branch = open(os.path.join(wit_folder_path, 'activated.txt'), 'w')
        activated_branch.write(NAME)
        activated_branch.close()

commit("b")
