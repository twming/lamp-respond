### Raspberry Pi Setup 
1. Download "Raspberry Pi Imager" and install it.
```
https://www.raspberrypi.com/software/
```
<img src="https://github.com/twming/ros2_master_tutorial/blob/main/img/raspberrypi.png" alt="Raspberry Pi" width="600">

2. Use the SD-Card provided, install Ubuntu 22.04 server on the card using "Raspberry Pi Imager"

> [!IMPORTANT] 
> - Customize Setting to setup the wifi

3. Connect up Raspberry Pi to TV monitor, keyboard, mouse. Boot up the into Ubuntu, to obtain the IP address
```
ip addr
```

4. Enable password login through ssh, edit the /etc/ssh/sshd_config.d/50-cloud-init.conf
```
sudo nano /etc/ssh/sshd_config.d/50-cloud-init.conf
```
Change the PasswordAuthentication from 'no' to 'yes'

5. Edit the /etc/apt/apt.conf.d/20auto-upgrades
```
sudo nano /etc/apt/apt.conf.d/20auto-upgrades
```
Disable Auto Update (prevent long wait for application update), to disable it, set the value '1' to '0'

6. Disable Network Sleep, Suspend, Hibernate
```
sudo systemctl mask systemd-networkd-wait-online.service
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
```
7. Reboot Raspberry Pi
```
sudo reboot
```

(Optional) Edit /etc/netplan/50-cloud-init.yaml
```
sudo nano /etc/netplan/50-cloud-init.yaml
```
Configure Wifi, get the password "wpa_passphrase ros_public 0123456789"
```
network:
    ethernets:
        eth0:
            dhcp4: true
            optional: true
    version: 2
    wifis:
        renderer: networkd
        wlan0:
            access-points:
                ros_public:
                    password: 9fea575b6a0d4668c666a4b111d7784ca062496a4570715e0d5120714b9b3f90
                SSID:
                    password: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
            dhcp4: true
            optional: true
```
### SenseHat Package Installation 
1. Update the ubuntu and install sense-hat
```
sudo apt update
sudo apt install sense-hat
```
2. Setup the Raspberry Pi firmware overlay, go to below file and add the two lines at the file bottom
```
sudo nano /boot/firmware/config.txt
```
add below 2 lines:
```
dtoverlay=rpi-sense
dtparam=i2c_arm=on
```
3. Give user the right permission to access sense-hat
```
sudo usermod -a -G input $USER
```
