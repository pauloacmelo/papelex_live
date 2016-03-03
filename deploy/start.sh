cd /home/suporte/app/
# Run If closed process rethinkdb &
kill -9 `cat run.pid`
nohup node index.js production > /dev/server.log 2>&1 & echo $! > run.pid
kill -9 `cat agent.pid`
python3 agent.py > /dev/agent.log 2>&1 & echo $! > agent.pid