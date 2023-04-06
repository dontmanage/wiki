#!/bin/bash
set -e
cd ~ || exit

echo "Setting Up Bench..."

pip install dontmanage-bench
bench -v init dontmanage-bench --skip-assets --python "$(which python)"
cd ./dontmanage-bench || exit

bench -v setup requirements

echo "Setting Up Wiki App..."
bench get-app wiki "${GITHUB_WORKSPACE}"

echo "Setting Up Sites & Database..."

mkdir ~/dontmanage-bench/sites/wiki.test
cp "${GITHUB_WORKSPACE}/.github/helper/site_config.json" ~/dontmanage-bench/sites/wiki.test/site_config.json

mariadb --host 127.0.0.1 --port 3306 -u root -p123 -e "SET GLOBAL character_set_server = 'utf8mb4'";
mariadb --host 127.0.0.1 --port 3306 -u root -p123 -e "SET GLOBAL collation_server = 'utf8mb4_unicode_ci'";

mariadb --host 127.0.0.1 --port 3306 -u root -p123 -e "CREATE DATABASE test_wiki";
mariadb --host 127.0.0.1 --port 3306 -u root -p123 -e "CREATE USER 'test_wiki'@'localhost' IDENTIFIED BY 'test_wiki'";
mariadb --host 127.0.0.1 --port 3306 -u root -p123 -e "GRANT ALL PRIVILEGES ON \`test_wiki\`.* TO 'test_wiki'@'localhost'";

mariadb --host 127.0.0.1 --port 3306 -u root -p123 -e "FLUSH PRIVILEGES";


echo "Setting Up Procfile..."

sed -i 's/^watch:/# watch:/g' Procfile
sed -i 's/^schedule:/# schedule:/g' Procfile

echo "Starting Bench..."

bench start &> bench_start.log &

CI=Yes bench build &
build_pid=$!

bench --site wiki.test reinstall --yes
bench --site wiki.test install-app wiki

# wait till assets are built succesfully
wait $build_pid
