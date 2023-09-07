# CyberBlitz 2023 - CI/Seedy

by amon

## Challenge Information

This is a CI/CD themed misc/pwn challenge where users are allowed to control the contents of what's
compiled by gcc, javac, and Python `compile`. Only the return code of the build is returned to the
user which limits an attacker's capabilities greatly. The goal is to obtain RCE.

Initially, only the gcc processor is available and the other processors require authentication
through an 'unlock code' UUID generated randomly at start up, which is present at
`/unlock_code.txt`. Linker error codes in gcc can be used to leak the contents of this file byte by
byte with a specially crafted assembler instructions.

Once the unlock code is obtained, the javac processor can be used to obtain RCE through annotator
processors in a JAR provided in the classpath. The attacker is able to control the complete contents
of the classpath and the Java file to compile as these are unpacked from a ZIP file. Once a reverse
shell is obtained, the `/readflag` SUID binary can be executed to grab the flag.

This was heavily inspired by:

* HXP 36C3 - compilerbot: https://hxp.io/blog/64/hxp-36C3-CTF-compilerbot/
* Real World CTF 4 - Secured Java: https://www.kalmarunionen.dk/writeups/2022/rwctf/secured-java/

## Distributions

The public-facing description of the challenge:

```
Continuous Integration is such a pain these days. Sometimes you just want to see if your code
compiles or not. CI/Seedy is that solution. Access your free trial today at: 192.168.10.100:31337.
For on-premise deployments, please see the attached file.
```

Download: ciseedy-2941d82880859591978e75fef66b81a5.tar.gz

IMPORTANT: The only files that should be provided to the participants are in `distrib/`. None of
the files in the distributable should ever contain the actual flag.

## Services

For more information on the services and how to setup, build, and run them, please see this
[README](service/README.md).

The default flag is: `CyberBlitz{Wh4tev3r_15_ju5t_3n0ugh_b0rn_d3s3rt_5un}`.

## Solutions

For the full writeup as well as more information on how to build and run the solutions, please see
this [README](solutions/README.md).
