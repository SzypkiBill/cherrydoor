SUDO=''
if (( $EUID != 0 )); then
    SUDO='sudo';
fi;
if hash mongo &>/dev/null; then
    echo -e "\e[92mMongoDB jest zainstalowane\e[39m";
else
    echo -e "\e[93mMongoDB niezainstalowane. Instalowanie...\e[39m"
    wget -qO - https://www.mongodb.org/static/pgp/server-4.2.asc | $SUDO apt-key add - &&
    echo "deb [ arch=amd64 ] https://repo.mongodb.org/apt/ubuntu bionic/mongodb-org/4.2 multiverse" | $SUDO tee /etc/apt/sources.list.d/mongodb-org-4.2.list &&
    $SUDO apt-get update &&
    $SUDO apt-get install -y mongodb-org
    $SUDO service mongod start;
fi;
if hash pip3 &>/dev/null; then
    echo -e "\e[92mpip3 jest zainstalowane, instalowanie wymaganych modułów\e[39m";
else
    echo -e "\e[93mpip3 niezainstalowane. Instalowanie...\e[39m" &&
    $SUDO apt-get install python3-pip;
fi;
pip3 install -r requirements.txt