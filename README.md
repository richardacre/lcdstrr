An Arduino project to display system stats on a 20x4 I2C LCD display.

Python script runs as a service and updates the screen every 5 seconds.

Stats are:
- CPU - [Percent Load] - Percent - Core Temperature
- RAM - [Percent Used] - Used - Free
- HDD - [Percent Used] - Used - Free
- NET - [10k|100k|1M|10M|100M] - Up - Down

Dependencies:
- Arduino : hd44780 
- Python : psutil + serial

No warranty or support given or implied, this is a personal project that I am sharing for the curious.

![image](https://github.com/user-attachments/assets/e4a6651e-e8da-41ef-b5f8-982ff70353dc)
