# check_synology [![Release](https://img.shields.io/github/release/wernerfred/check_synology.svg)](https://github.com/wernerfred/check_synology/releases)

This plugin uses ```snmpv3``` with ```MD5``` + ```AES``` to check a lot of different values on your Synology DiskStation.

This check plugin needs ```pysnmp``` to be installed on your system. You can install it with: ```pip3 install pysnmp```

Usage:
```
> python3 check_synology.py -h
usage: check_synology.py hostname username authkey privkey {mode} [-h] [-w W] [-c C] [-p PORT]
```

Example check:
```
> python3 check_synology.py hostname snmp_user auth_key priv_key load
OK - load average: 1.48, 1.71, 1.74 | load1=1.48c load5=1.71c load15=1.74c
```

Available modes:

| mode    | description                                                                | warning/critical                    |
| :-----: | -------------------------------------------------------------------------- | ----------------------------------- |
| load    | Checks the load1, load5 and load15 values                                  | if more than w/c in int (only load1)|
| memory  | Checks the physical installed memory (unused, cached and total)            | if less usable than w/c in %        |
| disk    | Detects and checks all disks (name, status, temperature)                   | if temp higher than w/c in °C <br> if c is set it will also trigger if status <br> is Failure or Crashed                                                             |
| storage | Detects and checks all disks (free, total, %)                              | if more used than w/c in %          |
| update  | Shows the current DSM version and if DSM update is available               | set w/c to any int this triggers: <br> warning if available and critical <br> if other than un-/available                                                           |
| status  | Shows model, s/n, temp and status of system, fan, cpu fan and power supply | if temp higher than w/c in °C       |

Note: A custom port can be specified by using ```-p```. The port defaults to 161.

Example ```CheckCommand``` for use with ```icinga2```:
```
object CheckCommand "check_synology" {
  command = ["/usr/bin/python3", PluginDir + "/check_synology.py" ]

  arguments = {
    "--host" = {
       skip_key = true
       order = 0
       value = "$synology_host$"
    }
    "--username" = {
       skip_key = true
       order = 1
       value = "$synology_snmp_user$"
    }
    "--authkey" = {
       skip_key = true
       order = 2
       value = "$synology_snmp_authkey$"
    }
    "--privkey" = {
       skip_key = true
       order = 3
       value = "$synology_snmp_privkey$"
    }
    "--mode" = {
       skip_key = true
       order = 4
       value = "$synology_mode$"
    }
    "-w" = "$synology_warning$"
    "-c" = "$synology_critical$"
  }
}
```
Example ```Service``` for use with ```icinga2```:
```
apply Service "syno-load" {
  import "generic-service"

  check_command = "check_synology"

  vars.synology_mode = "load"
  vars.synology_host = "$address$"
  
  vars.synology_warning = "$synology_load_w$"
  vars.synology_critical = "$synology_load_c$"

  assign where host.vars.os == "DSM"
}
```
Make sure to set ```synology_snmp_user```, ```synology_snmp_autkey``` and ```synology_snmp_privkey``` (e.g. in the host config file).


If you want to add a missing check or another value to be added than you can use the [official Synology MIB Guide](https://global.download.synology.com/download/Document/MIBGuide/Synology_DiskStation_MIB_Guide.pdf) as a hint for the right MIBs / OIDs and start a pull-request.

This plugin was tested successfully with DS215j and DS718+

Note: As of version 0.2 and higher only python3 is supported. Version 0.1 was the last python2 compatible release.

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="https://github.com/KreativeKrise"><img src="https://avatars.githubusercontent.com/u/6876675?v=4?s=100" width="100px;" alt=""/><br /><sub><b>KreativeKrise</b></sub></a><br /><a href="https://github.com/wernerfred/check_synology/commits?author=KreativeKrise" title="Code">💻</a></td>
    <td align="center"><a href="http://katulu.io"><img src="https://avatars.githubusercontent.com/u/9132055?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Nicolai</b></sub></a><br /><a href="https://github.com/wernerfred/check_synology/commits?author=nbuchwitz" title="Code">💻</a> <a href="#platform-nbuchwitz" title="Packaging/porting to new platform">📦</a></td>
  </tr>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!
