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
    """Extract comprehensive statistics for a GitHub repository"""
    # Basic stats
    stars = repo.stargazers_count
    forks = repo.forks_count
    watchers = repo.subscribers_count
    
    # Traffic stats (clones and views in last 14 days)
    try:
        # Get clones traffic - returns Clones object with .clones attribute
        clones_traffic = repo.get_clones_traffic(per='day')
        clones = sum(c.count for c in clones_traffic.clones)
    except Exception as e:
        print(f"Warning: Could not get clone data for {repo.name}: {e}")
        clones = 0
    
    try:
        # Get views traffic - returns Views object with .views attribute
        views_traffic = repo.get_views_traffic(per='day')
        visitors = sum(v.count for v in views_traffic.views)
    except Exception as e:
        print(f"Warning: Could not get views data for {repo.name}: {e}")
        visitors = 0
    
    # Commits in last 30 days
    try:
        thirty_days_ago = datetime.now() - timedelta(days=30)
        commits = repo.get_commits(since=thirty_days_ago).totalCount
    except Exception as e:
        print(f"Warning: Could not get commits data for {repo.name}: {e}")
        commits = 0
    
    # Open issues and pull requests
    open_issues = repo.open_issues_count
    try:
        open_prs = repo.get_pulls(state='open').totalCount
    except Exception as e:
        print(f"Warning: Could not get PRs data for {repo.name}: {e}")
        open_prs = 0
    
    # Contributors count
    try:
        contributors = repo.get_contributors().totalCount
    except Exception as e:
        print(f"Warning: Could not get contributors data for {repo.name}: {e}")
        contributors = 0
    
    # Repository size
    size_kb = repo.size
    
    # Latest release information
    try:
        latest_release = repo.get_latest_release()
        release_date = latest_release.published_at
        release_downloads = sum(asset.download_count for asset in latest_release.get_assets())
    except Exception:
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
    """Main function to process all repositories in the organization"""
    try:
        org = g.get_organization(organization)
        repos = org.get_repos()
        
        stats = []
        processed_count = 0
        
        for repo in repos:
            try:
                repo_stats = get_repo_stats(repo)
                stats.append(repo_stats)
                processed_count += 1
                print(f"✓ Processed {repo.name} ({processed_count})")
            except Exception as e:
                print(f"✗ Error processing {repo.name}: {str(e)}")
        
        # Save results to CSV
        if stats:
            df = pd.DataFrame(stats)
            df.to_csv('github_repo_stats.csv', index=False)
            print(f"\n✓ Stats for {len(stats)} repositories saved to github_repo_stats.csv")
            
            # Display summary
            print(f"\nSummary:")
            print(f"- Total repositories processed: {len(stats)}")
            print(f"- Total stars across all repos: {df['Stars'].sum():,}")
            print(f"- Total forks across all repos: {df['Forks'].sum():,}")
        else:
            print("No repository stats were collected.")
            
    except Exception as e:
        print(f"Error accessing organization '{organization}': {str(e)}")
        print("Please check your GITHUB_TOKEN and GITHUB_ORG environment variables.")

if __name__ == "__main__":
    main()
