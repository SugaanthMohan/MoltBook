import os
from git import Repo
from atlassian import Confluence
from pathlib import Path

# GitHub Ingestor using GitPython [6, 7]
def fetch_github(repo_url, local_path="raw/github_repo"):
    if os.path.exists(local_path):
        repo = Repo(local_path)
        repo.remotes.origin.pull()
    else:
        repo = Repo.clone_from(repo_url, local_path)
    # Recursively collect text from.md and.py files
    content = ""
    for path in Path(local_path).rglob("*"):
        if path.suffix in [".md", ".py"] and ".git" not in str(path):
            content += f"\n\n-- FILE: {path.name} --\n" + path.read_text(errors='ignore')
    return content

# Confluence Ingestor using Atlassian API [8, 9]
def fetch_confluence(page_id):
    confluence = Confluence(url=os.getenv("CONF_URL"), token=os.getenv("CONF_TOKEN"))
    page = confluence.get_page_by_id(page_id, expand='body.storage')
    return page['body']['storage']['value']
