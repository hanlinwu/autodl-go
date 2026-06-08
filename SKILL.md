---
name: autodl-manager
description: Manage AutoDL accounts, developer tokens, balances, Pro container instances, images, GPU compute resources, Jupyter/SSH access, and experiment lifecycle operations. Use when Codex needs to call AutoDL APIs, check account balance, list/create/start/stop/release AutoDL instances, save or choose images, select GPU specs for machine learning experiments, prepare remote experiment commands, or clean up paid AutoDL resources.
---

# AutoDL Manager

## Core Rules

- Use official AutoDL APIs at `https://api.autodl.com`; read `references/autodl-api.md` before constructing requests.
- Never ask the user to paste a token into chat if it can be read from `AUTODL_TOKEN`, `AUTODL_API_TOKEN`, or a local secrets file the user points to.
- Never print full tokens, `root_password`, Jupyter tokens, or private service domains in final answers. Redact secrets unless the user explicitly asks to reveal them.
- Treat create, power on, power off, release, save image, and NFS switching as live account operations. Before running them, summarize account, endpoint, instance UUID, GPU spec, GPU count, image UUID, disk expansion, and expected effect.
- Require explicit user confirmation before operations that create paid resources, release instances, overwrite startup commands, switch storage, or may affect experiment data.
- After any API call, check `code`. Treat only `Success` as success; otherwise report `msg`, `request_id`, and the exact operation attempted.

## Quick Workflow

1. Establish credentials with `AUTODL_TOKEN` or `AUTODL_API_TOKEN`.
2. Check balance before creating or starting resources.
3. List private images when the experiment depends on a saved environment.
4. Choose GPU spec, GPU count, data center, base/private image, CUDA floor, disk expansion, and optional startup command.
5. Create or power on the instance.
6. Poll status and snapshot until `running`; extract SSH/Jupyter access details only if needed.
7. Run the experiment through SSH/Jupyter using the user's repository commands.
8. Save an image when the environment matters, back up results, then power off resources when idle.
9. Release instances only after the user confirms data has been backed up and the instance is stopped.

## Bundled Tool

Use `scripts/autodl_api.py` for common API calls:

```bash
export AUTODL_TOKEN='...'
python3 /Users/hlwu/.codex/skills/autodl-manager/scripts/autodl_api.py balance
python3 /Users/hlwu/.codex/skills/autodl-manager/scripts/autodl_api.py instances --page-size 20
python3 /Users/hlwu/.codex/skills/autodl-manager/scripts/autodl_api.py status pro-xxxxxxxxxxxx
python3 /Users/hlwu/.codex/skills/autodl-manager/scripts/autodl_api.py snapshot pro-xxxxxxxxxxxx
```

For mutating calls, use the script only after confirmation:

```bash
python3 /Users/hlwu/.codex/skills/autodl-manager/scripts/autodl_api.py create \
  --gpu-spec pro6000-p --gpu-count 1 --image base-image-l2t43iu6uk --cuda-from 118 \
  --disk-gb 0 --name experiment-name --data-center westDC3 --start-command 'sleep 1'

python3 /Users/hlwu/.codex/skills/autodl-manager/scripts/autodl_api.py power-off pro-xxxxxxxxxxxx
python3 /Users/hlwu/.codex/skills/autodl-manager/scripts/autodl_api.py release pro-xxxxxxxxxxxx
```

## Experiment Guidance

- Prefer a private image for repeated experiments. Use a public base image only when the project setup is scripted and reproducible.
- Record instance UUID, GPU spec, image UUID, CUDA version floor, repository commit, and launch command in the user's experiment notes or repo artifacts when appropriate.
- Prefer startup commands for lightweight bootstrapping only. For long training, use a durable terminal/session approach requested by the user, such as SSH plus tmux, nohup, or the platform's daemon-process guidance.
- Back up datasets, checkpoints, logs, and final artifacts. AutoDL documentation says local SSD data has no redundancy guarantee; an instance's data is lost after release and may be released after 15 continuous powered-off days.
- Stop idle running instances promptly because billing starts when the instance status is running.

## References

- Read `references/autodl-api.md` for endpoint paths, request bodies, status interpretation, GPU spec IDs, public image UUIDs, and data-retention notes.
