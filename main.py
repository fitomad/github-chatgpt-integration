import argparse
import openai
import os
import requests
from github import Github, PullRequest

github_client: Github
parameters: dict

def code_review(parameters: dict):
    repo = github_client.get_repo(os.getenv('GITHUB_REPOSITORY'))
    pull_request = repo.get_pull(parameters["pr_id"])

    resume = make_resume_for_pull_request(pr=pull_request)
    
    try:
        pull_request.create_issue_comment(resume)
    except Exception as ex:
        error_message = str(ex)
        if "Resource not accessible by integration" in error_message or "403" in error_message:
            error_msg = (
                "🚨 **Code Review Failed**\n\n"
                "The GitHub token or app does not have the required permissions to post comments.\n\n"
                "**For GitHub App tokens:**\n"
                "- Ensure your GitHub App has the `issues: write` permission\n"
                "- See the README for setup instructions\n\n"
                "**For Personal Access Tokens:**\n"
                "- Ensure the token has `repo` or `public_repo` scope\n"
                f"\n**Error:** `{error_message}`"
            )
        else:
            error_msg = f"🚨 Failed to post initial review comment.\n\n`{error_message}`"
        
        try:
            pull_request.create_issue_comment(error_msg)
        except:
            print(f"Failed to post error message: {error_msg}")
        raise

    commits = pull_request.get_commits()

    for commit in commits:
        files = commit.files

        for file in files:
            filename = file.filename
            content = repo.get_contents(filename, ref=commit.sha).decoded_content

            try:
                response = openai.ChatCompletion.create(
                    model=parameters['model'],
                    messages=[
                        {
                            "role" : "user",
                            "content" : (f"{parameters['prompt']}:\n```{content}```")
                        }
                    ],
                    temperature=parameters['temperature']
                )

                pull_request.create_issue_comment(f"ChatGPT's review about `{file.filename}` file:\n {response['choices'][0]['message']['content']}")
            except Exception as ex:
                message = f"🚨 Fail code review process for file **{filename}**.\n\n`{str(ex)}`"
                try:
                    pull_request.create_issue_comment(message)
                except:
                    print(f"Failed to post error message for file {filename}: {str(ex)}")


def make_prompt(dev_lang: str) -> str:
    review_prompt = f"Review this {dev_lang} code for potential bugs or Code Smells and suggest improvements. Generate your response in markdown format"

    return review_prompt


def make_resume_for_pull_request(pr: PullRequest) -> str:
    comment = f"""
    Starting review process for this pull request send by **{pr.user.name}**
    **Commits** in this pull request: {pr.commits}

    **Additions**: {pr.additions}
    **Changed** files: {pr.changed_files}
    **Deletions**: {pr.deletions}
    """

    comment = comment.format(length='multi-line', ordinal='second')

    return comment


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--openai-api-key', help='Your OpenAI API Key')
    parser.add_argument('--github-token', help='Your Github Token')
    parser.add_argument('--github-pr-id', help='Your Github PR ID')
    parser.add_argument('--dev-lang', help='Development language used for this request')
    parser.add_argument('--openai-engine', default="gpt-3.5-turbo", help='GPT-3.5 model to use. Options: text-davinci-003, text-davinci-002, text-babbage-001, text-curie-001, text-ada-001')
    parser.add_argument('--openai-temperature', default=0.0, help='Sampling temperature to use. Higher values means the model will take more risks. Recommended: 0.5')
    parser.add_argument('--openai-max-tokens', default=4096, help='The maximum number of tokens to generate in the completion.')
    
    args = parser.parse_args()

    openai.api_key = args.openai_api_key
    github_client = Github(args.github_token)

    review_parameters = {
        "pr_id" : int(args.github_pr_id),
        "prompt" : make_prompt(dev_lang=args.dev_lang),
        "temperature" : float(args.openai_temperature),
        "max_tokens" : int(args.openai_max_tokens),
        "model" : args.openai_engine
    }

    code_review(parameters=review_parameters)
