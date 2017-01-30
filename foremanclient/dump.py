#!/usr/bin/python
# -*- coding: utf8 -*-


import sys
import logging
import log
import foremanclient
import yaml
from collections import OrderedDict
from pprint import pprint
from foreman.client import Foreman, ForemanException


import re
from cStringIO import StringIO

def _fix_dump(dump, indentSize=2):
    stream = StringIO(dump)
    out = StringIO()
    pat = re.compile('(\s*)([^:]*)(:*)')
    last = None

    prefix = 0
    for s in stream:
        indent, key, colon = pat.match(s).groups()
        if indent=="" and key[0]!= '-':
            prefix = 0
        if last:
            if len(last[0])==len(indent) and last[2]==':':
                if all([
                        not last[1].startswith('-'),
                        s.strip().startswith('-')
                        ]):
                    prefix += indentSize
        out.write(" "*prefix+s)
        last = indent, key, colon
    return out.getvalue()



class ForemanDump(foremanclient.ForemanBase):



    # dump functionality
    def dump(self):
        dumpdata = {}
        dumpdata['hosts']       = self.dump_hosts()
        dumpdata['hostgroup']   = self.dump_hostgroups()
        dumpdata['architecture'] = self.dump_arch()
        dumpdata['environment']  = self.dump_env()
        dumpdata['os']           = self.dump_os()
        dumpdata['model']        = self.dump_model()
        dumpdata['media']        = self.dump_media()
        dumpdata['domain']       = self.dump_domain()
        dumpdata['settings']     = self.dump_settings()
        dumpdata['subnet']       = self.dump_subnet()
        dumpdata['smart-proxy']  = self.dump_smartproxy()
        dumpdata['partition-table']  = self.dump_ptable()
        dumpdata['provisioning-template']  = self.dump_provisioningtpl()
        dumpdata['users']        = self.dump_users()
        dumpdata['users']        = self.dump_users()
        dumpdata['auth-source-ldap'] = self.dump_ldaps()
        dumpdata['usergroups'] = self.dump_usergroups()
        dumpdata['roles'] = self.dump_roles()

        # print the result
        fmyml = { 'foreman': dumpdata }

        def str_presenter(dumper, data):
            try:
                dlen = len(data.splitlines())
            except TypeError:
                return dumper.represent_scalar('tag:yaml.org,2002:str', data)
            if (dlen > 1):
                return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')

            return dumper.represent_scalar('tag:yaml.org,2002:str', data)

        yaml.add_representer(unicode, str_presenter)
        yaml.add_representer(str, str_presenter)

        yml = yaml.dump(fmyml, allow_unicode=True, default_flow_style=False )
        print( (yml) )


    def dump_hosts(self):
        ret = []
        all_hosts = self.fm.hosts.index(per_page=99999)['results']
        for host in all_hosts:
            host_tpl = {}
            for setting in host:
                value = host[setting]
                if value is None or value=='':
                    continue
                if (setting == "name"):
                    host_tpl['name'] = value
                elif (setting == "operatingsystem_name"):
                    host_tpl['os'] = value
                elif (setting == "environment_name"):
                    host_tpl['environment'] = value
                elif (setting == "architecture_name"):
                    host_tpl['architecture'] = value
                elif (setting == "medium_name"):
                    host_tpl['media'] = value
                elif (setting == "domain_name"):
                    host_tpl['domain'] = value
                elif (setting == "ptable_name"):
                    host_tpl['partition'] = value
                elif (setting == "model_name"):
                    host_tpl['model'] = value
                elif (setting == "hostgroup_name"):
                    host_tpl['hostgroup'] = value
            # host params
            try:
                hobj = self.fm.hostgroups.show(group['id'])
                if (len(hobj['parameters'])>0):
                    host_tpl['parameters'] = {}
                    for param in hobj['parameters']:
                        host_tpl['parameters'][param['name']] = param['value']
            except:
                pass

            ret.append(host_tpl)
        return ret


    def dump_hostgroups(self):
        ret = []
        all_groups = self.fm.hostgroups.index(per_page=99999)['results']
        for group in all_groups:
            grp_tpl = {}
            for setting in group:
                value = group[setting]
                if value is None or value=='':
                    continue
                if (setting == "name"):
                    grp_tpl['name'] = value
                elif (setting == "operatingsystem_name"):
                    grp_tpl['os'] = value
                elif (setting == "environment_name"):
                    grp_tpl['environment'] = value
                elif (setting == "architecture_name"):
                    grp_tpl['architecture'] = value
                elif (setting == "medium_name"):
                    grp_tpl['media'] = value
                elif (setting == "domain_name"):
                    grp_tpl['domain'] = value
                elif (setting == "ptable_name"):
                    grp_tpl['partition'] = value
                elif (setting == "subnet_name" ):
                    grp_tpl['subnet'] = value
            try:
                hobj = self.fm.hostgroups.show(group['id'])
                if (len(hobj['parameters'])>0):
                    grp_tpl['parameters'] = {}
                    for param in hobj['parameters']:
                        grp_tpl['parameters'][param['name']] = param['value']
            except:
                pass
            ret.append(grp_tpl)
        return ret


    def dump_arch(self):
        ret = []
        all_archs = self.fm.architectures.index(per_page=99999)['results']
        for arch in all_archs:
            ret.append({ 'name': arch['name'] })
        return ret


    def dump_env(self):
        ret = []
        all_envs = self.fm.environments.index(per_page=99999)['results']
        for env in all_envs:
            ret.append({ 'name': env['name'] })
        return ret


    def dump_os(self):
        ret = []
        all_os = self.fm.operatingsystems.index(per_page=99999)['results']
        for os in all_os:
            os_tpl = {}
            for setting in os:
                value = os[setting]
                if value is None or value=='':
                    continue
                if (setting == "name"):
                    os_tpl['name'] = value
                if (setting == "major"):
                    os_tpl['major'] = str(value)
                if (setting == "minor"):
                    os_tpl['minor'] = str(value)
                if (setting == "description"):
                    os_tpl['description'] = value
                if (setting == "release_name"):
                    os_tpl['release_name'] = value
                if (setting == "family"):
                    os_tpl['family'] = value
                if (setting == "password_hash"):
                    os_tpl['password-hash'] = value
            osobj = self.fm.operatingsystems.show(os['id'])
            # media
            if (len(osobj['media'])>0):
                os_tpl['media'] = []
                for media in osobj['media']:
                    os_tpl['media'].append(media['name'])
            # provisioning templates
            if (len(osobj['os_default_templates'])>0):
                os_tpl['provisioning-template'] = []
                for pt in osobj['os_default_templates']:
                    os_tpl['provisioning-template'].append(pt['provisioning_template_name'])
            # architectures
            if (len(osobj['architectures'])>0):
                os_tpl['architectures'] = []
                for pt in osobj['architectures']:
                    os_tpl['architectures'].append(pt['name'])
            # partition tables
            if (len(osobj['ptables'])>0):
                os_tpl['partition-table'] = []
                for pt in osobj['ptables']:
                    os_tpl['partition-table'].append(pt['name'])
            ret.append(os_tpl)
        return ret


    def dump_media(self):
        ret = []
        all_media = self.fm.media.index(per_page=99999)['results']
        mod_tpl = {}
        for medium in all_media:
            med_tpl = {}
            for setting in medium:
                value = medium[setting]
                if value is None or value=='':
                    continue
                if (setting == "name"):
                    med_tpl['name'] = value
                if (setting == "path"):
                    med_tpl['path'] = value
                if (setting == "os_family"):
                    med_tpl['os-family'] = value
            ret.append(med_tpl)
        return ret


    def dump_model(self):
        ret = []
        all_mods = self.fm.models.index(per_page=99999)['results']
        for model in all_mods:
            mod_tpl = {}
            for setting in model:
                value = model[setting]
                if value is None or value=='':
                    continue
                if (setting == "name"):
                    mod_tpl['name'] = value
                if (setting == "hardware_model"):
                    mod_tpl['hardware-model'] = value
                if (setting == "vendor_class"):
                    mod_tpl['vendor-class'] = value
                if (setting == "info"):
                    mod_tpl['info'] = value
            ret.append(mod_tpl)
        return ret


    def dump_domain(self):
        # TODO: dns-proxy
        ret = []
        all_doms = self.fm.domains.index(per_page=99999)['results']
        for dom in all_doms:
            dom_tpl = {}
            for setting in dom:
                value = dom[setting]
                if value is None or value=='':
                    continue
                if (setting == "name"):
                    dom_tpl['name'] = value
                if (setting == "fullname"):
                    dom_tpl['fullname'] = value
                if (setting == "fullname"):
                    dom_tpl['fullname'] = value
            # params
            domobj = self.fm.domains.show(dom['id'])
            if (len(domobj['parameters'])>0):
                dom_tpl['parameters'] = {}
                for param in domobj['parameters']:
                    dom_tpl['parameters'][param['name']] = param['value']
            ret.append(dom_tpl)
        return ret


    def dump_smartproxy(self):
        ret = []
        all_proxys = self.fm.smart_proxies.index(per_page=99999)['results']
        for proxy in all_proxys:
            sp_tpl = {}
            sp_tpl['name'] = proxy['name']
            sp_tpl['url'] = proxy['url']
            ret.append(sp_tpl)
        return ret


    def dump_subnet(self):
        ret = []
        wanted_keys = [
            "name",
            "network",
            "mask",
            "gateway",
            "ipam",
            "from",
            "to",
            "vlanid",
            "dns-primary",
            "dns-secondary",
            "boot-mode"
        ]
        all_subnets = self.fm.subnets.index(per_page=99999)['results']
        for subnet in all_subnets:
            subnet_tpl = {}
            dd = self.dict_dash(subnet)
            for setting in dd:
                if setting in wanted_keys:
                    value = dd[setting]
                    if value is None or value=='':
                        continue
                    subnet_tpl[setting] = value
            # tftp
            try:
                subnet_tpl['tftp-proxy'] = dd['tftp']['name']
            except TypeError:
                pass

            # dhcp
            try:
                subnet_tpl['dhcp-proxy'] = dd['dhcp']['name']
            except TypeError:
                pass

            # domains
            subnet_tpl['domain'] = []

            all_doms = self.fm.subnets.domains_index(dd['id'])
            for dom in all_doms['results']:
                subnet_tpl['domain'].append(dom['name'])

            ret.append(subnet_tpl)

        return ret


    def dump_settings(self):
        ret = []
        all_settings = self.fm.settings.index(per_page=99999)['results']
        for settings in all_settings:
            set_tpl = {}
            for setting in settings:
                value = settings[setting]
                if value is None or value=='':
                    continue
                if (setting == "name"):
                    set_tpl['name'] = value
                if (setting == "value"):
                    set_tpl['value'] = value
            # only in settings: allways print out value
            if set_tpl.get('value') is None:
                set_tpl['value'] = ""
            ret.append(set_tpl)
        return ret



    def dump_ptable(self):
        ret = []
        all_ptables = self.fm.ptables.index(per_page=99999)['results']
        for ptable in all_ptables:
            pt_tpl = {}
            for setting in ptable:
                value = ptable[setting]
                if value is None or value=='':
                    continue
                if (setting == "name"):
                    pt_tpl['name'] = value
                if (setting == "os_family"):
                    pt_tpl['os-family'] = value
                #if (setting == "template"):
                #    pt_tpl['layout'] = value
            # all other values need to be fetched from obj itself
            ptobj = self.fm.ptables.show(ptable['id'])
            try:
                pt_tpl['locked'] = ptobj['locked']
            except KeyError:
                pass
            try:
                pt_tpl['snippet'] = ptobj['snippet']
            except KeyError:
                pass
            try:
                pt_tpl['layout'] = str(ptobj['layout'])
                #print type(pt_tpl['layout'])
            except KeyError:
                pass
            ret.append(pt_tpl)

        return ret



    def dump_provisioningtpl(self):
        ret = []
        wanted_keys = [
            "snippet",
            "name",
            "template-kind-id",
            "locked",
            "audit-comment"
        ]
        all_provt = self.fm.provisioning_templates.index(per_page=99999)['results']

        for provt in all_provt:
            pt_tpl = {}
            dd = self.dict_dash(provt)
            for setting in dd:
                if setting in wanted_keys:
                    value = dd[setting]
                    if value is None or value=='':
                        continue
                    pt_tpl[setting] = value

            pto = self.fm.provisioning_templates.show(dd['id'])
            pt_tpl['template'] = (pto['template'])
            ret.append(pt_tpl)

        return ret


    def dump_users(self):
        ret = []
        wanted_keys = [
            "login",
            "firstname",
            "lastname",
            "locale",
            "mail",
            "timezone"
        ]
        all_users = self.fm.users.index(per_page=99999)['results']
        for user in all_users:
            usr_tpl = {}
            dd = self.dict_dash(user)
            for setting in dd:
                if setting in wanted_keys:
                    value = dd[setting]
                    if value is None or value=='':
                        continue
                    usr_tpl[setting] = value
            auths = dd['auth-source-name']
            if (auths == 'Internal'):
                auths = 'INTERNAL'
            usr_tpl['auth-source'] = auths
            ret.append(usr_tpl)

        return ret


    def dump_ldaps(self):
        ret = []
        wanted_keys = [
            "name",
            "host",
            "port",
            "base-dn",
            "ldap-filter",
            "tls",
            "onthefly-register",
            "usergroup-sync",
            "attr-firstname",
            "attr-lastname",
            "attr-login",
            "attr-mail",
            "attr-photo",
            "mail",
            "timezone"
        ]
        all_ldaps = self.fm.auth_source_ldaps.index(per_page=99999)['results']
        for ldaps in all_ldaps:
            dump_obj = self.filter_dump(ldaps, wanted_keys)
            ret.append(dump_obj)
        return ret


    def dump_usergroups(self):
        ret = []
        all_groups = self.fm.usergroups.index(per_page=99999)['results']
        for group in all_groups:
            gobj = {
                "name": group['name'],
                "admin": group['admin']
            }
            ret.append(gobj)
            # users
            uobj = self.fm.usergroups.users_index(group['id'])['results']
            if (len(uobj)>0):
                gobj['users'] = []
                for user in uobj:
                    add_u = { "name":user['login'] }
                    gobj['users'].append(add_u)
        return ret


    def dump_roles(self):
        ret = []
        all_roles = self.fm.roles.index(per_page=99999)['results']
        for role in all_roles:
            ret.append(
                self.filter_dump(role, ["name"] )
            )
        return ret
