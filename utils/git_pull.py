import os
import subprocess
import concurrent.futures

def git_pull(path):
    git_dir = os.path.join(path, ".git")
    if os.path.exists(git_dir):
        os.chdir(path)
        subprocess.run(['git', 'pull'])
        return f"Git pull executed in {path}"
    else:
        return f"No Git repository found in {path}"

def git_pull_recursive(root_path):
    results = []
    
    def process_dir(subdir_path):
        result = git_pull(subdir_path)
        results.append(result)
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for root, dirs, files in os.walk(root_path):
            if '.git' in dirs:
                dirs.remove('.git')  # Skip further traversal if ".git" is found in subfolders
            for dir in dirs:
                subdir_path = os.path.join(root, dir)
                executor.submit(process_dir, subdir_path)
    
    return results

def git_pull_in_subfolders(path, updateFunc):
    root_path = path 
    if not os.path.exists(root_path):
        print(f"The specified path '{root_path}' does not exist.")
    else:
        status_update_func = updateFunc
        # Check for a ".git" folder in path
        results = []
        results.append(git_pull(root_path))
        
        # git pull operation recursively on folders with a ".git" folder
        results.extend(git_pull_recursive(root_path))
        
        if status_update_func:
            for result in results:
                status_update_func(result)
    
        print("Git pull operation completed.")
