#!/bin/sh
#批量运行,销毁爬虫脚本(文件启动时要记得删除log日志)
if [ $# -lt 1 ]; then
	echo "args: start or stop"
else
	case $1 in
		"start"|"START")
		    echo "start ProducerChildUrlMain.py"
			#killall  python3 ProducerChildUrlMain.py >/dev/null 2>&1
			cd ../
#			export LD_LIBRARY_PATH=$(pwd)
#            echo $(pwd)
			if [ ! -f "/webCrawler" ] && [ -f "ProducerChildUrlMain.py" ];
			then
			    #修改进程数
                for i in $(seq 1 30)
			    do
			        nohup python3 -u ProducerChildUrlMain.py > $(pwd)/log/producer/"producerUrlMain_"$i.log 2>&1 &
			        echo "python3 ProducerChildUrlMain.py No."$i" is running and log is saved in producerUrlMain_"$i".log"
			        sleep 1
			    done
			fi
			echo "all work suceess and shell exit right now"
			sleep 1
			;;
		"stop"|"STOP")
			echo "killlall python3 ProducerChildUrlMain.py"
			killall python3 ProducerChildUrlMain.py >/dev/null 2>&1
			;;
		*)
			echo "args: start or stop";;
	esac
fi
exit 0
