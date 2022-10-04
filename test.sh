apt-get -y update
apt-get -y install python3 python3-pip tmux ffmpeg
pip3 install -r requirements.txt
pip install pymongo[srv]
timedatectl set-timezone Asia/Bangkok