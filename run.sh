#!/bin/bash

_load_scraper_vars() {
    echo -e "${purple}Initializing...${nc}"
    echo
    dir=$(pwd)
    output_dir=$dir/extracted_files
    script=$dir/main.py
    venv_dir=$dir/venv
    links_file=$dir/audio_links.txt
    reqs_file=$dir/requirements.txt
}

_setup_pyenv() {
    echo -e "${purple}Checking Dependencies...${nc}"
    echo
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
                echo -e "${yellow}$package $version${purple} is already installed.${nc}"
            else
                echo -e "${purple}Updating ${yellow}$package ${purple}from ${red}$installed_version ${purple}to ${red}$version${nc}"
                pip install -U "$requirement"
            fi
        else
            echo -e "${purple}Installing:${yellow} $package $version${nc}"
            pip install "$requirement"
        fi
    done < requirements.txt
}
_scrape_links() {
    if [[ -f $links_file ]]; then
        rm -f $links_file
    fi
    echo -e "${purple}Deploying Webscraper${nc}"
    python3 main.py

    echo -e "${purple}Extracting URLs...${nc}"
    while [ ! -f "$links_file" ]; do
        sleep 1
    done
    echo -e "${purple}Extraction Complete${nc}"
    echo
}

_download_links() {
    echo -e "${purple}Scraping audio using extracted URLs...${nc}"
    counter=1
    while IFS= read -r url; do
        wget "$url" -O "$output_dir/track_$counter.mp3"
        ((counter++))
    done < $links_file

    sleep 3
    rm -rf $links_file
    echo -e "${purple}Scraping Complete${nc}"
    echo
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
    echo
    echo -e "${green}All Operations Have Completed Successfully${nc}"
    echo
}

_execute