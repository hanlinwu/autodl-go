# autodl-manager

Codex skill for managing AutoDL accounts, Pro container instances, images, GPU resources, and experiment lifecycle operations.

## Install

Install the skill into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills/autodl-manager
cp -R SKILL.md agents references scripts ~/.codex/skills/autodl-manager/
```

Or install from a cloned repository:

```bash
git clone https://github.com/<owner>/autodl-go.git
cd autodl-go
mkdir -p ~/.codex/skills/autodl-manager
cp -R SKILL.md agents references scripts ~/.codex/skills/autodl-manager/
```

Restart Codex after installation so the skill can be discovered.

## Configure AutoDL

Create an AutoDL developer token in the AutoDL console:

```text
AutoDL Console -> Account/Settings -> Developer Token
```

Then export it in your shell:

```bash
export AUTODL_TOKEN='your-autodl-token'
```

`AUTODL_API_TOKEN` is also supported.

## Use

Ask Codex to use the skill:

```text
Use $autodl-manager to check my AutoDL balance.
Use $autodl-manager to list my AutoDL Pro instances.
Use $autodl-manager to create a 1-GPU experiment instance from a PyTorch image.
```

The skill includes a small CLI for common API calls:

```bash
python3 scripts/autodl_api.py balance
python3 scripts/autodl_api.py instances
python3 scripts/autodl_api.py status pro-xxxxxxxxxxxx
python3 scripts/autodl_api.py snapshot pro-xxxxxxxxxxxx
```

Mutating operations such as creating, powering on, powering off, releasing instances, saving images, or switching storage should be confirmed before execution because they can affect billing or data.

## Contents

- `SKILL.md`: main Codex skill instructions
- `references/autodl-api.md`: AutoDL API notes and endpoint reference
- `scripts/autodl_api.py`: lightweight Python CLI for AutoDL developer APIs
- `agents/openai.yaml`: Codex UI metadata

## Validate

If you have the Codex skill creator utilities available:

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py .
python3 -m py_compile scripts/autodl_api.py
```
