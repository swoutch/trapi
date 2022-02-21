import os
import time

import pulumi
from pulumi_gcp import cloudfunctions, storage


# File path to where the Cloud Function's source code is located.
PATH_TO_SOURCE_CODE = "../src"

# We will store the source code to the Cloud Function in a Google Cloud Storage bucket.
bucket = storage.Bucket("source-code", location="US-EAST1")

# The Cloud Function source code itself needs to be zipped up into an
# archive, which we create using the pulumi.AssetArchive primitive.
assets = {}
for file in os.listdir(PATH_TO_SOURCE_CODE):
    location = os.path.join(PATH_TO_SOURCE_CODE, file)
    asset = pulumi.FileAsset(path=location)
    assets[file] = asset
archive = pulumi.AssetArchive(assets=assets)

# Create the single Cloud Storage object, which contains all of the function's
# source code. ("main.py" and "requirements.txt".)
# The timestamp is incorporated in the name because if the name does not
# change, the function does not detect change of the source code
source_archive_object = storage.BucketObject(
    "eta_demo_object",
    name="main.py-%f" % time.time(), #TODO: iso datetime instead of unix ts, or maybe hash
    bucket=bucket.name,
    source=archive)

# Create the Cloud Function, deploying the source we just uploaded to Google
# Cloud Storage.
#TODO: make public
fxn = cloudfunctions.Function(
    "eta_demo_function",
    entry_point="tell_time",
    region="us-central1", #TODO: mettre une region gratuite
    runtime="python37",
    source_archive_bucket=bucket.name,
    source_archive_object=source_archive_object.name,
    trigger_http=True)