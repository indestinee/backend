find . | grep -E "(/__pycache__$|/\.DS_Store$)" | xargs rm -rf
rsync -avz --exclude .idea --exclude accompany --exclude .git --exclude .github . openwrt:~/server_backend/
