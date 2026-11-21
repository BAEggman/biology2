#!/bin/bash
# proc2.sh <Downloads 의 ZIP 이름> <tag> — (기기 Linux VM 에서) ZIP 을 b2audio/raw/<tag>/ 로 옮기고 WAV 마다 MP3 · sha256 · 길이 · 끝 음량 · 긴 침묵을 적는다.
D=$HOME/mnt/Downloads; R=$D/b2audio/raw; Z="$1"; T=$2; H=${HASHES:-$D/b2audio/hashes_20261121.txt}
mkdir -p $R/$T && mv "$D/$Z" $R/$T/ && cd $R/$T && unzip -o -q "$Z" -d x
for f in $(find x -name '*.wav' | sort); do b=$(basename $f .wav); L=$(echo $b|cut -d_ -f2); sid=$(echo $b|cut -d_ -f3); v=$(echo $b|cut -d_ -f4)
 mkdir -p $R/$L/x $R/$L/mp3; cp -n $f $R/$L/x/
 ffmpeg -hide_banner -loglevel error -n -i $f -ac 1 -ar 24000 -b:a 96k -map_metadata -1 $R/$L/mp3/${L}_${sid}_${v}.mp3
 tail=$(python3 -c "
import wave,struct,math
w=wave.open('$f');r=w.getframerate();N=w.getnframes();w.setpos(max(0,N-r//10));d=w.readframes(r//10);a=struct.unpack('<%dh'%(len(d)//2),d);print(round(20*math.log10(max(1,max(abs(x) for x in a))/32768)))")
 echo "${L}_${sid}_${v} $(shasum -a 256 $f|cut -d' ' -f1) $(shasum -a 256 $R/$L/mp3/${L}_${sid}_${v}.mp3|cut -d' ' -f1) $(ffprobe -v error -show_entries format=duration -of csv=p=0 $R/$L/mp3/${L}_${sid}_${v}.mp3) $(ffprobe -v error -show_entries stream=sample_rate,channels -of csv=p=0 $f) last100=$tail longsil=$(ffmpeg -hide_banner -i $f -af silencedetect=n=-40dB:d=1.2 -f null - 2>&1 | grep -c silence_start)" | tee -a $H
 echo "$R/$L/mp3/${L}_${sid}_${v}.mp3" >> list.txt
done
