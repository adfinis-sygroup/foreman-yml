#!/usr/bin/python
# -*- coding: utf8 -*-


import sys
import logging
import log
from foreman.client import Foreman
from pprint import pprint
from voluptuous import Schema, Required, All, Length, Range, Optional, Any, MultipleInvalid



class validator:

    def __init__(self):

        self.arch = Schema({
            Required('name'):                           All(str),
        })

        self.domain = Schema({
            Required('name'):                           All(str),
            Optional('fullname'):                       Any(str, None),
            Optional('dns-proxy'):                      Any(str, None),
            Optional('parameters'):                     Any(dict, None)
        })

        self.enviroment = Schema({
            Required('name'):                           All(str)
        })

        self.model = Schema({
            Required('name'):                           All(str),
            Optional('info'):                           Any(str, None),
            Optional('vendor-class'):                   Any(str, None),
            Optional('hardware-model'):                 Any(str, None)
        })

        self.medium = Schema({
            Required('name'):                           All(str),
            Required('path'):                           All(str),
            Required('os-family'):                      All(str),
        })

        self.ptable = Schema({
            Required('name'):                           All(str),
            Required('layout'):                         All(str),
            Optional('snippet'):                        Any(bool,None),
            Optional('os-family'):                      Any(str,None),
            Optional('audit-comment'):                  Any(str,None),
            Optional('locked'):                         Any(bool,None),
        })

        self.provt = Schema({
            Required('name'):                           All(str),
            Required('template'):                       All(str),
            Optional('snippet'):                        Any(bool,None),
            Optional('audit-comment'):                  Any(str,None),
            Optional('template-kind-id'):               Any(int,None),
            Optional('template-combination-attribute'): Any(int,None),
            Optional('locked'):                         Any(bool,None),
            Optional('os'):                             Any(None, Schema([{
                Required('name'):                       All(str)
            }]))
        })

        self.os = Schema({
            Required('name'):                           All(str),
            Required('major'):                          Any(str,int),
            Required('minor'):                          Any(str,int),
            Optional('description'):                    Any(str,None),
            Optional('family'):                         Any(str,None),
            Optional('release-name'):                   Any(str,None),
            Optional('parameters'):                     Any(dict, None),
            Optional('password-hash'):                  Any('MD5', 'SHA256', 'SHA512', 'Base64', None ),
            Optional('architecture'):                   Any(None, Schema([{
                Required('name'):                       All(str)
            }])),
            Optional('provisioning-template'):          Any(None, Schema([{
                Required('name'):                       All(str)
            }])),
            Optional('medium'):                         Any(None, Schema([{
                Required('name'):                       All(str)
            }])),
            Optional('partition-table'):                Any(None, Schema([{
                Required('name'):                       All(str)
            }]))
        })

        self.host = Schema({
            Required('name'):                           All(str),
            Required('template'):                       All(str),
            Optional('snippet'):                        Any(bool, None),
            Optional('audit-comment'):                  Any(str, None),
            Optional('mac'):                            Any(str, None),
            Optional('template-kind-id'):               Any(int, None),
            Optional('template-combination-attribute'): Any(int, None),
            Optional('locked'):                         Any(bool, None),
            Optional('hostgroup'):                      Any(str, None),
            Optional('parameters'):                     Any(dict, None),
            Optional('os'):                             Any(None, Schema([{
                Required('name'):                       All(str)
            }]))
        })

        self.hostgroup = Schema({
            Required('name'):                           All(str),
            Optional('parent'):                         Any(str,None),
            Optional('environment'):                    Any(str,None),
            Optional('os'):                             Any(str,None),
            Optional('architecture'):                   Any(str,None),
            Optional('medium'):                         Any(str,None),
            Optional('partition-table'):                Any(str,None),
            Optional('domain'):                         Any(str,None),
            Optional('subnet'):                         Any(str,None),
        })

        self.smartproxy = Schema({
            Required('name'):                           All(str),
            Required('url'):                            All(str),
        })

        self.setting = Schema({
            Required('name'):                           All(str),
            Optional('value'):                          Any(list, str, bool, int, None),
        })

        self.subnet =  Schema({
            Required('name'):                           All(str),
            Required('network'):                        All(str),
            Required('mask'):                           All(str),
            Optional('gateway'):                        Any(str, None),
            Optional('dns-primary'):                    Any(str, None),
            Optional('dns-secondary'):                  Any(str, None),
            Optional('ipam'):                           Any('DHCP', 'Internal DB', 'None', None),
            Optional('from'):                           Any(str, None),
            Optional('to'):                             Any(str, None),
            Optional('vlanid'):                         Any(str, int, None),
            Optional('domain'):                         Any(None, Schema([{
                Required('name'):                       All(str)
            }])),
            Optional('dhcp-proxy'):                     Any(str, None),
            Optional('tftp-proxy'):                     Any(str, None),
            Optional('dns-proxy'):                      Any(str, None),
            Optional('boot-mode'):                      Any('Static', 'DHCP', None),
        })

        self.cleanup_arch = Schema({
            Required('name'):                           All(str)
        })

        self.cleanup_computeprfl = Schema({
            Required('name'):                           All(str)
        })

        self.cleanup_medium = Schema({
            Required('name'):                           All(str)
        })

        self.cleanup_ptable = Schema({
            Required('name'):                           All(str)
        })

        self.cleanup_provt = Schema({
            Required('name'):                           All(str)
        })



class foreman:

    def __init__(self, config, loglevel=logging.INFO):
        logging.basicConfig(level=loglevel)
        self.config = config['foreman']
        self.loglevel = loglevel
        self.validator = validator()



    def get_config_section(self, section):
        try:
            cfg = self.config[section]
        except:
            cfg = []
        return cfg



    def connect(self):
        try:
            logging.disable(logging.WARNING)
            self.fm = Foreman(self.config['auth']['url'], (self.config['auth']['user'], self.config['auth']['pass']), api_version=2, use_cache=False, strict_cache=False)
            # this is nescesary for detecting faulty credentials in yaml
            self.fm.architectures.index()
            logging.disable(self.loglevel-1)
        except:
            log.log(log.LOG_ERROR, "Cannot connect to Foreman-API")
            sys.exit(1)



    def process_cleanup_arch(self):
        log.log(log.LOG_INFO, "Processing Cleanup of Architectures")
        for arch in self.get_config_section('cleanup-architecture'):
            try:
                self.validator.cleanup_arch(arch)
            except MultipleInvalid as e:
                log.log(log.LOG_WARN, "Cannot delete Architecture '{0}': YAML validation Error: {1}".format(arch['name'], e))
                continue

            try:
                self.fm.architectures.show(arch['name'])['id']
                log.log(log.LOG_INFO, "Delete Architecture '{0}'".format(arch['name']))

                self.fm.architectures.destroy( arch['name'] )
            except:
                log.log(log.LOG_WARN, "Architecture '{0}' already absent.".format(arch['name']))



    def process_cleanup_computeprfl(self):
        log.log(log.LOG_INFO, "Processing Cleanup of Compute profiles")
        for computeprfl in self.get_config_section('cleanup-compute-profile'):
            try:
                self.validator.cleanup_computeprfl(computeprfl)
            except MultipleInvalid as e:
                log.log(log.LOG_WARN, "Cannot delete Compute profile '{0}': YAML validation Error: {1}".format(computeprfl['name'], e))
                continue

            try:
                self.fm.compute_profiles.show(computeprfl['name'])['id']
                log.log(log.LOG_INFO, "Delete Compute profile '{0}'".format(computeprfl['name']))

                self.fm.compute_profiles.destroy( computeprfl['name'] )
            except:
                log.log(log.LOG_WARN, "Compute profile '{0}' already absent.".format(computeprfl['name']))



    def process_cleanup_medium(self):
        log.log(log.LOG_INFO, "Processing Cleanup of Media")
        medialist = self.fm.media.index(per_page=99999)['results']
        for medium in self.get_config_section('cleanup-medium'):
            try:
                self.validator.cleanup_medium(medium)
            except MultipleInvalid as e:
                log.log(log.LOG_WARN, "Cannot delete Medium '{0}': YAML validation Error: {1}".format(medium['name'], e))
                continue

            medium_deleted = False
            # fm.media.show(name) does not work, we need to iterate over fm.media.index()
            for mediac in medialist:
                if (mediac['name'] == medium['name']):
                    medium_deleted = True
                    log.log(log.LOG_INFO, "Delete Medium '{0}'".format(medium['name']))

                    self.fm.media.destroy( medium['name'] )
                    continue
            if not medium_deleted:
                log.log(log.LOG_WARN, "Medium '{0}' already absent.".format(medium['name']))



    def process_cleanup_ptable(self):
        log.log(log.LOG_INFO, "Processing Cleanup of Partition Tables")
        for ptable in self.get_config_section('cleanup-partition-table'):
            try:
                self.validator.cleanup_ptable(ptable)
            except MultipleInvalid as e:
                log.log(log.LOG_WARN, "Cannot delete Partition Table '{0}': YAML validation Error: {1}".format(ptable['name'], e))
                continue

            try:
                self.fm.ptables.show(ptable['name'])['id']
                log.log(log.LOG_INFO, "Delete Partition Table '{0}'".format(ptable['name']))

                self.fm.ptables.destroy( ptable['name'] )
            except:
                log.log(log.LOG_WARN, "Partition Table '{0}' already absent.".format(ptable['name']))



    def process_cleanup_provisioningtpl(self):
        log.log(log.LOG_INFO, "Processing Cleanup of Provisioning Templates")
        ptlist = self.fm.provisioning_templates.index(per_page=99999)['results']
        for pt in self.get_config_section('cleanup-provisioning-template'):
            try:
                self.validator.cleanup_provt(pt)
            except MultipleInvalid as e:
                log.log(log.LOG_WARN, "Cannot delete Provisioning Template '{0}': YAML validation Error: {1}".format(pt['name'], e))
                continue

            # fm.provisioning_templates.show(name) does not work as expected, we need to iterate over fm.provisioning_templates.index()
            pt_deleted = False
            for ptc in ptlist:
                if (ptc['name'] == pt['name']):
                    pt_deleted = True
                    log.log(log.LOG_INFO, "Delete Provisioning Template '{0}'".format(pt['name']))

                    self.fm.provisioning_templates.destroy( pt['name'] )
                    continue
            if not pt_deleted:
                log.log(log.LOG_WARN, "Provisioning Template '{0}' already absent.".format(pt['name']))



    def process_config_arch(self):
        log.log(log.LOG_INFO, "Processing Architectures")
        for arch in self.get_config_section('architecture'):
            try:
                self.validator.arch(arch)
            except MultipleInvalid as e:
                log.log(log.LOG_WARN, "Cannot create Architecture '{0}': YAML validation Error: {1}".format(arch['name'], e))
                continue

            try:
                arch_id = self.fm.architectures.show(arch['name'])['id']
                log.log(log.LOG_DEBUG, "Architecture '{0}' (id={1}) already present.".format(arch['name'], arch_id))
            except:
                log.log(log.LOG_INFO, "Create Architecture '{0}'".format(arch['name']))
                self.fm.architectures.create( architecture = { 'name': arch['name'] } )



    def process_config_domain(self):
        log.log(log.LOG_INFO, "Processing Domains")
        for domain in self.get_config_section('domain'):
            try:
                self.validator.domain(domain)
            except MultipleInvalid as e:
                log.log(log.LOG_WARN, "Cannot create Domain '{0}': YAML validation Error: {1}".format(domain['name'], e))
                continue
            try:
                dom_id = self.fm.domains.show(domain['name'])['id']
                log.log(log.LOG_DEBUG, "Domain '{0}' (id={1}) already present.".format(domain['name'], dom_id))
            except:
                dns_proxy_id = False
                try:
                    dns_proxy_id = self.fm.smart_proxies.show(domain['dns-proxy'])['id']
                except:
                    log.log(log.LOG_WARN, "Cannot get ID of DNS Smart Proxy '{0}', skipping".format(domain['dns-proxy']))

                log.log(log.LOG_INFO, "Create Domain '{0}'".format(domain['name']))
                dom_params = []
                if (domain['parameters']):
                    for name,value in domain['parameters'].iteritems():
                        p = {
                            'name':     name,
                            'value':    value
                        }
                        dom_params.append(p)
                dom_tpl = {
                    'name': domain['name'],
                    'fullname': domain['fullname'],
                }
                fixdom = {
                    'domain_parameters_attributes': dom_params
                }

                if dns_proxy_id: dom_tpl['dns_id'] = dns_proxy_id

                domo = self.fm.domains.create( domain = dom_tpl )
                if dom_params:
                    self.fm.domains.update(fixdom, domo['id'])



    def process_config_enviroment(self):
        log.log(log.LOG_INFO, "Processing Environments")
        envlist = self.fm.environments.index(per_page=99999)['results']
        for env in self.get_config_section('environment'):
            try:
                self.validator.enviroment(env)
            except MultipleInvalid as e:
                log.log(log.LOG_WARN, "Cannot create Environment '{0}': YAML validation Error: {1}".format(env['name'], e))
                continue

            env_id = False
            # fm.media.show(name) does not work, we need to iterate over fm.media.index()
            for envc in envlist:
                if (env['name'] == envc['name']):
                    env_id = envc['id']
                    log.log(log.LOG_DEBUG, "Environment '{0}' (id={1}) already present.".format(env['name'], env_id))
                    continue
            if not env_id:
                log.log(log.LOG_INFO, "Create Environment '{0}'".format(env['name']))
                self.fm.environments.create( environment = { 'name': env['name'] } )



    def process_config_model(self):
        log.log(log.LOG_INFO, "Processing Models")
        for model in self.get_config_section('model'):
            try:
                self.validator.model(model)
            except MultipleInvalid as e:
                log.log(log.LOG_WARN, "Cannot create Model '{0}': YAML validation Error: {1}".format(model['name'], e))
                continue
            try:
                model_id = self.fm.models.show(model['name'])['id']
                log.log(log.LOG_DEBUG, "Model '{0}' (id={1}) already present.".format(model['name'], model_id))
            except:
                log.log(log.LOG_INFO, "Create Model '{0}'".format(model['name']))
                model_tpl = {
                    'name':             model['name'],
                    'info':             model['info'],
                    'vendor_class':     model['vendor-class'],
                    'hardware_model':   model['hardware-model']
                }
                self.fm.models.create( model = model_tpl )



    def process_config_medium(self):
        log.log(log.LOG_INFO, "Processing Media")
        medialist = self.fm.media.index(per_page=99999)['results']
        for medium in self.get_config_section('medium'):
            try:
                self.validator.medium(medium)
            except MultipleInvalid as e:
                log.log(log.LOG_WARN, "Cannot create Media '{0}': YAML validation Error: {1}".format(medium['name'], e))
                continue

            medium_id = False
            # fm.media.show(name) does not work, we need to iterate over fm.media.index()
            for mediac in medialist:
                if (mediac['name'] == medium['name']):
                    medium_id = mediac['id']
                    log.log(log.LOG_DEBUG, "Medium '{0}' (id={1}) already present.".format(medium['name'], medium_id))
            if not medium_id:
                log.log(log.LOG_INFO, "Create Medium '{0}'".format(medium['name']))
                medium_tpl = {
                    'name':        medium['name'],
                    'path':        medium['path'],
                    'os_family':   medium['os-family']
                }
                self.fm.media.create( medium = medium_tpl )



    def process_config_settings(self):
        log.log(log.LOG_INFO, "Processing Foreman Settings")
        for setting in self.get_config_section('setting'):
            try:
                self.validator.setting(setting)
            except MultipleInvalid as e:
                log.log(log.LOG_WARN, "Cannot update Setting '{0}': YAML validation Error: {1}".format(setting['name'], e))
                continue

            setting_id = False
            try:
                setting_id = self.fm.settings.show(setting['name'])['id']
            except:
                log.log(log.LOG_WARN, "Cannot get ID of Setting '{0}', skipping".format(setting['name']))

            setting_tpl = {
                'value':            setting['value']
            }

            if setting_id:
                log.log(log.LOG_INFO, "Update Setting '{0}'".format(setting['name']))
                self.fm.settings.update(setting_tpl, setting_id)



    def process_config_smartproxy(self):
        log.log(log.LOG_INFO, "Processing Smart Proxies")
        for proxy in self.get_config_section('smart-proxy'):
            try:
                proxy_id = self.fm.smart_proxies.show(proxy['name'])['id']
                log.log(log.LOG_DEBUG, "Proxy '{0}' (id={1}) already present.".format(proxy['name'], proxy_id))
            except:
                log.log(log.LOG_INFO, "Create Smart Proxy '{0}'".format(proxy['name']))
                proxy_tpl = {
                    'name': proxy['name'],
                    'url': proxy['url'],
                }
                try:
                    self.fm.smart_proxies.create( smart_proxy = proxy_tpl )
                except:
                    log.log(log.LOG_WARN, "Cannot create Smart Proxy '{0}'. Is the Proxy online? ".format(proxy['name']))



    def process_config_subnet(self):
        log.log(log.LOG_INFO, "Processing Subnets")
        for subnet in self.get_config_section('subnet'):
            try:
                self.validator.subnet(subnet)
            except MultipleInvalid as e:
                log.log(log.LOG_WARN, "Cannot create Subnet '{0}': YAML validation Error: {1}".format(subnet['name'], e))
                continue
            try:
                subnet_id = self.fm.subnets.show(subnet['name'])['id']
                log.log(log.LOG_DEBUG, "Subnet '{0}' (id={1}) already present.".format(subnet['name'], subnet_id))
            except:
                # get domain_ids
                add_domain = []
                for subnet_domain in subnet['domain']:
                    try:
                        dom_id = self.fm.domains.show(subnet_domain['name'])['id']
                        add_domain.append(dom_id)
                    except:
                        log.log(log.LOG_WARN, "Cannot get ID of Domain '{0}', skipping".format(subnet_domain['name']))

                # get dhcp_proxy_id
                dhcp_proxy_id = False
                try:
                    dhcp_proxy_id = self.fm.smart_proxies.show(subnet['dhcp-proxy'])['id']
                except:
                    log.log(log.LOG_WARN, "Cannot get ID of DHCP Smart Proxy '{0}', skipping".format(subnet['dhcp-proxy']))

                # get tftp_proxy_id
                tftp_proxy_id = False
                try:
                    tftp_proxy_id = self.fm.smart_proxies.show(subnet['tftp-proxy'])['id']
                except:
                    log.log(log.LOG_WARN, "Cannot get ID of TFTP Smart Proxy '{0}', skipping".format(subnet['tftp-proxy']))

                # get dns_proxy_id
                dns_proxy_id = False
                try:
                    dns_proxy_id = self.fm.smart_proxies.show(subnet['dns-proxy'])['id']
                except:
                    log.log(log.LOG_WARN, "Cannot get ID of DNS Smart Proxy '{0}', skipping".format(subnet['dns-proxy']))

                log.log(log.LOG_INFO, "Create Subnet '{0}'".format(subnet['name']))
                subnet_tpl = {
                    'name':             subnet['name'],
                    'network':          subnet['network'],
                    'mask':             subnet['mask'],
                    'gateway':          subnet['gateway'],
                    'dns_primary':      subnet['dns-primary'],
                    'dns_secondary':    subnet['dns-secondary'],
                    'ipam':             subnet['ipam'],
                    'from':             subnet['from'],
                    'to':               subnet['to'],
                    'vlanid':           subnet['vlanid'],
                    'boot_mode':        subnet['boot-mode']
                }

                if add_domain: subnet_tpl['domain_ids'] = add_domain
                if dhcp_proxy_id: subnet_tpl['dhcp_id'] = dhcp_proxy_id
                if tftp_proxy_id: subnet_tpl['tftp_id'] = tftp_proxy_id
                if dns_proxy_id: subnet_tpl['dns_id'] = dns_proxy_id

                self.fm.subnets.create(subnet=subnet_tpl)



    def process_config_ptable(self):
        log.log(log.LOG_INFO, "Processing Partition Tables")
        for ptable in self.get_config_section('partition-table'):
            try:
                self.validator.ptable(ptable)
            except MultipleInvalid as e:
                log.log(log.LOG_WARN, "Cannot create Partition Table '{0}': YAML validation Error: {1}".format(ptable['name'], e))
                continue
            try:
                ptable_id = self.fm.ptables.show(ptable['name'])['id']
                log.log(log.LOG_DEBUG, "Partition Table '{0}' (id={1}) already present.".format(ptable['name'], ptable_id))
            except:
                log.log(log.LOG_INFO, "Create Partition Table '{0}'".format(ptable['name']))
                ptable_tpl = {
                    'name':             ptable['name'],
                    'layout':           ptable['layout'],
                    'snippet':          ptable['snippet'],
                    'audit_comment':    ptable['audit-comment'],
                    'locked':           ptable['locked'],
                    'os_family':        ptable['os-family']
                }
                self.fm.ptables.create( ptable = ptable_tpl )



    def process_config_os(self):
        log.log(log.LOG_INFO, "Processing Operating Systems")
        for operatingsystem in self.get_config_section('os'):
            try:
                self.validator.os(operatingsystem)
            except MultipleInvalid as e:
                log.log(log.LOG_WARN, "Cannot create Operating System '{0}': YAML validation Error: {1}".format(operatingsystem['name'], e))
                continue
            try:
                os_id = self.fm.operatingsystems.show(operatingsystem['description'])['id']
                log.log(log.LOG_DEBUG, "Operating System '{0}' (id={1}) already present.".format(operatingsystem['name'], os_id))
            except:
                log.log(log.LOG_INFO, "Create Operating System '{0}'".format(operatingsystem['name']))
                os_tpl = {
                    'name':             operatingsystem['name'],
                    'description':      operatingsystem['description'],
                    'major':            operatingsystem['major'],
                    'minor':            operatingsystem['minor'],
                    'family':           operatingsystem['family'],
                    'release_name':     operatingsystem['release-name'],
                    'password_hash':    operatingsystem['password-hash']
                }
                os_obj = self.fm.operatingsystems.create(operatingsystem=os_tpl)

                #  host_params
                if operatingsystem['parameters']:
                    for name,value in operatingsystem['parameters'].iteritems():
                        p = {
                            'name':     name,
                            'value':    value
                        }
                        try:
                            self.fm.operatingsystems.parameters_create(os_obj['id'], p )
                        except:
                            log.log(log.LOG_WARN, "Error adding host parameter '{0}'".format(name))


    def process_config_provisioningtpl(self):
        log.log(log.LOG_INFO, "Processing Provisioning Templates")
        # fm.provisioning_templates.show(name) does not work as expected, we need to iterate over fm.provisioning_templates.index()
        ptlist = self.fm.provisioning_templates.index(per_page=99999)['results']
        for pt in self.get_config_section('provisioning-template'):
            try:
                self.validator.provt(pt)
            except MultipleInvalid as e:
                log.log(log.LOG_WARN, "Cannot create Provisioning Template '{0}': YAML validation Error: {1}".format(pt['name'], e))
                continue

            pt_id = False
            for ptc in ptlist:
                if (ptc['name'] == pt['name']):
                    pt_id = ptc['id']
                    log.log(log.LOG_DEBUG, "Provisioning Template '{0}' (id={1}) already present.".format(pt['name'], pt_id))
            if not pt_id:
                log.log(log.LOG_INFO, "Create Provisioning Template '{0}'".format(pt['name']))
                pt_tpl = {
                    'name':             pt['name'],
                    'template':         pt['template'],
                    'snippet':          pt['snippet'],
                    'audit_comment':    pt['audit-comment'],
                    'template_kind_id': pt['template-kind-id'],
                    'locked':           pt['locked']
                }
                os_ids = []
                for osc in pt['os']:
                    try:
                        os_id = self.fm.operatingsystems.show(osc['name'])['id']
                        os_ids.append(os_id)
                    except:
                        log.log(log.LOG_WARN, "Cannot link OS '{0}' to Provisioning Template '{1}'".format(osc['name'],pt['name']))
                pt_tpl = {
                    'name':                 pt['name'],
                    'template':             pt['template'],
                    'snippet':              pt['snippet'],
                    'audit_comment':        pt['audit-comment'],
                    'template_kind_id':     pt['template-kind-id'],
                    'locked':               pt['locked'],
                    'operatingsystem_ids':  os_ids
                }
                prtes = self.fm.provisioning_templates.create(provisioning_template=pt_tpl)



    def process_config_os_link(self):
        #log.log(log.LOG_INFO, "Link Operating System Items (Provisioning Templates, Media, Partition Tables)")
        for operatingsystem in self.get_config_section('os'):
            try:
                self.validator.os(operatingsystem)
            except MultipleInvalid as e:
                log.log(log.LOG_WARN, "Cannot update Operating System '{0}': YAML validation Error: {1}".format(operatingsystem['name'], e))
                continue

            os_obj = False
            try:
                os_obj = self.fm.operatingsystems.show(operatingsystem['description'])
            except:
                log.log(log.LOG_WARN, "Cannot get ID of Operating System '{0}', skipping".format(operatingsystem['name']))
            if os_obj:

                # link Partition Tables
                add_pt = []
                for os_ptable in operatingsystem['partition-table']:
                    try:
                        ptable_id = self.fm.ptables.show(os_ptable['name'])['id']
                        add_pt.append({'id': ptable_id})
                    except:
                        log.log(log.LOG_WARN, "Cannot get ID of Partition Table '{0}', skipping".format(os_ptable['name']))

                # link architectures
                add_arch = []
                for os_arch in operatingsystem['architecture']:
                    try:
                        arch_id = self.fm.architectures.show(os_arch['name'])['id']
                        add_arch.append(arch_id)
                    except:
                        log.log(log.LOG_WARN, "Cannot get ID of Architecture '{0}', skipping".format(os_arch['name']))

                # link medium
                add_medium = []
                medialist = self.fm.media.index(per_page=99999)['results']
                for os_media in operatingsystem['medium']:
                    for mediac in medialist:
                        if mediac['name'] == os_media['name']:
                            add_medium.append(mediac['id'])

                # link Provisioning Templates
                add_osdef = []
                add_provt = []
                ptlist = self.fm.provisioning_templates.index(per_page=99999)['results']
                for os_pt in operatingsystem['provisioning-template']:
                    for ptc in ptlist:
                        if ptc['name'] == os_pt['name']:
                            pto = {
                                #'id':                       os_obj['id'],
                                #'config_template_id':       ptc['id'],
                                'template_kind_id':         ptc['template_kind_id'],
                                'provisioning_template_id': ptc['id'],
                            }
                            add_osdef.append(pto)
                            add_provt.append(ptc['id'])

                # now all mapping is done, update os
                update_tpl = {}
                update_osdef = {}
                if add_pt: update_tpl['ptables'] = add_pt
                if add_arch: update_tpl['architecture_ids']         = add_arch
                if add_medium: update_tpl['medium_ids']             = add_medium
                if add_provt:
                    update_tpl['provisioning_template_ids']           = add_provt
                    update_osdef['os_default_templates_attributes']   = add_osdef

                log.log(log.LOG_INFO, "Linking Operating System '{0}' to Provisioning Templates, Media and Partition Tables".format(operatingsystem['description']))

                try:
                    self.fm.operatingsystems.update(os_obj['id'], update_tpl)
                    if add_provt:
                        self.fm.operatingsystems.update(os_obj['id'], update_osdef)
                except:
                    log.log(log.LOG_DEBUG, "An Error Occured when linking Operating System '{0}' (non-fatal)".format(operatingsystem['description']))



    def process_config_hostgroup(self):
        for hostgroup in self.get_config_section('hostgroup'):
            # validate yaml
            try:
                self.validator.hostgroup(hostgroup)
            except MultipleInvalid as e:
                log.log(log.LOG_WARN, "Cannot create Hostgroup '{0}': YAML validation Error: {1}".format(hostgroup['name'], e))
                continue

            # check if hostgroup already exists
            try:
                hg_id = self.fm.hostgroups.show(hostgroup['name'])['id']
                log.log(log.LOG_DEBUG, "Hostgroup '{0}' (id={1}) already present.".format(hostgroup['name'], hg_id))
                continue

            # hg is not existent on fm, creating
            except:
                log.log(log.LOG_INFO, "Create Hostgroup '{0}'".format(hostgroup['name']))
                hg_parent = hg_env = hg_os = hg_arch = hg_medium = hg_parttbl = hg_domain = hg_subnet = False

                # find parent hostgroup
                try:
                    hg_parent = self.fm.hostgroups.show(hostgroup['parent'])['id']
                except:
                    log.log(log.LOG_DEBUG, "Cannot get ID of Parent Hostgroup '{0}', skipping".format(hostgroup['parent']))

                # find environment
                envlist = self.fm.environments.index(per_page=99999)['results']
                for envc in envlist:
                    if (hostgroup['environment'] == envc['name']):
                        hg_env = envc['id']
                if not hg_env:
                    log.log(log.LOG_DEBUG, "Cannot get ID of Environment '{0}', skipping".format(hostgroup['environment']))

                # find operatingsystem
                try:
                    hg_os = self.fm.operatingsystems.show(hostgroup['os'])['id']
                except:
                    log.log(log.LOG_DEBUG, "Cannot get ID of Operating System '{0}', skipping".format(hostgroup['os']))

                # find architecture
                try:
                    hg_arch = self.fm.architectures.show(hostgroup['architecture'])['id']
                except:
                    log.log(log.LOG_DEBUG, "Cannot get ID of Architecture '{0}', skipping".format(hostgroup['architecture']))

                # find medium
                medialist = self.fm.media.index(per_page=99999)['results']
                for mediac in medialist:
                    if (mediac['name'] == hostgroup['medium']):
                        hg_medium = mediac['id']
                if not hg_medium:
                    log.log(log.LOG_DEBUG, "Cannot get ID of Medium '{0}', skipping".format(hostgroup['medium']))

                # find partition table
                try:
                    hg_parttbl = self.fm.ptables.show(hostgroup['partition-table'])['id']
                except:
                    log.log(log.LOG_DEBUG, "Cannot get ID of Partition Table '{0}', skipping".format(hostgroup['partition-table']))

                # find domain
                try:
                    hg_domain = self.fm.domains.show(hostgroup['domain'])['id']
                except:
                    log.log(log.LOG_DEBUG, "Cannot get ID of Domain '{0}', skipping".format(hostgroup['partition-table']))

                # find subnet
                try:
                    hg_subnet = self.fm.subnets.show(hostgroup['subnet'])['id']
                except:
                    log.log(log.LOG_DEBUG, "Cannot get ID of Subnet '{0}', skipping".format(hostgroup['subnet']))

                # build array
                hg_arr = {
                    'name':         hostgroup['name']
                }
                if hg_parent:
                    hg_arr['parent_id']           = hg_parent
                if hg_env:
                    hg_arr['environment_id']      = hg_env
                if hg_os:
                    hg_arr['operatingsystem_id']  = hg_os
                if hg_arch:
                    hg_arr['architecture_id']     = hg_arch
                if hg_medium:
                    hg_arr['medium_id']           = hg_medium
                if hg_domain:
                    hg_arr['domain_id']           = hg_domain
                if hg_parttbl:
                    hg_arr['ptable_id']           = hg_parttbl
                if hg_subnet:
                    hg_arr['subnet_id']           = hg_subnet

                # send to foreman-api
                try:
                    self.fm.hostgroups.create(hostgroup=hg_arr)
                except:
                    log.log(log.LOG_ERROR, "An Error Occured when creating Hostgroup '{0}'".format(hostgroup['name']))



    def process_config_host(self):
        for hostc in self.get_config_section('host'):
            hostname = "{0}.{1}".format(hostc['name'], hostc['domain'])
            try:
                host = self.fm.hosts.show(hostname)
                host_id = host['id']
                log.log(log.LOG_DEBUG, "Host '{0}' (id={1}) already present.".format(hostc['name'], host_id))
            except:

                # get domain_id
                try:
                    domain_id = self.fm.domains.show(hostc['domain'])['id']
                except:
                    log.log(log.LOG_ERROR, "Domain {0} does not exist".format(hostc['environment']))
                    continue

                # get environment_id
                envlist = self.fm.environments.index(per_page=99999)['results']
                enviroment_id = False
                for envc in envlist:
                    if (hostc['environment'] == envc['name']):
                        enviroment_id = envc['id']
                if not enviroment_id:
                    log.log(log.LOG_WARN, "Cannot get ID of Environment '{0}', skipping".format(hostc['environment']))
                    continue

                # get architecture_id
                try:
                    architecture_id = self.fm.architectures.show(hostc['architecture'])['id']
                except:
                    log.log(log.LOG_ERROR, "Architecture {0} does not exist".format(hostc['architecture']))
                    continue

                # get os_id
                try:
                    os_id = self.fm.operatingsystems.show(hostc['os'])['id']
                except:
                    log.log(log.LOG_ERROR, "OS {0} does not exist".format(hostc['os']))
                    continue

                # get media_id, show() not working here, manual mapping
                media_id = False
                for media in self.fm.media.index()['results']:
                    if (media['name'] == hostc['media']):
                        media_id = media['id']
                if not media_id:
                    log.log(log.LOG_ERROR, "Media {0} does not exist".format(hostc['media']))
                    continue

                # get parttable_id
                try:
                    parttable_id = self.fm.ptables.show(hostc['partition'])['id']
                except:
                    log.log(log.LOG_ERROR, "Partition {0} does not exist".format(hostc['partition']))
                    continue

                # get model_id
                try:
                    model_id = self.fm.models.show(hostc['model'])['id']
                except:
                    log.log(log.LOG_ERROR, "Model '{0}' does not exist".format(hostc['model']))
                    continue

                # build host_params array
                host_params = []
                for name,value in hostc['parameters'].iteritems():
                    p = {
                        'name':     name,
                        'nested':   False,
                        'value':    value
                    }
                    host_params.append(p)

                host_tpl = {
                    'managed':              'true',
                    'build':                'true',
                    'name':                 hostc['name'],
                    #'mac':                  hostc['mac'],
                    'domain_id':            domain_id,
                    'environment_id':       enviroment_id,
                    'architecture_id':      architecture_id,
                    'operatingsystem_id':   os_id,
                    'medium_id':            media_id,
                    'ptable_id':            parttable_id,
                    'model_id':             model_id,
                    'root_pass':            hostc['root-pass'],
                }

                # try to get mac
                try:
                    hmac = hostc['mac']
                except:
                    pass
                if hmac:
                    host_tpl['mac'] = hmac

                # get hostgroup_id
                hg_id = False
                try:
                    hg_id = self.fm.hostgroups.show(hostc['hostgroup'])['id']
                    if hg_id:
                        host_tpl['hostgroup_id'] = hg_id
                except:
                    try:
                        log.log(log.LOG_ERROR, "Hostgroup {0} does not exist".format(hostc['hostgroup']))
                        continue
                    except:
                        pass

                # create host & fix interfaces
                log.log(log.LOG_INFO, "Create Host '{0}'".format(hostname))

                fmh = self.fm.hosts.create( host = host_tpl )
                fixif = {
                    'id':           fmh['interfaces'][0]['id'],
                    'managed':      'false',
                    'primary':      'true',
                    'provision':    'true'
                }
                fixhost = {
                    'interfaces_attributes':        [ fixif ],
                    'host_parameters_attributes':   host_params
                }
                try:
                    self.fm.hosts.update(fixhost, fmh['id'])
                    return fmh
                except:
                    log.log(log.LOG_DEBUG, "An Error Occured when linking Host '{0}' (non-fatal)".format(hostc['name']))

    def get_host(self, host_id):
        host = self.fm.hosts.show(id=host_id)
        return host

    def remove_host(self, host_id):
        try:
            self.fm.hosts.destroy(id=host_id)
            return True
        except:
            return False


    def get_audit_ip(self, host_id):
        # this is hacky right now since the audits-api has an bug and does not return any audits whe passing host_id
        # host_audits = self.fm.hosts.audits_index(auditable_id=80)
        #ha = self.fm.hosts.index(auditable_id=81)
        host_audits = []
        host_ip = False
        all_audits = self.fm.audits.index(per_page=99999)['results']

        # get audits of specified host
        for audit in all_audits:
            if ( audit['auditable_type'] == 'Host') and (audit['auditable_id'] == host_id):
                host_audits.append(audit)

        # search for audit type audited_changes['build']
        for audit in host_audits:
            if 'installed_at' in audit['audited_changes']:
                try:
                    ll = len(audit['audited_changes']['installed_at'])
                    host_ip = audit['remote_address']
                    return host_ip
                except:
                    pass

        # nothing found, return False
        return False
