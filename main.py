import psutil;      # python3-psutil
import serial;      # python3-serial
import time;

i_net_snd = 0;
i_net_rec = 0;
i_net_snd_old = 0;
i_net_rec_old = 0;

# format a number of bytes into 4 chars, inc KMGT suffix
# todo: divide by multiples of 1024 instead of 1000
def fmt(v):
    sfx = "B";
    f = float(v);

    # first determine magnitude and suffix
    # and bring into the range 0-999
    if v > 999999999999:
        sfx = "T";
        f = f / 1000000000000;
    elif v > 999999999:
        sfx = "G";
        f = f / 1000000000;
    elif v > 999999:
        sfx = "M";
        f = f / 1000000;
    else:
        sfx = "K";
        f = f / 1000;

    # if below 10 then show 1dp
    if f < 10:
        str = f"{f:0.1f}";
    else:
        str = f"{f:0.0f}";

    return f"{str:>3}" + sfx;

# converts a percentage to a bar chart
def pct(v):
    if v > 90:
        return "#####";
    if v > 70:
        return "#### ";
    if v > 50:
        return "###  ";
    if v > 30:
        return "##   ";
    if v > 10:
        return "#    ";
    return "     ";

# convert string to byte array,
def bittify(s):
    b = bytearray();
    b.extend(s.encode('ascii'));
    i = 0;
    while(b[i] != 0):
        if b[i] == 35:      # # (hash) replace with solid block
            b[i] = 255;
        if b[i] == 39:      # ' replace with degree symbol
            b[i] = 223;
        i = i + 1;
    return b;


# get these before the first compute, or it'll show the total send/rec since power on
# for the first few seconds!
o_net = psutil.net_io_counters();
i_net_snd_old = o_net.bytes_sent * 1.6;     # convert bytes to bits, then per-second
i_net_rec_old = o_net.bytes_recv * 1.6;

arduino = serial.Serial(port='/dev/ttyACM0', baudrate=9600, dsrdtr=False, timeout=None);
while arduino.is_open:
    time.sleep(5);      # sleep at the start because I'm paranoid about the first bootup/reset taking a moment

    # CPU
    #
    f_cpu = psutil.cpu_percent();
    s_cpu = str(int(f_cpu+0.5));

    f_tmp = psutil.sensors_temperatures()['coretemp'][0].current;
    s_tmp = str(int(f_tmp+0.5));

    line1 = "CPU " + pct(f_cpu) + f"  {s_cpu:>3}% {s_tmp:>3}'\0";

    
    # RAM
    #
    o_ram = psutil.virtual_memory();

    f_ram = o_ram.percent;
    s_ram = str(int(f_ram+0.5));

    line2 = "RAM " + pct(o_ram.percent) + "  " + fmt(o_ram.total - o_ram.available) + " " + fmt(o_ram.available) + "\0";

  

    # HDD
    #
    o_dsk = psutil.disk_usage('/');
    f_dsk = o_dsk.percent;     # used space
    s_dsk = str(int(f_dsk+0.5));

    line3 = "HDD " + pct(o_dsk.percent) + "  " + fmt(o_dsk.used) + " " + fmt(o_dsk.total - o_dsk.used) + "\0";
 


    # NET
    #
    o_net = psutil.net_io_counters();
    i_net_snd = o_net.bytes_sent * 1.6;     # convert bytes to bits, then per-second
    if i_net_snd_old > i_net_snd:
        i_net_snd_old = 0;

    i_net_rec = o_net.bytes_recv * 1.6;
    if i_net_rec_old > i_net_rec:
        i_net_rec_old = 0;

    i_net_snd_since = i_net_snd-i_net_snd_old;
    i_net_rec_since = i_net_rec-i_net_rec_old;    
    
    i_net_snd_old = i_net_snd;
    i_net_rec_old = i_net_rec;
    
    # make a "percentage" bar that's sort of logarithmic, based on whichever is higher out of s/r
    i_net_max = i_net_snd_since;
    if i_net_rec_since > i_net_max:
        i_net_max = i_net_rec_since;
    
    s_net_pct = "     ";    
    if i_net_max > 100000000:    # 100Mb
        s_net_pct = "#####";
    elif i_net_max > 10000000:  # 10Mb
        s_net_pct = "#### ";
    elif i_net_max > 1000000:   # 1Mb
        s_net_pct = "###  ";
    elif i_net_max > 100000:    # 100kb
        s_net_pct = "##   ";
    elif i_net_max > 10000:    # 10kb
        s_net_pct = "#    ";

    line4 = "NET " + s_net_pct + "  " + fmt(i_net_snd_since) + " " + fmt(i_net_rec_since) + "\0";




    #print(line1);
    #print(line2);
    #print(line3);
    #print(line4);

    arduino.write("!1\0".encode('ascii')); 
    arduino.write(bittify(line1));

    arduino.write("!2\0".encode('ascii'));
    arduino.write(bittify(line2));

    arduino.write("!3\0".encode('ascii'));
    arduino.write(bittify(line3));
    
    arduino.write("!4\0".encode('ascii'));
    arduino.write(bittify(line4));

arduino.close();
