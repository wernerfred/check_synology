# check_synology [![Release](https://img.shields.io/github/release/wernerfred/check_synology.svg)](https://github.com/wernerfred/check_synology/releases)


## About

A monitoring plugin for checking different values on a Synology DiskStation,
compatible with Nagios and Icinga.

The plugin was tested successfully with DS214play, DS215j, DS216+, DS218 and
DS718+ models. For communication, it uses `SNMPv3` with `MD5` + `AES`.

If you want to add a missing check or another value, you are most welcome to
submit a patch / pull request. As a reference for discovering the right
MIBs / OIDs, please have a look at the official [Synology DiskStation MIB Guide].


## Setup

`check_synology` is based on the [easysnmp] SNMP library, which is a binding to
the [Net-SNMP package]. You might need to install the corresponding packages on
your operating system.

An example to invoke the installation on a Debian-based system is:
```shell
apt install --yes libsnmp-dev snmp-mibs-downloader
pip install git+https://github.com/wernerfred/check_synology
```


## Usage
```shell
check_synology --help
```

```shell
check_synology
usage: check_synology [-h] [-w W] [-c C] [-t T] [-r R] [-p PORT] hostname username authkey privkey {load,memory,disk,storage,update,status}
```

A custom port can be specified by using `-p`. The default value is `161`.
Custom timeouts (`-t`) and retries (`-r`) can be specified by using `-t` and `-r` respectively. The default values are `-t 10` and `-r 3`.

### Available modes

| mode    | description                                                                | warning/critical                    |
| :-----: | -------------------------------------------------------------------------- | ----------------------------------- |
| load    | Checks the load1, load5 and load15 values                                  | if more than w/c in int (only load1)|
| memory  | Checks the physical installed memory (unused, cached and total)            | if less usable than w/c in %        |
| disk    | Detects and checks all disks (status, temperature)                         | if status is "SystemPartitionFailed" or "Crashed", will trigger CRITICAL <br> if temperature is higher than w/c in °C, will trigger WARNING/CRITICAL |
| storage | Detects and checks all disks (free, total, %)                              | if more used than w/c in %          |
| update  | Shows the current DSM version and if DSM update is available               | if update is "Unavailable", will trigger OK <br> if update is "Available", will trigger WARNING <br> otherwise: UNKNOWN |
| status  | Shows model, s/n, temp and status of system, fan, cpu fan and power supply | if temp higher than w/c in °C       |



## Example check
```shell
check_synology hostname snmp_user auth_key priv_key load
OK - load average: 1.48, 1.71, 1.74 | load1=1.48c load5=1.71c load15=1.74c
```


## Icinga 2 integration

For integrating the check program into Icinga 2, you can use the configuration files
in the ``icinga2`` subdirectory. You can easily acquire the files using:
```shell
wget https://raw.githubusercontent.com/wernerfred/check_synology/master/icinga2/synology-command.conf
wget https://raw.githubusercontent.com/wernerfred/check_synology/master/icinga2/synology-services.conf
wget https://raw.githubusercontent.com/wernerfred/check_synology/master/icinga2/synology-host.conf
```

In order to put the `check_synology` program at the right location aligned with the
definition within `synology-command.conf`, regardless where it has been installed
on your system, use:

```shell
ln -s $(which check_synology) /usr/lib/nagios/plugins/check_synology
```


## Development

For setting up a development sandbox and running the software tests, you might
want to follow this walkthrough.

```shell
git clone https://github.com/wernerfred/check_synology
cd check_synology
make test
```

By running `make test`, a Python virtual environment will be created within the
`.venv` folder of your working tree. Use `source .venv/bin/activate` to
activate it.

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center"><a href="https://github.com/KreativeKrise"><img src="https://avatars.githubusercontent.com/u/6876675?v=4?s=100" width="100px;" alt=""/><br /><sub><b>KreativeKrise</b></sub></a><br /><a href="https://github.com/wernerfred/check_synology/commits?author=KreativeKrise" title="Code">💻</a></td>
      <td align="center"><a href="http://katulu.io"><img src="https://avatars.githubusercontent.com/u/9132055?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Nicolai</b></sub></a><br /><a href="https://github.com/wernerfred/check_synology/commits?author=nbuchwitz" title="Code">💻</a> <a href="#platform-nbuchwitz" title="Packaging/porting to new platform">📦</a></td>
      <td align="center"><a href="https://github.com/Byolock"><img src="https://avatars.githubusercontent.com/u/25748003?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Byolock</b></sub></a><br /><a href="https://github.com/wernerfred/check_synology/commits?author=Byolock" title="Code">💻</a> <a href="https://github.com/wernerfred/check_synology/issues?q=author%3AByolock" title="Bug reports">🐛</a></td>
      <td align="center"><a href="https://github.com/amotl"><img src="https://avatars.githubusercontent.com/u/453543?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Andreas Motl</b></sub></a><br /><a href="https://github.com/wernerfred/check_synology/commits?author=amotl" title="Code">💻</a> <a href="#ideas-amotl" title="Ideas, Planning, & Feedback">🤔</a> <a href="#example-amotl" title="Examples">💡</a></td>
      <td align="center"><a href="http://thomasgalliker.net"><img src="https://avatars.githubusercontent.com/u/1712534?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Thomas Galliker</b></sub></a><br /><a href="https://github.com/wernerfred/check_synology/commits?author=Doomas" title="Code">💻</a></td>
      <td align="center"><a href="https://github.com/Kraeutergarten"><img src="https://avatars.githubusercontent.com/u/5418554?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Kraeutergarten</b></sub></a><br /><a href="#userTesting-Kraeutergarten" title="User Testing">📓</a></td>
      <td align="center"><a href="https://github.com/jebabin"><img src="https://avatars.githubusercontent.com/u/11474713?v=4?s=100" width="100px;" alt=""/><br /><sub><b>jebabin</b></sub></a><br /><a href="https://github.com/wernerfred/check_synology/commits?author=jebabin" title="Documentation">📖</a></td>
    </tr>
    <tr>
      <td align="center"><a href="https://github.com/kamakazikamikaze"><img src="https://avatars.githubusercontent.com/u/8862823?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Kent Coble</b></sub></a><br /><a href="#plugin-kamakazikamikaze" title="Plugin/utility libraries">🔌</a></td>
      <td align="center"><a href="https://github.com/to-kn"><img src="https://avatars.githubusercontent.com/u/1778428?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Tobias Knipping</b></sub></a><br /><a href="https://github.com/wernerfred/check_synology/commits?author=to-kn" title="Code">💻</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!


[easysnmp]: https://pypi.org/project/easysnmp/
[Net-SNMP package]: http://www.net-snmp.org/
[Synology DiskStation MIB Guide]: https://global.download.synology.com/download/Document/MIBGuide/Synology_DiskStation_MIB_Guide.pdf
