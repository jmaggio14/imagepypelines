# this file prints something to standard out every 5 minutes to prevent travis
# from automatically ending the build. It can be stopped by killing it's PID
while [ 1 ]; do
    sleep 5m
    echo "(IP TRAVIS) this message is printed to prevent the travis build from auto timing out"
done
