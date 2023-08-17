sudo cp director.service /etc/systemd/system/director.service

# Reload Systemd and Start the Service:
sudo systemctl daemon-reload
sudo systemctl start director.service

# Enable Automatic Start on Boot:
sudo systemctl enable director.service
sudo systemctl status director.service

sudo systemctl daemon-reload
sudo systemctl restart director.service


# Monitor and Restart with systemd-monitors:
# sudo apt-get install systemd-monitors
# sudo systemctl monitors add director.service


