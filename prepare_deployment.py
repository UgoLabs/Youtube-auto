import shutil
import os

def prepare_deployment():
    # Create deployment directory
    deploy_dir = "deployment"
    os.makedirs(deploy_dir, exist_ok=True)
    
    # Files to include
    files = [
        "main.py",
        "deploy.py",
        "youtube_auto.service",
        ".env",
        "client_secrets.json",
        "requirements.txt",
        "agent/image_generator.py",
        "utils/logging_utils.py",
        "utils/youtube_utils.py"
    ]
    
    # Copy files
    for file in files:
        if os.path.exists(file):
            if '/' in file:
                os.makedirs(os.path.join(deploy_dir, os.path.dirname(file)), exist_ok=True)
            shutil.copy2(file, os.path.join(deploy_dir, file))

if __name__ == "__main__":
    prepare_deployment()