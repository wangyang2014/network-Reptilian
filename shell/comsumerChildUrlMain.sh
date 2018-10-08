#!/bin/sh
#批量运行,销毁爬虫脚本(文件启动时要记得删除log日志)python3 ComsumerChildUrlMain.py
if [ $# -lt 1 ]; then
	echo "args: start or stop"
else
	case $1 in
		"start"|"START")
		    echo "start ComsumerChildUrlMain.py"
			#killall  python3 ComsumerChildUrlMain.py >/dev/null 2>&1
			cd ../
#			export LD_LIBRARY_PATH=$(pwd)
#            echo $(pwd)
			if [ ! -f "/webCrawler" ] && [ -f "ComsumerChildUrlMain.py" ];
			then
			    #修改进程数
                for i in $(seq 1 40)
			    do
			        nohup python3 -u ComsumerChildUrlMain.py > $(pwd)/log/comsumer/"ComsumerChildUrlMain_"$i.log 2>&1 &
			        echo "python3 ComsumerChildUrlMain.py No."$i" is running and log is saved in ComsumerChildUrlMain_"$i".log"
			        sleep 1
			    done
			fi
			echo "all work suceess and shell exit right now"
			sleep 1
			;;
		"stop"|"STOP")
#			echo "killlall python3 ComsumerChildUrlMain.py"
#			killall python3 ComsumerChildUrlMain.py >/dev/null 2>&1

            #根据进程名杀死进程 simpleProducerChildUrlMain
            COMSUMER_PRODUCER=`ps -ef|grep ComsumerChildUrlMain|grep -v grep|grep -v PPID|awk '{ print $2}'`
            for i in $COMSUMER_PRODUCER
            do
                echo "Kill the $1 COMSUMER_PRODUCER [ $i ]"
                kill -9 $i
            done
			;;
		*)
			echo "args: start or stop";;
	esac
fi
exit 0
