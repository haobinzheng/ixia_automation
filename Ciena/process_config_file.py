import os
import pexpect
import sys
import time
import datetime
import logging
import csv
import re
from switch_class import *

infile = '5160_1_J.log'
outfile = '5160_1_J_config.log'

remove_logical_id(infile,outfile)
