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
    pip3 install -r requirements.txt
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