# Get the exact pilot bundle

The pinned pilot packages are available as build artifacts from the successful
[native Linux qualification run](https://github.com/B3Cognition/prosaic-castle/actions/runs/40221007879).
They are not PyPI releases. All three wheel hashes match on AMD64 and ARM64;
the manifest selects the AMD64 job's complete wheel/sdist bundle. Native
dependencies are installed separately for the machine running the worker.

With GitHub CLI authenticated, run from this repository. Choose two new absolute
directories outside Git for the download and the flattened bundle:

```sh
set -eu
export DOWNLOAD=/absolute/new/pilot-download
export BUNDLE=/absolute/new/pilot-bundle
mkdir "$DOWNLOAD" "$BUNDLE"
gh run download 40221007879 --repo B3Cognition/prosaic-castle \
  --name installed-artifacts-amd64 --dir "$DOWNLOAD"
for component in worker adapter sue; do
  mkdir "$BUNDLE/$component"
  cp "$DOWNLOAD/$component/direct/"* "$BUNDLE/$component/"
done
python3.12 scripts/verify_pilot_bundle.py "$BUNDLE"
```

The verifier requires all six exact wheel/sdist files before installation.
Continue with [install and smoke](../../PROSAIC_CASTLE.md#repository-and-unpublished-pilot),
then the [pilot protocol](README.md). SUE need not be installed for memory.

GitHub retains these artifacts for 90 days. Keep an authorized local copy with
its manifest. If the download has expired, ask the maintainer for the retained
bundle or qualify a new build; do not install a random same-version package or
replace manifest hashes merely to bypass a mismatch. Other CI runs carry their
own qualification.json records and are not automatically this pinned bundle.

The accepted build source is e87fb9dc40ac9ff1d2c4628737b431edad3b46f9. Later
documentation/manifest commits do not retroactively change those artifacts.
The SUE byte identity changed only through verified formatting corrections;
older saved reviews continue to require their original pinned engine wheel.
