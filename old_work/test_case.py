import os
import pexpect
import sys
import time
import datetime
import logging
import csv
import re
from switch_class import *
from utility import *
from subprocess   import Popen, PIPE


def get_all_ingress_tunnel(dut):
	corout_in_lsp_list = []
	ingress_tu = ingress_tunnel(dut)
	ingress_tu.get_tunnel_details()
	hhcorout_in_lsp_list = []
	for tunnel_detail in ingress_tu.lsp_detail_list:
		in_lsp = corout_ingress_tunnel(dut, tunnel_detail)
		#in_lsp.print_tunnel_details()
		corout_in_lsp_list.append(in_lsp)
	return corout_in_lsp_list

def flap_all_ingress_tunnel(dut):
	lsp_list = get_all_ingress_tunnel(dut)
	for lsp in lsp_list:
		lsp.disable_tunnel_lsp()

	sleep(10)
	ingress_tu = ingress_tunnel(dut)
	print_line_step()
	ingress_tu.show_tunnel_stats()
	
def detach_all_vc(vs_list):
	for vs in vs_list.vs_instance_list:
		vs.detach_vc()

def attach_all_vc(vs_list):
	for vs in vs_list.vs_instance_list:
		vs.attach_vc()

def remove_vs_all_port(vs_list):
	for vs in vs_list.vs_instance_list:
		vs.remove_port()
		
def add_vs_all_port(vs_list):
	for vs in vs_list.vs_instance_list:
		vs.add_port()

def case_turn_on_hw_bfd_all(dut):
	print_line_case('turn on hardware BFD')
	ingress_tu = ingress_tunnel(dut)
	egress_tu = egress_tunnel(dut)
	egress_tu.build_tunnel_all()
	ingress_tu.build_tunnel_all()
	turn_on_hw_bfd(dut)
	ingress_tu.set_hw_bfd_all()
	egress_tu.set_hw_bfd_all()
	
def case_turn_on_hw_bfd_all_profile(dut):
	print_line_case('turn on hardware BFD')
	ingress_tu = ingress_tunnel(dut)
	egress_tu = egress_tunnel(dut)
	egress_tu.build_tunnel_all()
	ingress_tu.build_tunnel_all()
	turn_on_hw_bfd(dut)
	for profile in dut.bfd_list:
		ingress_tu.set_hw_bfd_all(profile)
		egress_tu.set_hw_bfd_all(profile)

def case_turn_off_hw_bfd_all(dut):
	print_line_case('turn on software BFD')
	ingress_tu = ingress_tunnel(dut)
	egress_tu = egress_tunnel(dut)
	egress_tu.build_tunnel_all()
	ingress_tu.build_tunnel_all()
	turn_off_hw_bfd(dut)
	ingress_tu.set_sw_bfd_all()
	egress_tu.set_sw_bfd_all()

def case_sweeping_sw_bfd_profiles(dut):
	print_line_case('Changing various BFD intervals')
	ingress_tu = ingress_tunnel(dut)
	egress_tu = egress_tunnel(dut)
	bfd1 = bfd(dut)
	egress_tu.build_tunnel_all()
	ingress_tu.build_tunnel_all()
	for bfd_profile in bfd1.profile_name_list:
		ingress_tu.set_sw_bfd_profile_all(bfd_profile)
		egress_tu.set_sw_bfd_profile_all(bfd_profile)
		print "After changing to BFD profile %s, show bfd " % bfd_profile
		sleep(10)
		result = sw_show_cmd (dut,'bfd show')
		print result
		result = sw_show_cmd (dut,'bfd session show')
		print result
		sleep(5)
		result = sw_show_cmd (dut,'bfd show')
		print result
		result = sw_show_cmd (dut,'bfd session show')
		print result
		sleep(5)
		result = sw_show_cmd (dut,'bfd show')
		print result
		result = sw_show_cmd (dut,'bfd session show')
		print result

def case_sweeping_ais_profiles(dut):
	print_line_case('Sweeping across different AIS profiles')
	ingress_tu = ingress_tunnel(dut)
	egress_tu = egress_tunnel(dut)
	ais_obj = ais(dut)
	egress_tu.build_tunnel_all()
	ingress_tu.build_tunnel_all()
	for profile in ais_obj.profile_list:
		ingress_tu.set_ais_profile_all(profile)
		egress_tu.set_ais_profile_all(profile)
		print_line_step('Finished change of one ais profile')
		sleep(10)
		print "After changing to ais profile %s, show ais statistics " % profile
		result = sw_show_cmd (dut,'ais statistics show')
		print result
		result = sw_show_cmd (dut,'ais statistics show')
		print result
		sleep(10)
		result = sw_show_cmd (dut,'ais statistics show')
		print result
		result = sw_show_cmd (dut,'ais statistics show')
		print result
		sleep(10)
		result = sw_show_cmd (dut,'ais statistics show')
		print result
		result = sw_show_cmd (dut,'ais statistics show')
		print result
		sleep(10)