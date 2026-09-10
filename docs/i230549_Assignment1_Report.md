# MLOps Assignment 1: CI Workflow with Pull Requests, Docker and a Container Registry

- **GitHub:** [@MustafaAhsanKhan](https://github.com/MustafaAhsanKhan)
- **Repository:** https://github.com/MustafaAhsanKhan/student-ml-api
- **Registry:** `ghcr.io/mustafaahsankhan/student-ml-api` (GitHub Container Registry, public)


## Quick reference

| Item | Value |
|---|---|
| Pull requests | [#1](https://github.com/MustafaAhsanKhan/student-ml-api/pull/1) prediction API → `v1.0.0`<br>[#3](https://github.com/MustafaAhsanKhan/student-ml-api/pull/3) gunicorn fix<br>[#2](https://github.com/MustafaAhsanKhan/student-ml-api/pull/2) model metadata → `v1.1.0`<br>[#4](https://github.com/MustafaAhsanKhan/student-ml-api/pull/4) this report |
| Release tags | `v1.0.0` → `95c63a7`, `v1.1.0` → `a1aa4d3` |
| Failed CI run | [34458945901](https://github.com/MustafaAhsanKhan/student-ml-api/actions/runs/34458945901) |
| Successful CI run | [34459093347](https://github.com/MustafaAhsanKhan/student-ml-api/actions/runs/34459093347) |
| Successful release runs | [v1.0.0: 34459346321](https://github.com/MustafaAhsanKhan/student-ml-api/actions/runs/34459346321), [v1.1.0: 34460769060](https://github.com/MustafaAhsanKhan/student-ml-api/actions/runs/34460769060) |
| Image `1.0.0` (= `95c63a7`) | `sha256:cdaa960e36bce8b0cab3cc815b1d452df89e8caa03aae8d38301c5730aa96013` |
| Image `1.1.0` (= `a1aa4d3` = `latest`) | `sha256:a38679a1ad792e71e4d6cf74195671b711f82c95ec8d4687768e729829e63ea0` |

## Repository structure

```
student-ml-api/
├── app.py
├── requirements.txt          # runtime dependencies (pinned)
├── requirements-dev.txt      # adds pytest, used for testing only
├── pytest.ini
├── Dockerfile
├── .dockerignore
├── VERSION
├── tests/
│   └── test_app.py
├── docs/
│   ├── REPORT.md
│   └── evidence/
└── .github/
    └── workflows/
        ├── ci.yml
        └── release.yml
```

Two small additions to the suggested layout:
- `requirements-dev.txt` means pytest is installed in CI but not shipped in the production image.
- `pytest.ini` means a plain `pytest` from the repo root can import `app.py`.

---

## Part 1: Application

`app.py` is a Flask app. Inside the container it is served by gunicorn.

- **`GET /health`** returns the status, the application name and the version. The version is read from the `VERSION` file, so it is defined in exactly one place.
- **`POST /predict`** takes `{"value": <number>}` and returns `value * 2`.
- **Invalid requests** get a `400` with an `error` message when:
  - the body isn't JSON,
  - `value` is missing, or
  - `value` isn't a finite number.

  Booleans are rejected explicitly because in Python `True` is an `int`.

Version 1.0.0:

```
$ curl -s http://localhost:5001/health
{"status":"healthy","application":"student-ml-api","version":"1.0.0"}

$ curl -s -X POST http://localhost:5001/predict -H 'Content-Type: application/json' -d '{"value": 10}'
{"input":10,"prediction":20}
```

Version 1.1.0 (Part 18):

```
{"status":"healthy","application":"student-ml-api","application_version":"1.1.0","model_version":"model-1"}
```

## Part 2: Automated tests

`tests/test_app.py` has 5 test functions, parametrized into **15 test cases**:

| Requirement | Test | Cases |
|---|---|---|
| `/health` | `test_health` | status 200, full response body, version equals `VERSION` |
| Successful `/predict` | `test_predict_success` | 10→20, 0→0, -3→-6, 2.5→5.0 |
| Missing input | `test_predict_missing_value` | `{}`, `{"val": 10}`, no body |
| Invalid input | `test_predict_invalid_value` | `"ten"`, `null`, `true`, `[10]`, `{"number": 10}`, `NaN` |
| Invalid input (not JSON) | `test_predict_rejects_non_json_body` | `text/plain` body |

```
$ pytest -q
...............                                                          [100%]
15 passed in 0.08s
```

## Part 3: Git workflow

All development happened on branches and reached `main` through pull requests. The only commit made directly on `main` is the very first one (`6ff90ec`, README and `.gitignore`), which was needed to create the default branch that PRs target.

| Branch | Purpose |
|---|---|
| `feature/prediction-api` | application, tests, Docker, CI and release workflows |
| `fix/gunicorn-control-socket` | fix for an error found while inspecting the container |
| `feature/model-metadata` | version 1.1.0 |
| `docs/assignment-report` | this report and the evidence |

Commits use the Conventional Commits prefixes (`feat:`, `test:`, `build:`, `ci:`, `fix:`, `docs:`, `chore:`), and each commit does one thing. Here is the history of `main` at `v1.1.0` (with decorations in [`evidence/git-history.txt`](evidence/git-history.txt)):

```
*   a1aa4d3 Merge pull request #2 from MustafaAhsanKhan/feature/model-metadata      <- v1.1.0
|\
| *   96ed34e Merge branch 'main' into feature/model-metadata
| |\
| |/
|/|
* |   4c9e510 Merge pull request #3 from MustafaAhsanKhan/fix/gunicorn-control-socket
|\ \
| * | 7ee95a2 fix: disable gunicorn control socket in container
|/ /
| * db5a037 docs: update health response example in README
| * 2f73e3e chore: bump version to 1.1.0
| * 798297e test: update health endpoint test for model metadata
| * 3edea83 feat: add application and model version metadata to /health
|/
*   95c63a7 Merge pull request #1 from MustafaAhsanKhan/feature/prediction-api      <- v1.0.0
|\
| * 7be3d89 fix: correct health endpoint test
| * 62efebf test: intentionally break health status assertion to verify CI gate
| * 3b0b34c docs: document API usage, Docker and release workflow
| * 4da5dc1 ci: publish commit SHA image tag on release
| * bb6a6cd build: add OCI metadata labels to the Docker image
| * bf2c559 ci: add tag-based release workflow for GHCR
| * 5838021 ci: add pull request CI workflow
| * c407b90 build: add production Dockerfile and .dockerignore
| * aa8705c test: add API unit tests
| * 6978f44 feat: add prediction endpoint
| * 52c1ad7 feat: add Flask app with health endpoint
|/
* 6ff90ec chore: initial repository setup
```

## Part 4: Pull requests

Each PR description has five sections: **Summary**, **Changes**, **Testing Performed**, **Docker Impact** and **Checklist**. Before merging, I left a review on the PR listing what I checked. I merged only once both required checks were green.

| PR | Branch | Content | CI runs |
|---|---|---|---|
| [#1](https://github.com/MustafaAhsanKhan/student-ml-api/pull/1) | `feature/prediction-api` | API, tests, Dockerfile, CI and release workflows | ✅ [34458790101](https://github.com/MustafaAhsanKhan/student-ml-api/actions/runs/34458790101)<br>❌ [34458945901](https://github.com/MustafaAhsanKhan/student-ml-api/actions/runs/34458945901) (deliberate failure)<br>✅ [34459093347](https://github.com/MustafaAhsanKhan/student-ml-api/actions/runs/34459093347) |
| [#3](https://github.com/MustafaAhsanKhan/student-ml-api/pull/3) | `fix/gunicorn-control-socket` | removes a startup error from the container logs | ✅ [34460560143](https://github.com/MustafaAhsanKhan/student-ml-api/actions/runs/34460560143) |
| [#2](https://github.com/MustafaAhsanKhan/student-ml-api/pull/2) | `feature/model-metadata` | model metadata in `/health`, version 1.1.0 | ✅ [34460196723](https://github.com/MustafaAhsanKhan/student-ml-api/actions/runs/34460196723)<br>✅ [34460700109](https://github.com/MustafaAhsanKhan/student-ml-api/actions/runs/34460700109) (after updating with `main`) |
| [#4](https://github.com/MustafaAhsanKhan/student-ml-api/pull/4) | `docs/assignment-report` | this report and the evidence | runs on the PR |

PR #3 was opened after #2 but merged first. Because `main` requires branches to be up to date, #2 then had to be updated with `main`, and CI ran again on the combined code before #2 could merge.

Screenshots:
- [PR #1 merged](evidence/06-pr1-merged.png)
- [PR #2 merged](evidence/13-pr2-merged.png)
- [pull request list](evidence/10-pull-requests.png)
- [Actions runs](evidence/12-actions-runs.png)

## Part 5: CI workflow (`.github/workflows/ci.yml`)

Trigger: `pull_request` targeting `main`. I didn't add a separate `push` trigger for feature branches. Every push to an open PR already runs CI, so a second trigger would only run the same checks twice.

```
PR
 ├── Unit Tests (job)
 │     ├── Checkout code              actions/checkout@v7
 │     ├── Set up Python 3.13         actions/setup-python@v7 (pip cache)
 │     ├── Install dependencies       pip install -r requirements-dev.txt
 │     └── Run unit tests             pytest -v
 └── Docker Build Validation (job, needs: Unit Tests)
       ├── Checkout code
       ├── Build Docker image         docker build -t student-ml-api:pr-<number> .
       └── Smoke test container       docker run, then curl /health (retries for 15 s)
```

How the workflow behaves:
- **No push.** The image is built but never pushed. The workflow only has `permissions: contents: read`, so it couldn't push to GHCR even by mistake.
- **If `pytest` fails,** the Unit Tests job fails, Docker Build Validation doesn't run, and the PR shows as failed.
- **If `docker build` fails,** or the container doesn't answer on `/health`, the Docker Build Validation job fails.
- **Merge is blocked.** Both job names are required status checks on `main` (Part 7), so a failing PR can't be merged.

The smoke test goes a step beyond "does it build". It catches runtime problems such as a missing dependency or an app bound to `127.0.0.1` (Part 26). A successful `docker build` alone would not catch those.

## Part 6: Deliberate failure

On PR #1, I changed the health test to `assert data["status"] == "wrong"` and pushed it as commit `62efebf`.

Run [34458945901](https://github.com/MustafaAhsanKhan/student-ml-api/actions/runs/34458945901) failed:
- Unit Tests failed.
- Docker Build Validation was skipped.
- The PR was blocked.

Log excerpt ([`evidence/ci-run-failed-log-excerpt.txt`](evidence/ci-run-failed-log-excerpt.txt)):

```
>       assert data["status"] == "wrong"
E       AssertionError: assert 'healthy' == 'wrong'
FAILED tests/test_app.py::test_health - AssertionError: assert 'healthy' == 'wrong'
========================= 1 failed, 14 passed in 0.18s =========================
```

Screenshots: [failed run](evidence/01-ci-failed-run.png), [PR checks failing](evidence/02-pr1-checks-failed.png).

I then restored `assert data["status"] == "healthy"` in `7be3d89` (`fix: correct health endpoint test`). Run [34459093347](https://github.com/MustafaAhsanKhan/student-ml-api/actions/runs/34459093347) passed. Screenshots: [passed run](evidence/03-ci-passed-run.png), [PR checks passing](evidence/04-pr1-checks-passed.png).

PR #1 was merged with a merge commit, so both commits are still visible in `main`'s history.

## Part 7: Branch protection on `main`

I configured this with the GitHub branch protection API. The saved response is in [`evidence/branch-protection.json`](evidence/branch-protection.json).

| Setting | Value | Reason |
|---|---|---|
| Require a pull request before merging | On | Nothing goes straight to `main` |
| Required approving reviews | 0 | This is a single-maintainer repository, and GitHub doesn't allow authors to approve their own PR. Requiring 1 would make merging impossible without bypassing protection. Every PR still gets a written review before merge. In a team I would set this to 1+ and add CODEOWNERS. |
| Dismiss stale approvals when new commits are pushed | On | An approval shouldn't carry over to code added after it was given |
| Require status checks to pass | On: `Unit Tests`, `Docker Build Validation` | A PR can only merge when tests and the Docker build/smoke test pass |
| Require branches to be up to date before merging | On | CI must pass against the latest `main`. This is what forced PR #2 to be updated after #3 merged. |
| Require conversation resolution | On | Unresolved review comments block the merge |
| Enforce for administrators | On | Even the repository owner can't bypass the rules or push directly |
| Allow force pushes | Off | History on `main` can't be rewritten |
| Allow deletions | Off | `main` can't be deleted |
| Require linear history | Off | It would conflict with the merge-commit strategy (Part 8) |

Protection was enabled while PR #1 was open, as soon as the CI check names existed, and before anything was merged. A direct push to `main` is rejected ([`evidence/direct-push-to-main-rejected.txt`](evidence/direct-push-to-main-rejected.txt)):

```
remote: error: GH006: Protected branch update failed for refs/heads/main.
remote: - Changes must be made through a pull request.
remote: - 2 of 2 required status checks are expected.
 ! [remote rejected] HEAD -> main (protected branch hook declined)
```

## Part 8: Merge strategy

**Selected: Merge Commit.** Squash and rebase merging are disabled in the repository settings, so every PR is merged the same way.

Why:
- **Traceability.** Each PR lands on `main` as one commit titled `Merge pull request #N from ...`. The PR number is recorded in Git itself, and that merge commit is exactly what gets tagged: `v1.0.0` → `95c63a7`, `v1.1.0` → `a1aa4d3`.
- **No rewritten commits.** Commits keep the SHAs they had when CI tested them on the branch. Rebase merging creates new SHAs, and squash merging throws the individual commits away.
- **Full history.** The small commits stay visible, including the deliberate failure and its fix. For a one-line-per-PR view I can still use `git log --first-parent main`.

The downside is a busier commit graph. For a large team with lots of "wip" commits, squash merging would probably be the better choice.

## Part 9: Dockerfile

See [`Dockerfile`](../Dockerfile).

| Practice | How it is applied |
|---|---|
| Explicit base image version | `python:3.13.15-slim`: exact patch release, slim variant, never `latest` |
| `WORKDIR` | `/app` |
| Dependency installation | `pip install -r requirements.txt` with pinned versions (`flask==3.1.3`, `gunicorn==26.2.0`) |
| Correct `COPY` ordering | copy `requirements.txt`, run `pip install`, then copy `VERSION app.py`. Code changes don't reinstall dependencies (Part 25). |
| `--no-cache-dir` | pip's download cache isn't saved into the image layer |
| `EXPOSE` | `5000` |
| Appropriate `CMD` | exec-form `gunicorn` bound to `0.0.0.0:5000`: a production WSGI server with 2 workers, logging requests to stdout |
| Also | non-root `appuser`, `PYTHONUNBUFFERED=1` so logs show up immediately in `docker logs`, OCI labels (Part 23), only the files the app needs are copied |

`.dockerignore` excludes:
- `.git` and `.github`
- `__pycache__`, `*.pyc` and `.pytest_cache`
- `.venv` and `.env`
- `tests`, `docs` and Markdown files

That keeps the build context small, and it guarantees a local `.env` with secrets can never be copied into an image.

## Part 10: Local build and run

I built from the `v1.0.0` tag ([build log](evidence/part10-docker-build.txt), [run output](evidence/part10-docker-run.txt)):

```
docker build -t student-ml-api:1.0.0 .
docker run -d --name student-ml-api -p 5001:5000 student-ml-api:1.0.0

$ curl -s http://localhost:5001/health
{"status":"healthy","application":"student-ml-api","version":"1.0.0"}
```

I published the app on **host port 5001** instead of 5000, because port 5000 on my Mac is taken by macOS AirPlay Receiver (failure 5 in Part 26). The container still listens on 5000. With AirPlay Receiver switched off, the assignment's `-p 5000:5000` works the same way.

## Part 11: Container inspection

Output of all five commands is in [`evidence/part11-docker-inspection.txt`](evidence/part11-docker-inspection.txt). The full `docker inspect` JSON is in [`evidence/part11-docker-inspect-full.json`](evidence/part11-docker-inspect-full.json). I wrapped `docker exec -it student-ml-api sh` in `script` so the interactive session could be saved to that file.

| Item | Value | Found with |
|---|---|---|
| Container ID | `d4cca86ee9755c20b92a7f2be18ec726379af74a39e93c0bce0df565149ee8c1` | `docker ps` (short form), `docker inspect` → `.Id` |
| Image ID | `sha256:28a037f6b401de895139cb3c7f085d5ef193c810f3bd09c406e406ada7435c92` | `docker images` (short form), `docker inspect` → `.Image` |
| Exposed port | `5000/tcp`, published on host `0.0.0.0:5001` | `.Config.ExposedPorts`, `.NetworkSettings.Ports` |
| Running command | `gunicorn --bind 0.0.0.0:5000 --workers 2 --access-logfile - app:app` | `.Path` and `.Args` |
| Working directory | `/app` | `.Config.WorkingDir`, `pwd` inside the container |
| User | `appuser` | `.Config.User`, `whoami` inside the container |

**Problem found in the logs.** `docker logs` also showed `[ERROR] Control server error: [Errno 13] Permission denied: '/home/appuser'`.
- **Cause:** gunicorn 26 creates a control socket in the user's home directory, and `appuser` doesn't have one.
- **Fix:** Docker already manages the process, so I disabled the socket with `--no-control-socket` in PR #3.
- **Result:** the `1.1.0` container logs are clean ([`evidence/part20-rollback.txt`](evidence/part20-rollback.txt)).

## Part 12: Container registry

I used **GitHub Container Registry**:
- **Image name:** `ghcr.io/mustafaahsankhan/student-ml-api:<tag>`. GHCR requires lowercase names, so the workflow lowercases the owner with `${GITHUB_REPOSITORY_OWNER,,}`.
- **Login:** the release job uses the built-in `GITHUB_TOKEN` with `packages: write`. No password or personal token is stored in the repo or in secrets.
- **Visibility:** the package is public, so anyone can pull it without logging in.

Screenshots: [package page](evidence/08-ghcr-package.png), [tagged versions](evidence/09-ghcr-tagged-versions.png).

## Part 13: Git tags

I created annotated tags on `main` after each merge:

```
git checkout main
git pull
git tag -a v1.0.0 -m "Release v1.0.0"      # -> 95c63a7, merge commit of PR #1
git push origin v1.0.0

git tag -a v1.1.0 -m "Release v1.1.0"      # -> a1aa4d3, merge commit of PR #2
git push origin v1.1.0
```

Result: Git tag `v1.0.0` → image `student-ml-api:1.0.0`, and Git tag `v1.1.0` → image `student-ml-api:1.1.0`. [Tags screenshot](evidence/11-git-tags.png)

## Parts 14 and 15: Release workflow (`.github/workflows/release.yml`)

Trigger, semantic-version tags only:

```yaml
on:
  push:
    tags:
      - "v*.*.*"
```

```
Version tag (v1.1.0)
 └── Run Tests (job)                  checkout, Python 3.13, install, pytest -v
      └── Build and Push Image (job, needs: Run Tests)
            ├── Checkout code
            ├── Derive version from tag    1.1.0 from v1.1.0, check against VERSION, short SHA, image name
            ├── Log in to GHCR             GITHUB_TOKEN via --password-stdin
            ├── Build Docker image         with OCI label build args
            ├── Apply version tags         1.1.0, latest, a1aa4d3
            ├── Push Docker image          docker push --all-tags
            └── Record image digest        written to the run's job summary
```

The version comes from the tag and is never hard-coded:

```bash
VERSION="${GITHUB_REF_NAME#v}"   # v1.0.0 -> 1.0.0
if [ "$VERSION" != "$(cat VERSION)" ]; then
  echo "::error::Tag $GITHUB_REF_NAME does not match VERSION file ($(cat VERSION))"
  exit 1
fi
```

- **How the version is derived:** `GITHUB_REF_NAME` holds the tag name, and `${...#v}` strips the leading `v`.
- **Why the `VERSION` check exists:** it stops the release if the tag and the code disagree, for example if someone tags `v1.2.0` but forgets to bump `VERSION`. Without it, the image tag and what `/health` reports could end up different.

Runs:
- [v1.0.0](https://github.com/MustafaAhsanKhan/student-ml-api/actions/runs/34459346321) ([screenshot](evidence/05-release-v1.0.0-run.png))
- [v1.1.0](https://github.com/MustafaAhsanKhan/student-ml-api/actions/runs/34460769060) ([screenshot](evidence/07-release-v1.1.0-run.png))

## Part 16: Registry verification

Tags and digests come from the registry API. Full output is in [`evidence/registry-verification.txt`](evidence/registry-verification.txt).

```
student-ml-api
├── 1.0.0      sha256:cdaa960e36bc…
├── 95c63a7    sha256:cdaa960e36bc…   same image as 1.0.0
├── 1.1.0      sha256:a38679a1ad79…
├── a1aa4d3    sha256:a38679a1ad79…   same image as 1.1.0
└── latest     sha256:a38679a1ad79…   points to 1.1.0
```

Recorded image digests:
- `1.0.0`: `sha256:cdaa960e36bce8b0cab3cc815b1d452df89e8caa03aae8d38301c5730aa96013`
- `1.1.0`: `sha256:a38679a1ad792e71e4d6cf74195671b711f82c95ec8d4687768e729829e63ea0`

The same digests appear in the `docker push` output of the release runs: [v1.0.0 log](evidence/release-v1.0.0-log-excerpt.txt), [v1.1.0 log](evidence/release-v1.1.0-log-excerpt.txt).

## Part 17: Artifact reproducibility

I deleted the local image, pulled the release image from GHCR and ran it ([`evidence/part17-reproducibility.txt`](evidence/part17-reproducibility.txt)):

```
$ docker rmi student-ml-api:1.0.0
Untagged: student-ml-api:1.0.0

$ docker pull --platform linux/amd64 ghcr.io/mustafaahsankhan/student-ml-api:1.0.0
Digest: sha256:cdaa960e36bce8b0cab3cc815b1d452df89e8caa03aae8d38301c5730aa96013

$ docker run -d --name student-ml-api --platform linux/amd64 -p 5001:5000 ghcr.io/mustafaahsankhan/student-ml-api:1.0.0
$ curl -s http://localhost:5001/health
{"status":"healthy","application":"student-ml-api","version":"1.0.0"}
```

This really was a different runtime environment:
- **Build machine:** a GitHub-hosted **linux/amd64** runner.
- **Runtime:** my **arm64** Mac under Colima, with no rebuild.
- **Same artefact:** the pulled digest matches the one the release workflow pushed, and the image's `org.opencontainers.image.revision` label is `95c63a7833fd62bba02790876f02d0ea9fa5daf0`.

`--platform linux/amd64` is only needed because the image is single-architecture and my laptop is ARM.

## Parts 18 and 19: Version 1.1.0

Branch `feature/model-metadata`, merged through PR #2:
- `3edea83 feat: add application and model version metadata to /health`
- `798297e test: update health endpoint test for model metadata`
- `2f73e3e chore: bump version to 1.1.0`
- `db5a037 docs: update health response example in README`

The full process, in order:
1. CI ran and passed.
2. CI ran again after the branch was updated with `main` to include #3.
3. I reviewed the PR.
4. I merged it as `a1aa4d3`.
5. I tagged and pushed `v1.1.0`.

Registry after the release:

| Tag | Digest |
|---|---|
| `1.0.0` | `sha256:cdaa960e36bce8b0cab3cc815b1d452df89e8caa03aae8d38301c5730aa96013` |
| `1.1.0` | `sha256:a38679a1ad792e71e4d6cf74195671b711f82c95ec8d4687768e729829e63ea0` |
| `latest` | `sha256:a38679a1ad792e71e4d6cf74195671b711f82c95ec8d4687768e729829e63ea0` |

`latest` has the same digest as `1.1.0`, and `1.0.0` is still available.

## Part 20: Rollback

Scenario: `1.1.0` has a production issue. Without changing any source code or rebuilding anything, I restored `1.0.0` from the registry ([`evidence/part20-rollback.txt`](evidence/part20-rollback.txt)):

```
$ docker run -d --name student-ml-api --platform linux/amd64 -p 5001:5000 ghcr.io/mustafaahsankhan/student-ml-api:1.1.0
$ curl -s http://localhost:5001/health
{"status":"healthy","application":"student-ml-api","application_version":"1.1.0","model_version":"model-1"}

# 1.1.0 is "broken": roll back to the known-good image
$ docker rm -f student-ml-api
$ docker image rm ghcr.io/mustafaahsankhan/student-ml-api:1.0.0     # make sure it really comes from the registry
$ docker pull --platform linux/amd64 ghcr.io/mustafaahsankhan/student-ml-api:1.0.0
$ docker run -d --name student-ml-api --platform linux/amd64 -p 5001:5000 ghcr.io/mustafaahsankhan/student-ml-api:1.0.0
$ curl -s http://localhost:5001/health
{"status":"healthy","application":"student-ml-api","version":"1.0.0"}
```

**Why this is easier than deploying with `git clone`, `pip install` and `python app.py`:**

- **Nothing is built during the rollback.** It's a pull and a restart, which takes seconds. With clone-and-install you have to check out the old tag, rebuild the virtualenv and reinstall everything, right when production is broken.
- **You run the exact bytes that were released.** The `1.0.0` digest is the artefact that was tested and released. Reinstalling from source can resolve different versions of transitive dependencies, run on whatever Python the server has, or fail because PyPI or a package is unavailable.
- **The environment is inside the image.** OS libraries, Python 3.13.15, gunicorn and the start command are all packaged together. The server only needs Docker, not Python, pip or build tools.
- **Production settings come with it.** `python app.py` starts Flask's development server as whatever user runs it. The image always starts gunicorn as a non-root user with the same settings.
- **Old versions are always there.** Every release stays in the registry under its own tag and digest, so rolling back just means choosing an older tag.

The real follow-up would be a fix PR and a `v1.1.1` release. The rollback only buys time to do that.

## Part 21: Traceability for version 1.1.0

| Step in the chain | Value |
|---|---|
| Pull Request | [#2](https://github.com/MustafaAhsanKhan/student-ml-api/pull/2), `feature/model-metadata` → `main` |
| Merge commit SHA | `a1aa4d3679f1464dd39db61bd821d1917b2cb31a` |
| Git tag | `v1.1.0` → `a1aa4d3679f1464dd39db61bd821d1917b2cb31a` |
| Release run | [34460769060](https://github.com/MustafaAhsanKhan/student-ml-api/actions/runs/34460769060) |
| Docker image tag | `ghcr.io/mustafaahsankhan/student-ml-api:1.1.0` (also `:a1aa4d3` and `:latest`) |
| Docker image digest | `sha256:a38679a1ad792e71e4d6cf74195671b711f82c95ec8d4687768e729829e63ea0` |
| OCI revision label inside the image | `a1aa4d3679f1464dd39db61bd821d1917b2cb31a` |

The chain can be followed in both directions:
- **From a running container:** `docker inspect` → revision label → `git show a1aa4d3` → "Merge pull request #2".
- **From the PR:** merge commit → tag → release run → digest.

Evidence: [`evidence/part21-traceability.txt`](evidence/part21-traceability.txt).

## Part 22: CI workflow vs release workflow

| | CI (`ci.yml`) | Release (`release.yml`) |
|---|---|---|
| Runs on | pull requests to `main` | pushed `v*.*.*` tags |
| Responsibilities | test, validate, build-check (with smoke test) | test, build, version, publish |
| Token permissions | `contents: read` | `contents: read`, plus `packages: write` on the publish job only |
| Output | pass/fail status on the PR | images in GHCR, digest in the run summary |

**Why publishing an image from every pull request is usually a bad idea:**

- **Unapproved code.** PR code hasn't been reviewed or merged yet, and some PRs never are. Once an image is in the registry, someone can deploy it by mistake.
- **Security.** PR workflows, especially from forks, run code nobody has checked. Publishing from them would mean giving that code registry write credentials. That's why GitHub gives fork PRs a read-only token and no secrets.
- **Noise and cost.** Every push to every PR would add another image. The registry fills up with artefacts nobody deploys, and it gets harder to tell which images are real releases.
- **Releases should be deliberate.** A release should come from a decision (a version tag on reviewed code in `main`), not happen as a side effect of opening a PR.
- **Nothing is gained.** CI already proves that the Dockerfile builds and the container starts. Pushing the image adds nothing to that check.

## Part 23: OCI image labels

The Dockerfile declares build arguments and turns them into standard OCI labels. The release workflow fills them in:

```bash
docker build \
  --build-arg APP_VERSION="$VERSION" \
  --build-arg GIT_COMMIT="$GIT_SHA" \
  --build-arg BUILD_DATE="$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --build-arg REPOSITORY_URL="$GITHUB_SERVER_URL/$GITHUB_REPOSITORY" \
  -t "$IMAGE:$VERSION" .
```

Verified with `docker inspect` on the image pulled from GHCR ([`evidence/part23-oci-labels.txt`](evidence/part23-oci-labels.txt)):

```json
{
    "org.opencontainers.image.created": "2026-09-10T09:28:09Z",
    "org.opencontainers.image.description": "Prediction API for the MLOps CI/CD exercise",
    "org.opencontainers.image.revision": "a1aa4d3679f1464dd39db61bd821d1917b2cb31a",
    "org.opencontainers.image.source": "https://github.com/MustafaAhsanKhan/student-ml-api",
    "org.opencontainers.image.title": "student-ml-api",
    "org.opencontainers.image.version": "1.1.0"
}
```

The `ARG`/`LABEL` block is placed after `pip install` on purpose. `BUILD_DATE` is different on every build. If the args were declared at the top of the Dockerfile, that changing value would invalidate the cache for the dependency layer on every release.

## Part 24: Commit SHA tag

Every release pushes three tags that point to the same digest: the version, `latest`, and the 7-character commit SHA.

```
ghcr.io/mustafaahsankhan/student-ml-api:1.1.0
ghcr.io/mustafaahsankhan/student-ml-api:latest
ghcr.io/mustafaahsankhan/student-ml-api:a1aa4d3
```

**Why a commit-specific tag is useful:**

- **It maps to exactly one version of the source.** `a1aa4d3` is a Git commit, so `git show a1aa4d3` shows exactly what's inside. `latest` moves on every release, and a version like `1.1.0` is a human label that could in theory be pushed again.
- **People can read it.** A digest is unique but means nothing to a person. A SHA tag can go straight into a deployment file or an incident report and be looked up in Git.
- **It makes debugging and audits easier.** When `…:a1aa4d3` is running somewhere, there's no question about which code it is.
- **It works for more than releases.** It also covers builds that aren't releases, or several builds of the same version.

## Part 25: Docker build cache

I rebuilt the project Dockerfile twice: once after changing only `app.py`, then after changing `requirements.txt`. I then made the same `app.py` change with a `COPY . .` version of the Dockerfile. Step results are from `docker build --progress=plain`; the summary is in [`evidence/part25-build-cache.txt`](evidence/part25-build-cache.txt).

**Project Dockerfile:**

| Step | After changing only `app.py` | After changing `requirements.txt` |
|---|---|---|
| `FROM python:3.13.15-slim` | reused | reused |
| `WORKDIR /app` | CACHED | CACHED |
| `RUN useradd … appuser` | CACHED | CACHED |
| `COPY requirements.txt .` | CACHED | rebuilt (0.1 s) |
| `RUN pip install …` | **CACHED** | **rebuilt (13.4 s)** |
| `COPY VERSION app.py ./` | rebuilt (0.1 s) | rebuilt (0.1 s) |
| Total build time | **about 1 s** | **about 14 s** |

**`COPY . .` before `pip install`, changing only `app.py`:**

| Step | Result |
|---|---|
| `COPY . .` | rebuilt |
| `RUN pip install …` | **rebuilt again (9.2 s)** |
| Total build time | **about 9 s** |

**Why `COPY requirements.txt` → `RUN pip install` → `COPY app.py` is better than `COPY . .` → `RUN pip install`:**

Docker caches every instruction as a layer. When an instruction's input changes, that layer and every layer after it get rebuilt. For `COPY`, the input is the checksum of the copied files.

- **With `COPY . .` first:** any file change (code, tests, README) invalidates that layer, so `pip install` runs again even when no dependency changed.
- **With `requirements.txt` copied on its own:** the expensive `pip install` layer depends only on that file. Code changes, which are far more frequent, only rebuild the tiny final `COPY`.

In a CI/CD pipeline this adds up. Most commits only touch code, so builds stay fast and don't re-download packages from PyPI every time.

## Part 26: Failure analysis

I reproduced five problems: four from the assignment's list, plus one I actually ran into on my machine.

### 1. Failed pytest

- **Symptom:** PR #1 turned red. "Unit Tests" failed, "Docker Build Validation" was skipped, and merging was blocked.
- **Root cause:** `test_health` asserted `data["status"] == "wrong"`, but the API returns `"healthy"`.
- **Evidence:** run [34458945901](https://github.com/MustafaAhsanKhan/student-ml-api/actions/runs/34458945901) shows `AssertionError: assert 'healthy' == 'wrong'`. See the [log excerpt](evidence/ci-run-failed-log-excerpt.txt) and [screenshot](evidence/01-ci-failed-run.png).
- **Correction:** restored the assertion in `7be3d89`, and run [34459093347](https://github.com/MustafaAhsanKhan/student-ml-api/actions/runs/34459093347) passed.

### 2. Missing dependency

- **Symptom:** `docker build` succeeded, but the container stopped right after starting (`Exited (1)`), and `curl` reported `Failed to connect`.
- **Root cause:** `flask` was removed from `requirements.txt`. gunicorn was installed, but its workers couldn't import `app.py` (`ModuleNotFoundError: No module named 'flask'`), so gunicorn shut down with `Worker failed to boot`.
- **Evidence:** `docker ps -a` status and `docker logs` output in [`evidence/failure-missing-dependency.txt`](evidence/failure-missing-dependency.txt).
- **Correction:** restored `flask==3.1.3`, rebuilt, and `/health` returned 200 again. The image built without errors, which is exactly why the CI pipeline also runs a container smoke test instead of stopping at `docker build`.

### 3. Application bound to 127.0.0.1

- **Symptom:** the container was `Up` and the logs said `Listening at: http://127.0.0.1:5000`, but `curl http://localhost:18001/health` from the host returned `curl: (52) Empty reply from server`.
- **Root cause:** inside a container, `127.0.0.1` is the container's own loopback interface. Docker's port mapping forwards traffic to the container's network interface (its bridge IP), where nothing was listening.
- **Evidence:** the same request made from inside the container worked. `docker exec bind-localhost python -c "...urlopen('http://127.0.0.1:5000/health')..."` returned the JSON. See [`evidence/failure-bound-to-localhost.txt`](evidence/failure-bound-to-localhost.txt).
- **Correction:** bind to `0.0.0.0`, which is the Dockerfile's default `CMD`. The logs then showed `Listening at: http://0.0.0.0:5000`, and the request from the host worked.

### 4. Wrong container port

- **Symptom:** `docker run -p 5004:8000 ...` started without errors, but `curl http://localhost:5004/health` returned `Empty reply from server`.
- **Root cause:** the mapping forwarded host port 5004 to container port **8000**, but gunicorn listens on **5000**.
- **Evidence:** `docker port wrong-port` showed `8000/tcp -> 0.0.0.0:5004`, while the logs showed `Listening at: http://0.0.0.0:5000`. See [`evidence/failure-wrong-container-port.txt`](evidence/failure-wrong-container-port.txt).
- **Correction:** `-p 5004:5000`, the port declared with `EXPOSE 5000`. `docker port` then showed `5000/tcp -> 0.0.0.0:5004`, and `/health` responded.

### 5. Host port 5000 already in use (found on my machine)

- **Symptom:** with `-p 5000:5000`, `curl http://localhost:5000/health` returned `HTTP/1.1 403 Forbidden` with an empty body, even though `docker ps` showed `0.0.0.0:5000->5000/tcp`.
- **Root cause:** macOS AirPlay Receiver (the `ControlCenter` process) already listens on `*:5000`, so the request never reached the container.
- **Evidence:** `lsof -iTCP:5000` lists `ControlCe`, and the response header is `Server: AirTunes/950.7.1`. See [`evidence/failure-host-port-5000-conflict.txt`](evidence/failure-host-port-5000-conflict.txt).
- **Correction:** publish on a free host port (`-p 5001:5000`), or turn off AirPlay Receiver in System Settings. The container port stays 5000.

## Core principle

> Git manages the evolution of source code. Pull Requests control how changes enter the main branch. CI verifies those changes. Docker converts approved source code into a reproducible artifact. The container registry stores and distributes versioned artifacts that can later be delivered consistently to staging and production.

How this played out in the project:

- **Git** holds every version of the code, and the tags `v1.0.0` and `v1.1.0` mark the exact commits that were released.
- **Pull requests** are the only way into `main`. Branch protection enforces that (direct pushes are rejected), and every change arrives with a description and a review.
- **CI** runs the tests, then builds and starts the container for every PR. The deliberate failure showed that a broken change simply can't be merged.
- **Docker** packages the approved code together with its Python version, dependencies and start command into one image, identified by its digest.
- **The registry** keeps every version under a tag and a digest. Any environment gets the exact same artefact, which is why the reproducibility test and the rollback to `1.0.0` each needed nothing more than `docker pull` and `docker run`.

## Evidence index

| File | Shows |
|---|---|
| [01-ci-failed-run.png](evidence/01-ci-failed-run.png) | Failed CI run (deliberate test failure) |
| [02-pr1-checks-failed.png](evidence/02-pr1-checks-failed.png) | PR #1 checks failing |
| [03-ci-passed-run.png](evidence/03-ci-passed-run.png) | CI passing after the fix |
| [04-pr1-checks-passed.png](evidence/04-pr1-checks-passed.png) | PR #1 checks passing |
| [05-release-v1.0.0-run.png](evidence/05-release-v1.0.0-run.png) | Release workflow for `v1.0.0` |
| [06-pr1-merged.png](evidence/06-pr1-merged.png) | PR #1 description, review and merge |
| [07-release-v1.1.0-run.png](evidence/07-release-v1.1.0-run.png) | Release workflow for `v1.1.0` |
| [08-ghcr-package.png](evidence/08-ghcr-package.png) | GHCR package page |
| [09-ghcr-tagged-versions.png](evidence/09-ghcr-tagged-versions.png) | Tagged image versions in GHCR |
| [10-pull-requests.png](evidence/10-pull-requests.png) | Pull request list |
| [11-git-tags.png](evidence/11-git-tags.png) | Git tags |
| [12-actions-runs.png](evidence/12-actions-runs.png) | GitHub Actions run history |
| [13-pr2-merged.png](evidence/13-pr2-merged.png) | PR #2 description, review and merge |
| [ci-run-failed.txt](evidence/ci-run-failed.txt), [ci-run-failed-log-excerpt.txt](evidence/ci-run-failed-log-excerpt.txt) | Failed CI run details |
| [ci-run-passed.txt](evidence/ci-run-passed.txt) | Successful CI run |
| [release-v1.0.0-run.txt](evidence/release-v1.0.0-run.txt), [release-v1.0.0-log-excerpt.txt](evidence/release-v1.0.0-log-excerpt.txt) | `v1.0.0` release run and pushed digests |
| [release-v1.1.0-run.txt](evidence/release-v1.1.0-run.txt), [release-v1.1.0-log-excerpt.txt](evidence/release-v1.1.0-log-excerpt.txt) | `v1.1.0` release run and pushed digests |
| [branch-protection.json](evidence/branch-protection.json) | Branch protection settings for `main` |
| [direct-push-to-main-rejected.txt](evidence/direct-push-to-main-rejected.txt) | Direct push to `main` rejected |
| [git-history.txt](evidence/git-history.txt) | Commit graph of `main` |
| [part10-docker-build.txt](evidence/part10-docker-build.txt), [part10-docker-run.txt](evidence/part10-docker-run.txt) | Local build and run |
| [part11-docker-inspection.txt](evidence/part11-docker-inspection.txt), [part11-docker-inspect-full.json](evidence/part11-docker-inspect-full.json) | `docker images`, `ps`, `logs`, `inspect`, `exec` |
| [part17-reproducibility.txt](evidence/part17-reproducibility.txt) | Delete local image, pull from GHCR, run |
| [registry-verification.txt](evidence/registry-verification.txt) | Tags and digests in GHCR |
| [part20-rollback.txt](evidence/part20-rollback.txt) | Rollback from 1.1.0 to 1.0.0 |
| [part21-traceability.txt](evidence/part21-traceability.txt) | PR → commit → tag → image → digest |
| [part23-oci-labels.txt](evidence/part23-oci-labels.txt) | OCI labels on the release image |
| [part25-build-cache.txt](evidence/part25-build-cache.txt) | Build cache comparison |
| [failure-*.txt](evidence/) | Failure analysis reproductions |
