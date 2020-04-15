# 每天
# /etc/crontab
# 05 15   * * *   datochan cd /opt/DTGear/ && ./update_all.sh > "./logs/$(date +"\%Y-\%m-\%d").log" 2>&1
source /home/datochan/Documents/DTGear/venv/bin/activate

/home/datochan/Documents/DTGear/venv/bin/python ./cli.py update basics
/home/datochan/Documents/DTGear/venv/bin/python ./cli.py update days
/home/datochan/Documents/DTGear/venv/bin/python ./cli.py update bond

/home/datochan/Documents/DTGear/venv/bin/python ./cli.py update report
/home/datochan/Documents/DTGear/venv/bin/python ./cli.py update rt

/home/datochan/Documents/DTGear/venv/bin/python ./cli.py convert report

/home/datochan/Documents/DTGear/venv/bin/python ./cli.py convert fixed
/home/datochan/Documents/DTGear/venv/bin/python ./cli.py convert mv
/home/datochan/Documents/DTGear/venv/bin/python ./cli.py convert pe-pb-roe

/home/datochan/Documents/DTGear/venv/bin/python ./cli.py calc a
/home/datochan/Documents/DTGear/venv/bin/python ./cli.py calc indexes

date "+%Y%m%d" > ./last_update

deactivate
