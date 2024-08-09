# mh_infrared
Infrared codes sender and reciever app for MicroHydra

Can send signals and maybe scan (can't test it).
Also it can use popup_options_2d function, which is not implemented in main branch yet.
You can take popup_options_2d from temp.py file and insert it into /lib/mhoverlay.py to test it.
Also, you can use __init__(MH2.0).py, that works with experimental-multiplatform branch (which has built-in support for 2d popups)

If you got any bugs - welcome to Issues tab

This code can open .ir files, which you can get by exporting [Mi Remote Database](https://github.com/ysard/mi_remote_database) in Flipper format, and saving it in /sd/ir

Also, UpyIrRx.py and UpyIrTx.py are stolen from [here](https://github.com/meloncookie/RemotePy)

Would be easier to develop, if russians weren't bombing our power plants. [Help Ukraine](https://u24.gov.ua/)
