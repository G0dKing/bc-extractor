#!/bin/bash

_load_scraper_vars() {
    echo "Initializing..."
    root_dir=/mnt/g/.dev/projects/active/coldCaller
    dir=$root_dir/webscraper
    output_dir=$dir/extracted_files
    script=$dir/main.py
    venv_dir=$dir/venv
    links_file=$dir/audio_links.txt
    reqs_file=$dir/requirements.txt
}

_setup_pyenv() {
    echo "Checking Dependencies..."
    source venv/bin/activate

    # Read requirements file and check each dependency
    while IFS= read -r requirement || [[ -n "$requirement" ]]; do
        # Extract package name and version
        package=$(echo "$requirement" | cut -d'=' -f1)
        version=$(echo "$requirement" | cut -d'=' -f3)

        # Check if package is installed and its version
        if pip freeze | grep -i "^$package==" > /dev/null; then
            installed_version=$(pip freeze | grep -i "^$package==" | cut -d'=' -f3)
            if [ "$installed_version" = "$version" ]; then
                echo "$package $version is already installed."
            else
                echo "Updating $package from $installed_version to $version"
                pip install -U "$requirement"
            fi
        else
            echo "Installing $package $version"
            pip install "$requirement"
        fi
    done < requirements.txt
}
_scrape_links() {
    if [[ -f $links_file ]]; then
        rm -f $links_file
    fi
    echo "Deploying Webscraper"
    python3 main.py

    echo "Extracting..."
    while [ ! -f "$links_file" ]; do
        sleep 1
    done
    echo "Metadata extraction complete."
    echo
}

_download_links() {
    echo "Scraping files using extracted metadata..."
    counter=1
    while IFS= read -r url; do
        wget "$url" -O "$output_dir/track_$counter.mp3"
        ((counter++))
    done < $links_file

    sleep 3
    rm -rf $links_file
}

_execute() {
    clear
    _load_scraper_vars
    cd $dir
    _setup_pyenv
    _scrape_links
    _download_links
    sleep 3
    clear
    echo "Operation Complete."
    echo
}

_execute