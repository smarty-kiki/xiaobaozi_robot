#!/bin/bash

ROOT_DIR="$(cd "$(dirname $0)" && pwd)"

apt-get install -y pulseaudio python3-pyaudio swig libatlas-base-dev

card=`arecord -L | grep sysdefault:CARD= | cut -d '=' -f 2`
case $card in
    seeed2micvoicec)
	ln -fs $ROOT_DIR/led/2mics_hat $ROOT_DIR/pixels
	;;
    seeed4micvoicec)
	ln -fs $ROOT_DIR/led/4mics_hat $ROOT_DIR/pixels
	;;
    *)
	echo "未识别的声卡"
esac
