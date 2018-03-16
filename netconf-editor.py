#!/usr/bin/env python3

"""
Configuration résau pour Gentoo et Debian

License Libre
rod.cat@free.fr
"""

import os

def from_masq(masq):
    """ Convertit la notation pointée en notation CIDR."""
    oct1, oct2, oct3, oct4 = masq.split(".")
    oct1 = str(bin(int(oct1)))[2:]
    oct2 = str(bin(int(oct2)))[2:]
    oct3 = str(bin(int(oct3)))[2:]
    oct4 = str(bin(int(oct4)))[2:]
    check_bin = oct1 + oct2 + oct3 + oct4
    if "1" not in check_bin:
        cidr = "0"
    else:
        check_bin = check_bin.split("0")
        check = True
        for e in check_bin[1:]:
            if "1" in e:
                check = False
                return(False)
                break
        if check:
            cidr = str(len(check_bin[0]))
            return(cidr)

def from_cidr(cidr):
    """ Convertit la notation CIDR en notation pointée."""
    cidr = int(cidr)
    oct_cidr = "1" * cidr + "0" * (32 - cidr)
    oct1 = str(int(oct_cidr[:8], 2))
    oct2 = str(int(oct_cidr[8:16], 2))
    oct3 = str(int(oct_cidr[16:24], 2))
    oct4 = str(int(oct_cidr[24:], 2))
    masq = oct1 + "." + oct2 + "." + oct3 + "." + oct4
    return(masq)

#Récupération de la config actuelle via 'ip'
os.system('touch current_config')
os.system('whoami > current_config')
os.system('ip route >> current_config')
os.system('ip a >> current_config')
#os.system('export | grep proxy >> current_config')

root = False
with open('current_config') as cc:
    interface_dic = {}
    name_int = ''
    route = ''
    for line in cc:
        if 'root' in line:
            root = True
        if line[0] != ' ':
            if line[0].isdigit() and line[1] == ':':
                if int(line[0]) > 1:
                    for i in line[3:]:
                        if i == ':':
                            break
                        else:
                            name_int += i
            elif 'default' in line:
                route = line.split(' ')[2]
        elif name_int != '':
            if 'inet ' in line:
                slash_index = line.index('/')
                ip = line[9:slash_index]
                masq = line[slash_index + 1:slash_index + 3]
                if masq[1] == ' ':
                    masq = masq[0]
                interface_dic[name_int] = [ip, masq, route]

interface_list = list(interface_dic.keys())
print()
print()
print('                       & ~ NETCONF-EDITOR ~ &')
print()
print('''_ . , ; - « < ` ' " : \ ( [ {| ^!@!^ |} ] ) / : " ' ´ > » - ; , . _''')
print()
print()
if root:
    print('I AM ROOT!')
else:
    print('Lancez le script en root')
    print('pour pouvoir modifier les fichiers de configuration')
print()
print('interfaces réseau trouvées par la commande ip:')
for i in interface_list:
    print('  {}'.format(i))
    print('    {}/{}'.format(interface_dic[i][0], interface_dic[i][1]))
    print('    {}'.format(interface_dic[i][2]))
print('***')
print('Quelle est votre distibution?')
print('  Gentoo -> 1 /etc/conf.d/net')
print('  Debian -> 2 /etc/network/interfaces')
#print('  Redhat -> 3 ')
while True:
    distrib = input('Entrez votre choix: ')
    if distrib == '1' or distrib == '2':
        break
    else:
        print('Choisissez 1 ou 2')
interface_dic = {}
print()

def read_gconf(ext=''):
    """Lecture des fichiers de configuration Gentoo"""
    fichier = '/etc/conf.d/net' + ext
    with open(fichier) as conf_file:
        dns = ''
        for line in conf_file:
            if line[0] == '#':
                pass
            else:
                if 'config_' in line:
                    egal_index = line.index('=')
                    name_int = line[7:egal_index]
                    split_line = line.split(' ')
                    if len(split_line) == 1:
                        slash_index = line.index('/')
                        ip = line[egal_index + 2:slash_index]
                        masq = line.split('/')[1][:-2]
                    else:
                        ip = split_line[0][egal_index + 2:]
                        masq_point = split_line[2]
                        masq = from_masq(masq_point)
                    interface_dic[name_int] = [ip, masq]
                elif 'routes_' in line:
                    route = line.split(' ')[2][:-2]
                    interface_dic[name_int].append(route)
                elif 'dns_servers_' in line:
                    dns = line.split('"')[1]
                    dns = dns.split(' ')
                    interface_dic[name_int].append(dns)
        if dns == '':
            with open('/etc/resolv.conf') as res:
                dns = []
                for line in res:
                    if 'search' in line or 'nameserver' in line:
                        dns.append(line.split(' ')[1][:-1])
            interface_dic[name_int].append(dns)

dhcp = False
def read_dconf(ext=''):
    """Lecture des fichiers de configuration Debian"""
    fichier = '/etc/network/interfaces' + ext
    with open(fichier) as conf_file:
        for line in conf_file:
            if line[0] == '#':
                pass
            else:
                if 'iface' in line:
                    name_int = line.split(' ')[1]
                    if name_int == 'lo':
                        pass
                    else:
                        interface_dic[name_int] = []
                    if 'dhcp' in line:
                        dhcp = True
                elif 'address' in line:
                    ip = line.split(' ')[-1]
                    ip = ip[:-1]
                    interface_dic[name_int] = [ip]
                elif 'netmask' in line:
                    masq = line.split(' ')[-1]
                    masq = from_masq(masq)
                    interface_dic[name_int].append(masq)
                elif 'gateway' in line:
                    route = line.split(' ')[-1]
                    interface_dic[name_int].append(route)
    try:
        with open('/etc/resolv.conf') as res:
            dns = []
            for line in res:
                if 'search' in line or 'nameserver' in line:
                    dns.append(line.split(' ')[1][:-1])
        interface_dic[name_int].append(dns)
    except:
        pass

os.system('touch sauvegarde')
if distrib == '1':
    read_gconf()
    os.system('ls /etc/conf.d | grep net. > sauvegarde')
elif distrib == '2':
    read_dconf()
    os.system('ls /etc/network | grep interfaces. > sauvegarde')
save_list = []
with open('sauvegarde') as sg:
    for line in sg:
        if '.' in line:
            if len(line.split('.')[-1][:-1]) > 1:
                save_list.append(line.split('.')[-1][:-1])

interface_list = list(interface_dic.keys())
for i in interface_list:
    print('Interface réseau {}:'.format(i))
    if dhcp:
        print('    dhcp')
    else:
        print('    ip = {}/{}'.format(interface_dic[i][0], interface_dic[i][1]))
        print('    passerelle = {}'.format(interface_dic[i][2]))
        try:
            for i in interface_dic[i][3]:
                print('    dns = {}'.format(i))
        except IndexError:
            pass
print('***')
save = input('sauvegarder la configuration actuelle? [Oui|Non]: ')
if len(save) > 0 and save[0].lower() == 'o':
    print('    Choississez un nom pour votre sauvegarde')
    print("    il servirat à la rappeler")
    extension = input('Entrez un nom (simple) pour la sauvegarde: ')
    if distrib == '1':
        action = 'cp /etc/conf.d/net /etc/conf.d/net.{}'.format(extension)
        os.system(action)
    elif distrib == '2':
        action = 'cp /etc/network/interfaces'
        action += ' /etc/network/interfaces.{}'.format(extension)
        os.system(action)
        os.system('cp /etc/resolv.conf /etc/resolv.conf.{}'.format(extension))
        os.system('cp /etc/apt/apt.conf /etc/apt/apt.conf.{}'.format(extension))
print()
saves = False
if len(save_list) > 0:
    saves = True
    save_ind = 0
    print('Sauvegardes actuelles: ')
    for i in save_list:
        print('    {} -> {}'.format(i, save_ind))
        save_ind += 1
    print()

new = False

print('Charger une sauvegarde ou configurer une nouvelle connexion?')
while True:
    load = input('C pour charger, N pour nouvelle: ')
    if load.upper() == 'C':
        if not saves:
            print('Pas de sauvegarde')
        else:
            new = False
            break
    elif load.upper() == 'N':
        new = True
        break
    else:
        print('C ou N')
if new:
    print('Choisissez une interface réseau à configurer')
    pos = 0
    for i in interface_list:
        print(i, '->', pos)
        pos += 1
    while True:
        carte_index = input(': ')
        if carte_index.isdigit():
            if int(carte_index) >= 0 and int(carte_index) < len(interface_list):
                break
            else:
                print('Un chiffre à partir de 0 ou tapez Entrée')
        elif carte_index == '':
            carte_index = '0'
            break
        else:
            print('Un chiffre à partir de 0 ou tapez Entrée')
    carte_reseau = interface_list[int(carte_index)]
    print('Quelle type de connexion?')
    print('  DHCP -> 1')
    print('  manuelle -> 2')
    while True:
        con_mod = input('Entrez votre choix: ')
        if con_mod == '1' or con_mod == '2':
            break
        else:
            print('Choisissez 1 ou 2')

    if con_mod == '2':
        def ip_check(ip):
            test = True
            check = ip.split('.')
            if len(check) != 4:
                test = False
            else:
                for i in check:
                    if i.isdigit():
                        pass
                    else:
                        test = False
            return(test)

        def print_ad():
            print('adresse invalide')

        while True:
            ip = input("Entrez l'adresse ip: ")
            if ip_check(ip):
                break
            else:
                print_ad()

        print('Entrez un masque de sous-réseau')

        while True:
            masq = input('/cidr ou notation pointée: ')
            if masq == '':
                print_ad()
            elif len(masq) > 0 and len(masq) < 4:
                if masq[0] == '/':
                    masq = masq[1:]
                if masq.isdigit() and int(masq) > 0 and int(masq) < 33:
                    break
                else:
                    print_ad()
            elif ip_check(masq):
                if from_masq(masq):
                    masq = from_masq(masq)
                    break
                else:
                    print_ad()

        while True:
            route = input('Entrez une passerelle par défaut: ')
            if ip_check(route):
                break
            else:
                print_ad()

        while True:
            dns1 = input('Entrez un premier dns: ')
            if ip_check(dns1):
                break
            else:
                print_ad()

        while True:
            dns2 = input('et un deuxième: ')
            if ip_check(dns2):
                break
            else:
                print_ad()

    set_proxy = False
    proxy = input('Souhaitez-vous configurer un accès via proxy? [Oui|Non]: ')
    if len(proxy) > 0 and proxy[0].lower() == 'o':
        while True:
            print('xxx.xxx.xxx.xxx:xxxx')
            proxy = input("Entrez l'adresse et le port du proxy: ")
            if ':' in proxy:
                proxy_ad, proxy_port = proxy.split(':')
                if ip_check(proxy_ad) and proxy_port.isdigit():
                    set_proxy = True
                    break
                else:
                    print_ad()
            else:
                print_ad()
    print()
    print('Interface réseau: {}'.format(carte_reseau))
    if con_mod == '2':
        print('    ip = {}/{}'.format(ip, masq))
        print('    passerelle = {}'.format(route))
        print('    dns = {}'.format(dns1))
        print('    dns = {}'.format(dns2))
    else:
        print('    dhcp')
    if set_proxy:
        print('    proxy = {}'.format(proxy))
    print()
    go = input('Activer cette configuration maintenant? [Oui|Non]: ')
    if len(go) > 0 and go[0].lower() == 'o':
        print('Les fichiers de configuration concernés vont être modifiés!')
        go = input('Confirmer? [Oui|Non]: ')
        if len(go) > 0 and go[0].lower() == 'o':
            if distrib == '1':
                if con_mod == '1':
                    os.system('dhcpd {}'.format(carte_reseau))
                else:
                    config = 'config_{}="{}/{}"'.format(carte_reseau, ip, masq)
                    gw = 'routes_{}="default via {}"'.format(
                        carte_reseau, route)
                    dn = 'dns_servers_{}="{} {}"'.format(
                        carte_reseau, dns1, dns2)

                    with open('/etc/conf.d/net', 'w') as etc:
                        etc.write(config + '\n')
                        etc.write(gw + '\n')
                        etc.write(dn + '\n')
                if set_proxy:
                    https = 'export https_proxy="https://{}"'.format(proxy)
                    http = 'export http_proxy="http://{}"'.format(proxy)
                    ftp = 'export ftp_proxy="http://{}"'.format(proxy)
                    rsync = 'export RSYNC_PROXY="{}"'.format(proxy)
                    os.system(https)
                    os.system(http)
                    os.system(ftp)
                    os.system(rsync)
            else:
                if con_mod == '1':
                    with open('/etc/network/interfaces', 'w') as etc:
                        etc.write('auto {}\n'.format(carte_reseau))
                        etc.write('allow-hotplug {}\n'.format(carte_reseau))
                        etc.write('iface {} inet dhcp\n'.format(carte_reseau))
                else:
                    masq = from_cidr(masq)
                    with open('/etc/network/interfaces', 'w') as etc:
                        etc.write('auto {}\n'.format(carte_reseau))
                        etc.write('iface {} inet static\n'.format(carte_reseau))
                        etc.write('    address {}\n'.format(ip))
                        etc.write('    netmask {}\n'.format(masq))
                        etc.write('    gateway {}\n'.format(route))
                    with open('/etc/resolv.conf', 'w') as res:
                        etc.write('nameserver {}\n'.format(dns1))
                        etc.write('nameserver {}\n'.format(dns2))
                if set_proxy:
                    with open('/etc/apt/apt.conf', 'w') as apt:
                        http = 'Acquire::https::proxy "https://{}";'.format(
                            proxy)
                        http = 'Acquire::http::proxy "http://{}";'.format(proxy)
                        http = 'Acquire::ftp::proxy "ftp://{}";'.format(proxy)
                    action = ('echo "http_proxy=http://{}" >> /etc/environment'
                              ).format(proxy)
                    os.system(action)
                    action = (
                        'echo "https_proxy=https://{}" >> /etc/environment'
                    ).format(proxy)
                    os.system(action)
                    action = ('echo "ftp_proxy=ftp://{}" >> /etc/environment'
                              ).format(proxy)
                    os.system(action)
else:
    print('Entrez le n° de la sauvegarde à charger')
    ind = input(': ')
    print()
    extension = save_list[int(ind)]
    interface_dic = {}
    if distrib == '1':
        read_gconf('.' + extension)
    elif distrib == '2':
        read_dconf('.' + extension)
    interface_list = list(interface_dic.keys())
    for i in interface_list:
        print('Interface réseau {}:'.format(i))
        if dhcp:
            print('    dhcp')
        else:
            print('    ip = {}/{}'.format(
                interface_dic[i][0], interface_dic[i][1]))
            print('    passerelle = {}'.format(interface_dic[i][2]))
            try:
                for i in interface_dic[i][3]:
                    print('    dns = {}'.format(i))
            except IndexError:
                pass
    print()
    load = input('Charger cette sauvegarde [Oui|Non]?')
    if load.lower() == 'o':
        if distrib == '1':
            action = 'cp /etc/conf.d/net.' + extension + ' /etc/conf.d/net'
            os.system(action)
        elif distrib == '2':
            action = 'cp /etc/network/interfaces.' + extension
            action += ' /etc/network/interfaces'
            os.system(action)
            action = 'cp /etc/resolv.conf.' + extension + ' /etc/resolv.conf'
            os.system(action)
            action = 'cp /etc/apt/apt.conf.' + extension + ' /etc/apt/apt.conf'
            os.system(action)
print()
print('Choisissez une interface a redemarrer')
pos = 0
for i in interface_list:
    print(i, '->', pos)
    pos += 1
while True:
    carte_index = input(': ')
    if carte_index.isdigit():
        if int(carte_index) >= 0 and int(carte_index) < len(interface_list):
            break
        else:
            print('Un chiffre à partir de 0 ou tapez Entrée')
    elif carte_index == '':
        carte_index = '0'
        break
    else:
        print('Un chiffre à partir de 0 ou tapez Entrée')
carte_reseau = interface_list[int(carte_index)]
if distrib == '1':
    os.system('/etc/init.d/net.{} stop'.format(carte_reseau))
    os.system('/etc/init.d/net.{} start'.format(carte_reseau))
elif distrib == '2':
    os.system('/etc/init.d/networking restart')
    
os.system('ping -c 3 google.com')
os.system('rm current_config')
os.system('rm sauvegarde')

print('Done!')



