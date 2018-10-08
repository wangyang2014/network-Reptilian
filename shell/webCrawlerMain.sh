#!/bin/sh
#批量运行,销毁爬虫脚本(文件启动时要记得删除log日志)
if [ $# -lt 1 ]; then
	echo "args: start or stop"
else
	case $1 in
		"start"|"START")
		    echo "start webCrawlerMain.py"
			killall python3 webCrawlerMain.py >/dev/null 2>&1
			cd ../
#			export LD_LIBRARY_PATH=$(pwd)
#            echo $(pwd)
			if [ ! -f "/webCrawler" ] && [ -f "webCrawlerMain.py" ];
			then
			    #修改进程数
                for i in $(seq 1 50)
			    do
			        nohup python3 -u webCrawlerMain.py > $(pwd)/log/webCrawler/"webCrawlerMain_"$i.log 2>&1 &
			        echo "python3 webCrawlerMain.py No."$i" is running and log is saved in webCrawlerMain_"$i".log"
			        sleep 1
			    done
			fi
			echo "all work suceess and shell exit right now"
			sleep 1
			;;
		"stop"|"STOP")
			echo "killlall python3 webCrawlerMain.py"
			killall python3 webCrawlerMain.py >/dev/null 2>&1
			;;
		*)
			echo "args: start or stop";;
	esac
fi
exit 0
