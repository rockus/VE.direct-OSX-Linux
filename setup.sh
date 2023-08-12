#!/bin/bash

# Install required packages
sudo apt-get update
sudo apt-get install -y libconfig9 libconfig-dev build-essential

# Directory to store the repository
repo_dir="mppt-ve.direct"

# Check if the repository directory exists
if [ -d "$repo_dir" ]; then
    # Repository exists, pull updates
    echo "Repository already exists. Pulling updates..."
    cd "$repo_dir"
    git pull
else
    # Repository does not exist, clone it
    echo "Repository does not exist. Cloning repository..."
    git clone https://github.com/photovoltaic/mppt-ve.direct.git "$repo_dir"
    cd "$repo_dir"
fi

# Compile mpptdump
cd VE.direct-OSX-Linux/mpptdump
make

# Compile mpptemoncms
cd ../mpptemoncms
make

# Inform the user about the compiled binaries
echo "Compilation finished."
echo "The compiled binaries are available in the 'mpptdump' and 'mpptemoncms' directories."
echo "You can use these binaries to interact with your Victron MPPT solar charge controller."

# Optionally, you can copy the binaries to a desired location
# For example:
# sudo cp mpptdump /usr/local/bin/
# sudo cp mpptemoncms /usr/local/bin/
