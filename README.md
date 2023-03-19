# GitHub & ChatGPT integration

![python](https://img.shields.io/badge/python-3.9.6-blue) ![openai](https://img.shields.io/badge/OpenAI-0.27.2-orange)

This PoC is related to the integration of ChatGPT into a GitHub repository through [GitHub Actions](https://github.com/features/actions).

Actually there's no way to allow ChatGPT access a GitHub repository, inclusing the Pull Request permormed in any repository branch.

## Design

We will obtain this integration thanks to GitHub actions. This repository contains an Action that performs the following tasks.

* Pull Request checking and analizing, providing comments abou the repo.

## GitHub Action 

Our shell script must be executable. Make sure the `main.sh` file has execute permissions before using it in a workflow. You can modify the permission from your terminal using this command.

```zsh
chmod +x main.sh
```

## Contact

* **Email** [adolfo.vera@globant.com]()
* **LinkedIn** [https://www.linkedin/com]()
