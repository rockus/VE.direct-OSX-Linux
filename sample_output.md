VE.direct-OSX-Linux$ sudo ./mpptemoncms/mpptemoncms -c mppt_config.conf -d /dev/ttyUSB3

  MPPT EMONCMS v2.02 (c)2015,2016 Oliver Gerler (rockus@rockus.at)

  date : Sun Aug 13 19:38:05 2023

charger:
  type: *UNKNOWN*
  fw  : v1.59
  ser : HQ2146CMFMK

panel:
  vpv : 13.710V
 [ipv :  0.000A]
  ppv :   0W
battery:
  v   : 12.940V
  i   : -0.830A
 [p   : -10.740W]
load:
 [v   : 12.940V (same voltage as battery)]
  il  :  0.800A
 [pl  : 10.352W
]charger status:
  cs  : Off
  err : No error
  load: On
  yield total         :   0.06kWh
  yield today         :   0.00kWh [  0.00Ah @ 13V nom.]
  yield yesterday     :   0.00kWh [  0.00Ah @ 13V nom.]
  max. power today    :    1W
  max. power yesterday:    0W
  hsds: 26

Note: values in square brackets [] are calculated by this tool,
      not in the charger.

256
GET /input/post.json?node="MySolarController"&json={vpv:13.710,ppv:0,v:12.940,i:-0.830,yt:0.06,yd:0.00,yy:0.00,mpd:1,mpy:0,cs:0}&apikey=58b2624934cbfbd3388b88b4e5253256 HTTP/1.1
Host: emoncms.org
User-Agent: MPPT EMONCMS v2.02
Connection: keep-alive


send: 256
Closing down.
