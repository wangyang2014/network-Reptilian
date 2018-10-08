#!/bin/sh
#crontab每天早上4点kill掉生产者进程,每天早上5点启动生产者进程
#0 4 * * * sh crontabProducerMain.sh stop
#0 5 * * * sh crontabProducerMain.sh start
if [ $# -lt 1 ]; then
	echo "args: start or stop"
else
	case $1 in
		"start"|"START")

		    #启动生产者单进程第一路
		    echo "start simpleProducerChildUrlMain＿1.py"
		    cd $(pwd)
			cd ../
			if [ ! -f "/webCrawler" ] && [ -f "ProducerChildUrlMain.py" ];
			then
                nohup python3 -u simpleProducerChildUrlMain.py > $(pwd)/log/producer/"simpleProducerChildUrlMain＿1.log" 2>&1 &
                echo "python3 simpleProducerChildUrlMain＿1.py is running and log is saved in simpleProducerChildUrlMain＿1.log"
                sleep 1
			fi

			sleep 1
			;;
		"stop"|"STOP")
#			echo "killlall python3 ProducerChildUrlMain.py"
#			killall python3 ProducerChildUrlMain.py >/dev/null 2>&1

            #根据进程名杀死进程 simpleProducerChildUrlMain
            PROCESS_PRODUCER=`ps -ef|grep simpleProducerChildUrlMain|grep -v grep|grep -v PPID|awk '{ print $2}'`
            for i in $PROCESS_PRODUCER
            do
                echo "Kill the $1 PROCESS_PRODUCER [ $i ]"
                kill -9 $i
            done
			;;
		*)
			echo "args: start or stop";;
	esac
fi
exit 0
