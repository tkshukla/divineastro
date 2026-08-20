set -e
if [ ! -f /swapfile ]; then
  sudo fallocate -l 4G /swapfile && sudo chmod 600 /swapfile && sudo mkswap /swapfile >/dev/null && sudo swapon /swapfile
  echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab > /dev/null
  echo 'vm.swappiness=10' | sudo tee /etc/sysctl.d/99-swap.conf > /dev/null
  sudo sysctl -p /etc/sysctl.d/99-swap.conf > /dev/null
fi
sudo apt-get update -qq
sudo apt-get install -y -qq ca-certificates curl gnupg >/dev/null
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor --yes -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $(. /etc/os-release && echo $VERSION_CODENAME) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update -qq
sudo apt-get install -y -qq docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin >/dev/null
sudo usermod -aG docker $USER
sudo mkdir -p /opt/divineastro && sudo chown -R $USER /opt/divineastro
free -h | head -3
docker --version
echo "VM READY"
