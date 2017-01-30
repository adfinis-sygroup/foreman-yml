# foreman-yml

Make automated foreman configuration as easy as pie.

This script automatically resolves names so you can link templates, hosts, domains with only using their names. It's not required to know their ids beforehand.

## Installation
```
git clone https://github.com/adfinis-sygroup/foreman-yml
cd foreman-yml
sudo pip install .
```


## Usage

```
foreman-yml [import|dump|cleanup] /path/to/config.yaml
```


### Configuration

Root node of YAML is always `foreman`.
You can find an configuration example under `config/example.yml`

### Dump current configuration

foreman-yml supports dumping the whole configuration of a remote foreman instance
to sdout. Use `foreman-yml dump` for this feauture.

For dumping, provide an config file with auth settings:
```yaml
foreman:
  auth:
    url: "https://foreman.lab.local"
    user: username
    pass: password
```

Then run foreman-yml like this to dump configuration:
```
foreman-yml dump /path/to/config.yml > foreman_dump.yml
```


### Import settings into foreman

If no keyword or `import` is provided to `foreman-yml`, the script tries
to import settings provided by yaml-file.

```
foreman-yml /path/to/config.yml
foreman-yml dump /path/to/config.yml
```

The following config sections are supported:


#### Section `auth`
```yaml
auth:
  url: "https://foreman.lab.local"
  user: username
  pass: password
```
- __url__          URL of your foreman instance
- __user__         Username for connecting to the API. User should have administrative rights
- __pass__         Password for the User


#### Section `setting`
```yaml
setting:
  - name: entries_per_page
    value: 42
  - name:  safemode_render
    value: false
```
Key/Value pair for global foreman settings

- __name__          Key
- __value__         Value


#### Section `architecture`
```yaml
architecture:
  - name: x86_64
  - name: i386
```
- __name__          Architecture string (Example: 'x86_64')


#### Section `environment`
```yaml
environment:
  - name: production
  - name: development
  - name: staging
```
- __name__          Environment name


#### Section `smart-proxy`
```yaml
smart-proxy:
  - name: smproxy01
    url: "http://localhost:8000/"
```
- __name__         Smart proxy name
- __url__          Smart proxy url


#### Section `domain`
```yaml
domain:
  - name: lab.local
    fullname: lab.local is a test domain
    dns-proxy: smproxy01
    parameters:
      - name:  keyname
        value: keyvalue
```
- __name__          Domain name
- __fullname__      Detailed description     
- __dns-proxy__     DNS proxy for the domain. Maps to `smart-proxy.name`
- __parameters__    Extra parameters, key/value pair
 - __name__         Key
 - __value__        Value


#### Section `subnet`
```yaml
subnet:
  - name: lab
    network: 192.168.122.0
    mask: 255.255.255.0
    gateway: 192.168.122.1
    dns-primary: 192.168.122.1
    dns-secondary: 8.8.8.8
    ipam: DHCP
    from: 192.168.122.10
    to: 192.168.122.50
    vlanid:
    domain:
      - name: lab.local
    dhcp-proxy: Smart Proxy
    tftp-proxy: Smart Proxy
    dns-proxy:
    boot-mode: DHCP
```
- __name__                 Subnet name
- __network__              Network address
- __mask__                 Network Netmask
- __gateway__              Network gateway
- __dns-primary__          Primary DNS server
- __dns-secondary__        Secondary DNS server
- __ipam__                 IP Address auto suggestion mode for this subnet, valid values are "DHCP", "Internal DB", "None"
- __from__                 Starting IP Address for IP auto suggestion
- __to__                   Ending IP Address for IP auto suggestion
- __vlanid__               VLAN ID for this subnet
- __domain__               Domains in which this subnet is part
 - __name__                Domain name, maps to `domain.name`
- __dhcp-proxy__           DHCP Proxy to use within this subnet, maps to `smart-proxy.name`
- __tftp-proxy__           TFTP Proxy to use within this subnet, maps to `smart-proxy.name`
- __dns-proxy__            DNS Proxy to use within this subnet, maps to `smart-proxy.name`
- __boot-mode__            Default boot mode for interfaces assigned to this subnet, valid values are "Static", "DHCP"


#### Section `model`
```yaml
model:
  - name: libvirt
    info: Virtual Machine
    vendor-class: vmware
    hardware-model: esxi6
```
- __name__                 Model name
- __info__                 Detailed description
- __vendor-class__         Hardware vendor
- __hardware-model__       Hardware model


#### Section `medium`
```yaml
medium:
  - name: Ubuntu Mirror
    path: "http://archive.ubuntu.com/ubuntu"
    os-family: Debian

```
- __name__                 Model name
- __path__                 The path to the medium, can be a URL or a valid NFS server (exclusive of the architecture)
- __os-family__            Operating system family, available values: AIX, Altlinux, Archlinux, Coreos, Debian, Freebsd, Gentoo, Junos, NXOS, Redhat, Solaris, Suse, Windows


#### Section `partition-table`
```yaml
partition-table:
  - name: Ubuntu Default
    os-family: Debian
    audit-comment: initial import
    layout: |
            #!ipxe
            <%#
            kind: iPXE
            name: RLC iPXE
            oses:
            - Ubuntu 14.04
            %>
            [...]
    locked: false
```
- __name__                  Partition table name
- __os-family__             Operating system family, available values: AIX, Altlinux, Archlinux, Coreos, Debian, Freebsd, Gentoo, Junos, NXOS, Redhat, Solaris, Suse, Windows
- __audit-comment__         Comment for the audit log
- __layout__                Partition layout
- __locked__                Whether or not the template is locked for editing


#### Section `provisioning-template`
```yaml
provisioning-template:
    name: Ubuntu Preseed
    template: |
               <%#
              kind: provision
              name: Ubuntu Preseed
              oses:
              - Debian 8.
              %>
              [...]
    snippet: false
    audit-comment: initial import
    template-kind-id: 3
    template-combination-attribute:
    os:
      - name: Debian 8
    locked: false
```
- __name__                  Partition table name
- __template__              The provisioning template itself
- __snippet__               Set to true if template is a snippet only
- __audit-comment__         Comment for the audit log
- __template_kind_id__      Template kind id
- __os__                    
 - __name__                 Operating system name, maps to `os.name`
- __locked__                Whether or not the template is locked for editing


#### Section `os`
```yaml
os:
  - name: Ubuntu
    major: 14
    minor: 4
    description: Ubuntu 14.04 LTS
    family: Debian
    release-name: trusty
    password-hash: SHA512
    architecture:
      - name: x86_64
    provisioning-template:
      - name: Ubuntu PXE
      - name: Ubuntu Preseed
    medium:
      - name: Ubuntu Mirror
    partition-table:
      - name: Ubuntu Default
    parameters:
      version: "14.04"
      codename: "trusty"
```
- __name__                  Operating system table name
- __major__                 The provisioning template itself
- __minor__                 Set to true if template is a snippet only
- __description__           Comment for the audit log
- __family__                Operating system family, available values: AIX, Altlinux, Archlinux, Coreos, Debian, Freebsd, Gentoo, Junos, NXOS, Redhat, Solaris, Suse, Windows
- __release-name__          OS release name
- __password-hash__         Root password hash function to use, one of MD5, SHA256, SHA512, Base64
- __architecture__        
  - __name__                Architecture name, maps to `architecture.name`
- __provisioning-template__
  - __name__                Provisioning template name, maps to `provisioning-template.name`
- __medium__
  - __ name__               Medium name, maps to `medium.name`
- __partition-table__
  - __name__                Ptable name, maps to `partition-table.name`
- __parameters__
  - __ key__                Additional OS settings in format 'keyname': 'keyvalue'


#### Section `hostgroup`
```yaml
hostgroup:
  - name: switzerland
    parent:
    environment: production
    os: Ubuntu 14.04 LTS
    architecture: x86_64
    medium: Ubuntu Mirror
    partition-table: Ubuntu Default
    subnet: lab
    domain: lab.local
    parameters:
      - keyname:  keyvalue

```
- __name__                  Hostgroup name
- __parent__                Parent hostgroup
- __environment__           Environment name, maps to `environment.name`
- __os__                    Operating system name, maps to `os.name`
- __architecture__          Architecture name, maps to `architecture.name`
- __medium__                Media name, maps to `medium.name`
- __partition-table__       Ptable name, maps to `partition-table.name`
- __subnet__                Subnet name, maps to `subnet.name`
- __domain__                Domain name, maps to `domain.name`
- __parameters__            Dict of params
  -__keyname__              Value of param

#### Section `host`
```yaml
host:
  - name: testhost
    domain: lab.local
    architecture: x86_64
    hostgroup: switzerland
    environment: production
    os: Ubuntu 14.04 LTS
    media: Ubuntu Mirror
    partition: Ubuntu Default
    model: VMWare VM
    mac: 00:11:22:33:44:55
    root-pass: supersecret42
    parameters:
      env: prod
      kernel_params: quiet
```
- __name__                  Host name
- __domain__                Domain name, maps to `domain.name`
- __architecture__          Architecture name, maps to `architecture.name`
- __hostgroup__             Hostgroup name, maps to `hostgroup.name`
- __environment__           Environment name, maps to `environment.name`
- __os__                    Operating system name, maps to `os.name`
- __media__                 Media name, maps to `medium.name`
- __partition__             Ptable name, maps to `partition.name`
- __model__                 Hardware model name, maps to `model.name`
- __mac__                   MAC address
- __root-pass__             Root password
- __parameters__            Dict of params
  - __keyname__              Value of param

#### Section `roles`
```yaml
roles:
  - name: testrole
    permissions:
      architecture:
        - view_architectures
        - edit_architectures
      compute_resources:
        - view_compute_resources
        - create_compute_resources
        - destroy_compute_resources
```
- __name__                  Role name
- __permissions__                     
  - __groupname__           Name of permission group (not applied to foreman), only for clarity
    - __permission_name__   Permission name, maps to `permission.name`
    - __permission_name__   Permission name, maps to `permission.name`
    - __permission_name__   Permission name, maps to `permission.name`
    - ...                   ...


#### Section `users`
```yaml
users:
  - login: testhaaaans
    password: schmetterling42
    mail: haaaans@example.com
    auth-source: ldap-is-not-web-scale
    firstname: Test
    lastname: Haaaaaans
    admin: true
    timezone: UTC
    locale: en
```
- __login__                  User login
- __password__               Password of user
- __auth-source__            Name of auth source or 'INTERNAL' for foreman-own auth source
- __firstname__              First name of user
- __lastname__               Last name of user
- __admin__                  If `true`, user will be created with admin permissions
- __timezone__               Timezone for the user
- __locale__                 WebUI locale for the user


#### Section `usergroups`
```yaml
usergroups:
  - name: api-test2
    admin: false
    users:
      - name: foo
      - name: burlson
    groups:
      - name: api-testgroup
    ext-usergroups:
      - name: foremangroup
        auth-source-ldap: ldap-is-not-web-scale
    roles:
      - name: foo
```
- __name__                  Usergroup name
- __admin__                 If set to true or 1, group is has admin permissions
- __users__                 List of users                
  - __name__                Username, maps to `users.name`
- __groups__                List of groups
  - __name__                Groupname, maps to `usergroups.name`
- __ext-usergroups__        List of external usergroups
  - __name__                Name of the external usergroup
  - __auth-source-ldap__    Name of the external auth source, maps to  `auth-source-ldap.name`
- __roles__                 List of roles
  - __name__                Role name, maps to `role.name`


#### Section `auth-source-ldap`
```yaml
auth-source-ldap:
  - name: ldap-is-not-web-scale
    host: 10.11.12.13
    port: 389
    account: uid=binduser,cn=users,dc=test,dc=example,dc=com
    account-password: 123qwe
    base-dn: dc=test,dc=example,dc=com
    attr-login: uid
    attr-firstname: firstName
    attr-lastname: lastName
    attr-mail: mail
    attr-photo: picture
    onthefly-register: false
    usergroup-sync: false
    tls: false
    groups-base: cn=groups,dc=test,dc=example,dc=com
    ldap-filter:
    server-type: posix
```
- __name__                    Name of the authsource
- __host__                    LDAP host
- __port__                    Server port
- __account__                 Bind account user
- __account-password__        Bind account password
- __base-dn__                 LDAP Base DN
- __attr-login__              LDAP attribute for username, required if onthefly-register is true
- __attr-firstname__          LDAP attribute for first name, required if onthefly-register is true
- __attr-lastname__           LDAP attribute for last name, required if onthefly-register is true
- __attr-mail__               LDAP attribute for mail, required if onthefly-register is true
- __attr-photo__              LDAP attribute for user photo
- __onthefly-register__       Register users on the fly if `true` or `1`
- __usergroup-sync__          Sync external user groups on login if `true` or `1`
- __tls__                     If `true` or `1`, use SSL to connect to the server
- __groups-base__             groups base DN
- __ldap-filter__             LDAP filter
- __server-type__             LDAP Server type, valid are `free_ipa`, `active_directory` and `posix`



### Cleanup (delete) settings

If the keyword `cleanup` is provided to foreman-yml, it will try to delete
items specified by its name.

```
foreman-yml cleanup /path/to/config.yml
```

#### Section `cleanup-[architecture|compute-profile|partition-table|provisioning-template]`
```yaml
cleanup-[architecture|compute-profile|partition-table|provisioning-template]:
  - name: foo
  - name: bar
```
Removes specified objects, mapping to object.name
- __name__                  architecture|compute-profile|partition-table|provisioning-template name to delete





## Hacking
```
virtualenv --system-site-packages venv-dev
source venv-dev/bin/activate
pip install -e .
```

## Future
- Dump current settings
- Better documentaion

## License
GNU GENERAL PUBLIC LICENSE Version 3
