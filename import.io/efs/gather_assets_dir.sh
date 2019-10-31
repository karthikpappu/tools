ASSETS_DIR=/efs/assets

ASSETS_FILE="assets_`date +%Y%m%d-%H%M`.dirs"
echo "Saving to $ASSETS_FILE ..."
find $ASSETS_DIR -maxdepth 1 -mtime +30 > $ASSETS_FILE

