import requests
import pandas as pd
from datetime import datetime, timedelta
from github import Github
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# GitHub API token
github_token = os.getenv('GITHUB_TOKEN')
organization = os.getenv('GITHUB_ORG')

# Initialize GitHub API client
g = Github(github_token)

def get_repo_stats(repo):
    # Basic stats
    stars = repo.stargazers_count
    forks = repo.forks_count
    watchers = repo.subscribers_count
    
    # Clones in last 14 days
    clones = sum(c.count for c in repo.get_clones_traffic(per='day')['clones'])
    
    # Visitors in last 14 days
    visitors = sum(v.count for v in repo.get_views_traffic(per='day')['views'])
    
    # Commits in last 30 days
    thirty_days_ago = datetime.now() - timedelta(days=30)
    commits = repo.get_commits(since=thirty_days_ago).totalCount
    
    # Open issues and pull requests
    open_issues = repo.open_issues_count
    open_prs = repo.get_pulls(state='open').totalCount
    
    # Contributors
    contributors = repo.get_contributors().totalCount
    
    # Size of repository
    size_kb = repo.size
    
    # Latest release info
    try:
        latest_release = repo.get_latest_release()
        release_date = latest_release.published_at
        release_downloads = sum(asset.download_count for asset in latest_release.get_assets())
    except:
        release_date = None
        release_downloads = 0
    
    return {
        'Repository': repo.name,
        'Stars': stars,
        'Forks': forks,
        'Watchers': watchers,
        'Clones (14 days)': clones,
        'Unique Visitors (14 days)': visitors,
        'Commits (30 days)': commits,
        'Open Issues': open_issues,
        'Open PRs': open_prs,
        'Contributors': contributors,
        'Size (KB)': size_kb,
        'Latest Release Date': release_date,
        'Release Downloads': release_downloads
    }

def main():
    org = g.get_organization(organization)
    repos = org.get_repos()
    
    stats = []
    for repo in repos:
        try:
            repo_stats = get_repo_stats(repo)
            stats.append(repo_stats)
            print(f"Processed {repo.name}")
        except Exception as e:
            print(f"Error processing {repo.name}: {str(e)}")
    
    df = pd.DataFrame(stats)
    df.to_csv('github_repo_stats.csv', index=False)
    print("Stats saved to github_repo_stats.csv")

if __name__ == "__main__":
    main()
