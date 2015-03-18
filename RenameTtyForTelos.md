# Add udev rule to avoid confusion between the Telos mote and other tty devices #

```
sudo tee -a /etc/udev/rules.d/10-local.rules <<'EOF'
SUBSYSTEMS=="usb", KERNEL=="ttyUSB*", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001",  SYMLINK+="ttyTelos"
EOF
```