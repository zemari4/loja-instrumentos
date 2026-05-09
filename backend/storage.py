from whitenoise.storage import CompressedManifestStaticFilesStorage


class ManifestStorage(CompressedManifestStaticFilesStorage):
    manifest_strict = False
