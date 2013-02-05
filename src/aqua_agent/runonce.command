#!/bin/bash
for v in /Volumes/*;do
	if [ -e "$v/QMSClient" ];then
		script_file=$v/callpy.command
		echo "### Script Action ###" > $script_file
		echo "for i in 10 9 8 7 6 5 4 3 2 1" >> $script_file
		echo "do" >> $script_file
		echo '	echo "count backwards... $i"' >> $script_file
		echo "	sleep 1" >> $script_file
		echo "done" >> $script_file
		echo "echo 'Starting QMSClient ...'" >> $script_file
		echo "cd ${v}/QMSClient" >> $script_file
		echo "python2.5 ./restAdm.py" >> $script_file
		chmod +x "$script_file"
		osascript -e 'tell application "System Events" to delete login item "runonce.command"';
		osascript -e "tell application \"System Events\" to make new login item with properties { path: \"$script_file\", hidden:false } at end";
		$script_file;
		break;
	fi;
done
