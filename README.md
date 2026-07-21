# 💿 Operator
A Windows Anti-IdentityCRL script made in Python.<br/>
What it does:

1. Stop & disable bad services *(DoSvc, CDPSvc, CDPUserSvc, wlidsvc)*
2. Remove device ID from IdentityCRL
3. View all device Microsoft accounts<br/>
   *(currently, the script does not log them off, but I probably will add that as an optional thing)*

## 📦 Installation
1. Install Python, **without** Administrator privileges, **with** the Environment PATH setting.
2. After it installs, click Win+R and type:<br/>
   `python -c "import os,urllib.request as r,subprocess,sys;f=open(path:=os.getenv('TEMP')+'/operator.py','wb');f.write(r.urlopen(""https://github.com/Olafcio1/Operator/raw/refs/heads/main/__main__.py"").read());f.close();subprocess.run([sys.executable, path])`

   This also works on other systems, although I'm not sure why would you wanna run it there.<br/>
   It 100% does nothing on ReactOS.
