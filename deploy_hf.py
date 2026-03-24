import os
import sys
from huggingface_hub import HfApi

def deploy():
    try:
        api = HfApi()
        
        # Whoami to get the username
        user_info = api.whoami()
        username = user_info['name']
        repo_id = f"{username}/aura-splitter"
        
        print(f"Authenticated as: {username}")
        print(f"Creating Hugging Face Space: {repo_id}...")
        
        api.create_repo(
            repo_id=repo_id,
            repo_type="space",
            space_sdk="docker",
            private=False,
            exist_ok=True
        )
        print("Space is ready.")
        
        print("Uploading files...")
        api.upload_folder(
            folder_path=".",
            repo_id=repo_id,
            repo_type="space",
            ignore_patterns=[".git", "__pycache__", "uploads", "separated", "deploy_hf.py"]
        )
        
        print("\n" + "="*50)
        print("DEPLOYMENT SUCCESSFUL!")
        print(f"Your app will be live at: https://huggingface.co/spaces/{repo_id}")
        print("="*50)
        
    except Exception as e:
        print(f"Deployment failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    deploy()
