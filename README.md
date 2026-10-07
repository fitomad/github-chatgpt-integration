# GitHub & ChatGPT integration

![python](https://img.shields.io/badge/python-3.9.6-blue) ![openai](https://img.shields.io/badge/OpenAI-0.27.2-orange)

This PoC is related to the integration of ChatGPT into a GitHub repository through [GitHub Actions](https://github.com/features/actions).

Actually there's no way to allow ChatGPT access a GitHub repository, inclusing the Pull Request permormed in any repository branch.

## Design

We will obtain this integration thanks to GitHub actions. This repository contains an Action that performs the following tasks.

* Pull Request checking and analizing, providing comments abou the repo.

## Use this action in your CI/CD

You need to create two secrets in order to run this action

* `OPENAI_API_KEY` Create an OpenAI developer account and obtain an API acces key
* `GH_TOKEN` Create a GitHub developer access token or use a GitHub App token

Other fields that you can customize are

* `dev-lang` Define the programming language using in your repository

### Using Personal Access Token (PAT)

```yaml
name: App Code Review

permissions:
  contents: read
  pull-requests: write

on:
  pull_request:
    types: [opened, reopened]

jobs:
  code-review:
    runs-on: ubuntu-latest
    steps:
      - uses: fitomad/github-chatgpt-integration@main
        with:
          openai-api-key: ${{ secrets.OPENAI_API_KEY }}
          github-token: ${{ secrets.GH_TOKEN }}
          github-pr-id: ${{ github.event.number }}
          dev-lang: Swift
          openai-max-tokens: 4096
```

### Using GitHub App Token

If you are using a GitHub App token (via `actions/create-github-app-token`), ensure your GitHub App has the following permissions:

* **Repository permissions:**
  - `contents: read` - To read repository contents
  - `pull_requests: read` - To read pull requests
  - `issues: write` - To create comments on pull requests

Example workflow:

```yaml
name: App Code Review with GitHub App

permissions:
  contents: read
  pull-requests: read

on:
  pull_request:
    types: [opened, reopened]

jobs:
  code-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/create-github-app-token@v1
        id: app-token
        with:
          app-id: ${{ env.APP_ID }}
          private-key: ${{ env.PRIVATE_KEY }}
      - uses: fitomad/github-chatgpt-integration@main
        with:
          openai-api-key: ${{ secrets.OPENAI_API_KEY }}
          github-token: ${{ steps.app-token.outputs.token }}
          github-pr-id: ${{ github.event.number }}
          dev-lang: c#
          openai-max-tokens: 4096
```

**Important:** When configuring your GitHub App, make sure to grant the `issues: write` permission so the action can post comments on pull requests.

## GitHub Action 

Our shell script must be executable. Make sure the `main.sh` file has execute permissions before using it in a workflow. You can modify the permission from your terminal using these commands.

Using the `update-index` parameter we will be sure that the execution flag will not be reseted every time we fork or create a new branch.

```zsh
$ git add entrypoint.sh
$ git update-index --chmod=+x entrypoint.sh
```

## Contact

* **Email** [adolfo.vera@globant.com](mailto:adolfo.vera@globant.com)
* **LinkedIn** [https://www.linkedin.com/in/adolfo-vera](https://www.linkedin.com/in/adolfo-vera)
