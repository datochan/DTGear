# 每天
# /etc/crontab
# 05 15   * * *   datochan cd /opt/DTGear/ && ./update_all.sh > "./logs/$(date +"\%Y-\%m-\%d").log" 2>&1

python3 ./cli.py update basics
python3 ./cli.py update days
python3 ./cli.py update bond

python3 ./cli.py update report
python3 ./cli.py update rt

python3 ./cli.py convert report

python3 ./cli.py convert fixed
python3 ./cli.py convert mv
python3 ./cli.py convert pe-pb-roe

python3 ./cli.py calc cybz
python3 ./cli.py calc hs300
python3 ./cli.py calc sz50
python3 ./cli.py calc szhl
python3 ./cli.py calc zxbz
python3 ./cli.py calc zz500
python3 ./cli.py calc zzhl

date "+%Y%m%d" > ./last_update
