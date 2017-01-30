#!/usr/bin/python
# -*- coding: utf8 -*-


import sys
import logging
import log
import foremanclient
from pprint import pprint
from foreman.client import Foreman, ForemanException
from voluptuous import MultipleInvalid




class ForemanCleanup(foremanclient.ForemanBase):

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
