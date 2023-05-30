# Set up the Pigweed repo. We only need the latest commit.
git clone --depth 1 https://pigweed.googlesource.com/pigweed/pigweed
cd pigweed
# Build the docs.
source bootstrap.sh
gn gen out
ninja -C out docs
deactivate
cd -
