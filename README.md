# mTagPython
Simple and incomplete python implementation of the mTag API (Grenoble)

## Usage

For help :
```shell
$ python3 mTag_python.py -h
```

## Connection to I3

The code may be connected to I3 if needed, for now I use it to print the hours of arrival at my work bus stop in the direction of my house and vice-versa.
You may modify the "print_to_home_from_work" and use the "-custom" option or just create your own.

You just need to modify your i3 config file (may be any of the following):

- ~/.config/i3status/config
- /etc/xdg/i3status/config
- ~/.i3status.conf
- /etc/i3status.conf

Add the following line to the "bar" element:
```shell
	status_command <PATH to i3_mTag_on_bar.sh>
```
(You can also directly copy the script to the config file)
