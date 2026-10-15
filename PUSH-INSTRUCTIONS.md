# Push instructions (Aldo's one tap)

The repo is fully built and tested locally at
`~/workspace/oss/prompt-injection-evals/`. Creating the GitHub repo is an
account action — your tap:

## Option A — GitHub CLI (fastest)

```bash
cd ~/workspace/oss/prompt-injection-evals
gh repo create prompt-injection-evals --public \
  --description "58-case open test suite for AI-agent prompt-injection resistance"
git init -b main
git add .
git commit -m "prompt-injection-evals: 58-case open test suite (defensive)"
git remote add origin https://github.com/<your-username>/prompt-injection-evals.git
git push -u origin main
```

## Option B — web UI

1. github.com → New repository → name `prompt-injection-evals`, Public,
   do NOT initialize with README (we have one).
2. Then run from the repo dir:
   ```bash
   git init -b main && git add . && git commit -m "initial" \
     && git remote add origin https://github.com/<your-username>/prompt-injection-evals.git \
     && git push -u origin main
   ```

## After pushing (traffic taps)

- Add repo topics: `prompt-injection`, `ai-safety`, `llm-security`,
  `red-teaming`, `ai-agents`, `security-testing`.
- Pin the repo on your GitHub profile.
- Announce: X thread + the "Homelab Security Diaries" dev.to series +
  r/AI_Agents (pre-flight checklist first) + TLDR submit form.
- Suggested awesome-list PR (check current CONTRIBUTING rules first):
  awesome lists for LLM security / AI red-teaming.
