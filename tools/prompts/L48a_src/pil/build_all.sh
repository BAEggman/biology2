set -e
cd /tmp/L48a
Z=/tmp/b2/tools/prompts/zone3.py
python3 $Z crop base.png z a3 800 100 1200 811 >/dev/null
python3 $Z paste base.png z a3 z/rem_a3.png w3.png "900,290,1150,805" | tail -1
python3 c3.py
python3 $Z crop base.png z a1 60 640 480 955 >/dev/null
python3 $Z paste w3c.png z a1 z/rem_a1.png w1.png "175,690,445,955" | tail -1
python3 c1.py
python3 $Z crop base.png z a2 470 480 830 960 >/dev/null
python3 $Z paste w1c.png z a2 z/rem_a2.png w2.png "480,500,825,955" 28 --fit="560,560,820,940" | tail -1
python3 c2.py >/dev/null
python3 $Z crop base.png z a4 1185 415 1545 865 >/dev/null
python3 $Z paste w2c.png z a4 z/rem_a4.png w4.png "1200,430,1530,860" 28 --fit="1250,480,1480,840" | tail -1
python3 c4.py
python3 c10.py
cp w10.png final.png
