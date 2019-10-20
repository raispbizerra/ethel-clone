Copyright (C) 2017 Raí Sales Pereira Bizerra

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
  
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
  
You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

# ETHEL ![ETHEL](media/logo_small.png "ETHEL")

## DESCRIPTION

System for instrumentation of medical examinations, wii balance board version.

## REQUIREMENTS
### Packages
```bash
sudo apt install flex bison libbluetooth-dev libcwiid-dev python-gobject python3-tk python3-dev at-spi2-core python3 python3-pip
```

#### Python3 modules
```bash
sudo -H pip3 install awk flex pybluez xlrd xlwt xlutils matplotlib
```
			
[cwiid](https://github.com/azzra/python3-wiimote) Clone repository and follow README instructions

## USAGE
```bash
./interface
```