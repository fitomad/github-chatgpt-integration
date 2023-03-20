import argparse
import openai
import os
import requests
from github import Github

github_client: Github

def code_review(pr_id: int, chatgpt_prompt: str):
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
                prompt=(f"{chatgpt_prompt}:\n```{content}```"),
                temperature=float(args.openai_temperature),
                max_tokens=int(args.openai_max_tokens)
            )

            pull_request.create_issue_comment(f"ChatGPT's review about `{file.filename}` file:\n {response['choices'][0]['text']}")


def make_prompt(dev_lang: str) -> str:
    review_prompt = f"Act as a {dev_lang} developer. Review this {dev_lang} code for potential bugs or Code Smells and suggest improvements."

    return review_prompt


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
    parser.add_argument('--dev-lang', help='Development language used for this request')
    parser.add_argument('--openai-engine', default="text-davinci-003", help='GPT-3.5 model to use. Options: text-davinci-003, text-davinci-002, text-babbage-001, text-curie-001, text-ada-001')
    parser.add_argument('--openai-temperature', default=0.0, help='Sampling temperature to use. Higher values means the model will take more risks. Recommended: 0.5')
    parser.add_argument('--openai-max-tokens', default=4096, help='The maximum number of tokens to generate in the completion.')
    
    args = parser.parse_args()

    openai.api_key = args.openai_api_key
    github_client = Github(args.github_token)

    pull_request_id = int(args.github_pr_id)
    prompt = make_prompt(dev_lang=args.dev_lang)

    code_review(pr_id=pull_request_id, chatgpt_prompt=prompt)
