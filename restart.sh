echo "Restarting pyloop..."
sudo systemctl restart pyloop
echo ""
echo "Restart done! Waiting 3 seconds..."
sleep 3
echo ""
echo "Pyloop status: (press Q to exit)"
echo ""
sudo systemctl status pyloop
