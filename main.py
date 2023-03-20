import argparse
import openai
import os
import requests
from github import Github

github_client: Github

REVIEW_PROMPT = "Act as a Swift developer. Review this Swift code for potential bugs or Code Smells and suggest improvements."

def files_from_pull_request(pr_id: int):
    repo = github_client.get_repo(os.getenv('GITHUB_REPOSITORY'))
    pull_request = repo.get_pull(pr_id)

    resume = make_resume_for_pull_request(pr=pull_request_id)
    pull_request.create_issue_comment(resume)

    commits = pull_request.get_commits()

    for commit in commits:
        files = commit.files

        for file in files:
            filename = file.filename
            content = repo.get_contents(filename, ref=commit.sha).decoded_content

            response = openai.Completion.create(
                engine=args.openai_engine,
                prompt=(f"{REVIEW_PROMPT}:\n```{content}```"),
                temperature=float(args.openai_temperature),
                max_tokens=int(args.openai_max_tokens)
            )

            pull_request.create_issue_comment(f"ChatGPT's review about `{file.filename}` file:\n {response['choices'][0]['text']}")


def patch_from_pull_request(pr_id: int):
    repo = github_client.get_repo(os.getenv('GITHUB_REPOSITORY'))
    pull_request = repo.get_pull(pr_id)

    content = get_content_patch_from_pull_request(pr_id=pr_id)

    if len(content) == 0:
        pull_request.create_issue_comment(f"Patch file does not contain any changes")
        return

    parsed_text = content.split("diff")

    for diff_text in parsed_text:
        if len(diff_text) == 0:
            continue

        try:
            file_name = diff_text.split("b/")[1].splitlines()[0]
            print(file_name)

            response = openai.Completion.create(
                engine=args.openai_engine,
                prompt=(f"Summarize what was done in this diff:\n```{diff_text}```"),
                temperature=float(args.openai_temperature),
                max_tokens=int(args.openai_max_tokens)
            )
            print(response)
            print(response['choices'][0]['text'])

            pull_request.create_issue_comment(f"ChatGPT's response about ``{file_name}``:\n {response['choices'][0]['text']}")
        except Exception as e:
            error_message = str(e)
            print(error_message)
            pull_request.create_issue_comment(f"ChatGPT was unable to process the response about {file_name}")


def get_content_patch_from_pull_request(pr_id: int):
    url = f"https://api.github.com/repos/{os.getenv('GITHUB_REPOSITORY')}/pulls/{pr_id}"
    print(url)

    headers = {
        'Authorization': f"token {args.github_token}",
        'Accept': 'application/vnd.github.v3.diff'
    }

    response = requests.request("GET", url, headers=headers)

    if response.status_code != 200:
        raise Exception(response.text)

    return response.text

def make_resume_for_pull_request(pr: PullRequest) -> str:
    comment = f"""
    Starting review process for this pull request send by {pr.user.name}
    Commits in this pull request: {pr.commits}

    Additions: {pr.additions}
    Changed files: {pr.changed_files}
    Deletions: {pr.deletions}
    """

    return comment


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--openai-api-key', help='Your OpenAI API Key')
    parser.add_argument('--github-token', help='Your Github Token')
    parser.add_argument('--github-pr-id', help='Your Github PR ID')
    parser.add_argument('--openai-engine', default="text-davinci-003", help='GPT-3.5 model to use. Options: text-davinci-003, text-davinci-002, text-babbage-001, text-curie-001, text-ada-001')
    parser.add_argument('--openai-temperature', default=0.0, help='Sampling temperature to use. Higher values means the model will take more risks. Recommended: 0.5')
    parser.add_argument('--openai-max-tokens', default=4096, help='The maximum number of tokens to generate in the completion.')
    parser.add_argument('--mode', default="files", help='PR interpretation form. Options: files, patch')
    
    args = parser.parse_args()

    openai.api_key = args.openai_api_key
    github_client = Github(args.github_token)

    pull_request_id = int(args.github_pr_id)

    if(args.mode == "files"):
        files_from_pull_request(pr_id=pull_request_id)
    elif(args.mode == "patch"):
        patch_from_pull_request(pr_id=pull_request_id)
    else:
        print("Mode not recognized")
