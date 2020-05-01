#pybot --argumentfile hb_args /Users/mike.zheng2008/Python/fortinet/automation/testcases
# example.robot
*** Settings ***
| Library | Process
| Library  hello.py

*** Test Cases ***
| Test #1: Example of running a python script
| | ${result}= | run process | python | helloworld.py
| | Should be equal as integers | ${result.rc} | 0
| | Should be equal as strings  | ${result.stdout} | hello, world

*** Test Cases ***
| Test #2: Another Example of running a python script
| | ${result}= | run process | python | helloworld2.py
| | Should be equal as integers | ${result.rc} | 0
| | Should be equal as strings  | ${result.stdout} | hello, world
*** Test cases ***
| Example of running a python script again
hello  | Mike |  20

*** Keywords ***
Init
   hello 

#| *Keywords* |
#| Suite Setup Keyword | [Arguments] | ${testbed} | ${tbinfo} | ${tbtopo} |
#| | [Documentation] | Initialize an Envirioment for Suite test |
#| | Run Keyword | Test Topo Init | ${testbed} | ${tbinfo} | ${tbtopo} |
