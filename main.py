import psutil;      # python3-psutil
import serial;      # python3-serial
import time;

i_net_snd = 0;
i_net_rec = 0;
i_net_snd_old = 0;
i_net_rec_old = 0;

# format a number of bytes into 4 chars, inc KMGT suffix
# 4006490112
def fmt(v):
    sfx = "B";
    f = float(v);

    t = 1024 * 1024 * 1024 * 1024;
    g = 1024 * 1024 * 1024;
    m = 1024 * 1024;
    k = 1024;

    # first determine magnitude and suffix
    if v >= t:
        sfx = "T";
        f = f / t;
    elif v >= g:
        sfx = "G";
        f = f / g;
    elif v >= m:
        sfx = "M";
        f = f / m;
    else:
        sfx = "K";
        f = f / k;
        
    # now solve for when still four-digits e.g. 1023 GB 
    if f > 999:
        f = f / 1024;
        if sfx == "G":
            sfx = "T";
        elif sfx == "M":
            sfx = "G";
        elif sfx == "K":
            sfx = "M";

    # if below 10 then show 1dp
    if f > 9:
        str = f"{f:0.0f}";
    else:
        str = f"{f:0.1f}";

    return f"{str:>3}" + sfx;

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
    l = len(b);
    while(i < l):
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

# you may need to change this to /dev/ttyUSB0 or something else
arduino = serial.Serial(port='/dev/ttyACM0', baudrate=9600, timeout=None);
while arduino.is_open:
    time.sleep(5);      # sleep at the start because I'm paranoid about the first bootup/reset taking a moment

    # CPU
    #
    f_cpu = psutil.cpu_percent();
    s_cpu = str(int(f_cpu+0.5));

    f_tmp = psutil.sensors_temperatures()['coretemp'][0].current;
    s_tmp = str(int(f_tmp+0.5));

    line1 = "CPU " + pct(f_cpu) + f"  {s_cpu:>3}% {s_tmp:>3}'";

    
    # RAM
    #
    o_ram = psutil.virtual_memory();

    f_ram = o_ram.percent;
    s_ram = str(int(f_ram+0.5));

    line2 = "RAM " + pct(o_ram.percent) + "  " + fmt(o_ram.total - o_ram.available) + " " + fmt(o_ram.available);

  

    # HDD
    #
    o_dsk = psutil.disk_usage('/');
    f_dsk = o_dsk.percent;     # used space
    s_dsk = str(int(f_dsk+0.5));

    line3 = "HDD " + pct(o_dsk.percent) + "  " + fmt(o_dsk.used) + " " + fmt(o_dsk.total - o_dsk.used);
 


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
        
    #bits -> bytes
    i_net_max = i_net_max/8;
    i_net_snd_since = i_net_snd_since/8;
    i_net_rec_since = i_net_rec_since/8;
    
    s_net_pct = "     ";    
    if i_net_max > 100000000:    # 100MB
        s_net_pct = "#####";
    elif i_net_max > 10000000:  # 10MB
        s_net_pct = "#### ";
    elif i_net_max > 1000000:   # 1MB
        s_net_pct = "###  ";
    elif i_net_max > 100000:    # 100kB
        s_net_pct = "##   ";
    elif i_net_max > 10000:    # 10kB
        s_net_pct = "#    ";

    line4 = "NET " + s_net_pct + "  " + fmt(i_net_snd_since) + " " + fmt(i_net_rec_since);




    #print(line1);
    #print(line2);
    #print(line3);
    #print(line4);

    # 2 = STX (Start of text)
    # 3 = ETX (End of text)
    arduino.write([2])
    arduino.write(bittify(line1))
    arduino.write(bittify(line3))   # the lcd hardware wraps lines in the order 1324 for some reason
    arduino.write(bittify(line2))
    arduino.write(bittify(line4))
    arduino.write([3]);

arduino.close();
