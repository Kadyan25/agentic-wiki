import os
import subprocess

ROOT = os.path.join(os.path.dirname(__file__), "..")


def sync(query: str = ""):
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPO")  # e.g. "Kadyan25/agentic-wiki"

    if not token or not repo:
        return  # not configured, skip silently

    try:
        # Set git identity
        subprocess.run(["git", "config", "user.email", "bot@agenticwiki.app"], cwd=ROOT, check=True)
        subprocess.run(["git", "config", "user.name", "Agentic Wiki Bot"], cwd=ROOT, check=True)

        # Embed token in remote URL
        remote_url = f"https://{token}@github.com/{repo}.git"
        subprocess.run(["git", "remote", "set-url", "origin", remote_url], cwd=ROOT, check=True)

        # Stage knowledge folder
        subprocess.run(["git", "add", "knowledge/"], cwd=ROOT, check=True)

        # Check if there is anything new to commit
        result = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT)
        if result.returncode == 0:
            return  # nothing changed

        short_query = query.strip()[:60] if query.strip() else "general query"
        commit_msg = f"knowledge update: {short_query}"
        subprocess.run(["git", "commit", "-m", commit_msg], cwd=ROOT, check=True)
        subprocess.run(["git", "push", "origin", "master"], cwd=ROOT, check=True)

    except subprocess.CalledProcessError:
        pass  # never break the query response over a sync failure
