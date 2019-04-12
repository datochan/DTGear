# 每天
# /etc/crontab
# 25 15   * * *   datochan cd /home/datochan/Documents/DTGear/ && ./update_all.sh > "./logs/$(date +"\%Y-\%m-\%d").log" 2>&1

source /home/datochan/Documents/DTGear/venv/bin/activate

python3 ./cli.py update basics
python3 ./cli.py update days
python3 ./cli.py update bond

python3 ./cli.py update report
python3 ./cli.py update rt

python3 ./cli.py convert report

python3 ./cli.py convert fixed
python3 ./cli.py convert mv
python3 ./cli.py convert pe-pb-roe

python3 ./cli.py calc a
python3 ./cli.py calc indexes

date "+%Y%m%d" > ./last_update
