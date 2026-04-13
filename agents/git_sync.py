import os
import subprocess
import logging

logger = logging.getLogger("git_sync")
logging.basicConfig(level=logging.INFO, format="[git_sync] %(message)s")

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _run(cmd: list, **kwargs) -> subprocess.CompletedProcess:
    logger.info("Running: %s", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True, **kwargs)
    if result.stdout.strip():
        logger.info("stdout: %s", result.stdout.strip())
    if result.stderr.strip():
        logger.info("stderr: %s", result.stderr.strip())
    logger.info("exit code: %d", result.returncode)
    return result


def sync(query: str = ""):
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPO")

    logger.info("=== git_sync.sync() called ===")
    logger.info("GITHUB_TOKEN present: %s", bool(token))
    logger.info("GITHUB_REPO: %s", repo)
    logger.info("ROOT: %s", ROOT)

    if not token or not repo:
        logger.info("Skipping — GITHUB_TOKEN or GITHUB_REPO not set.")
        return

    try:
        _run(["git", "config", "user.email", "bot@agenticwiki.app"], cwd=ROOT)
        _run(["git", "config", "user.name", "Agentic Wiki Bot"], cwd=ROOT)

        remote_url = f"https://{token}@github.com/{repo}.git"
        _run(["git", "remote", "set-url", "origin", remote_url], cwd=ROOT)

        _run(["git", "add", "knowledge/"], cwd=ROOT)

        diff = _run(["git", "diff", "--cached", "--stat"], cwd=ROOT)
        if not diff.stdout.strip():
            logger.info("Nothing to commit — knowledge base unchanged.")
            return

        short_query = query.strip()[:60] if query.strip() else "general query"
        commit_msg = f"knowledge update: {short_query}"
        commit = _run(["git", "commit", "-m", commit_msg], cwd=ROOT)
        if commit.returncode != 0:
            logger.info("Commit failed.")
            return

        push = _run(["git", "push", "origin", "master"], cwd=ROOT)
        if push.returncode == 0:
            logger.info("Push successful.")
        else:
            logger.info("Push failed.")

    except Exception as e:
        logger.info("Exception during sync: %s", str(e))
