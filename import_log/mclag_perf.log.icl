2019-10-11 10:50:29 :: Upgrade FSW software via via Fortigate 
2019-10-11 10:50:29 :: ** Running the test in silent mode 
2019-10-11 10:50:29 :: ** Before starting testing, configure devices 
2019-10-11 10:50:29 :: ** Running test with port log-mac-event enabled 
2019-10-11 10:50:29 :: ** Will factory reset each FSW  
2019-10-11 10:50:29 :: ** Fiber cut test will be in automated mode 
2019-10-11 10:50:29 :: ** Test Bed = fg-548d 
2019-10-11 10:50:29 :: ** IXIA ports will be allocated IP address statically  
2019-10-11 10:50:29 :: ** Test iterate numbers = 2 
2019-10-11 10:50:29 :: ** Test Case To Run:3 
For test #1, MAC table size = [1000, 2000]
2019-10-11 10:50:29 :: ** Test under background MAC address learning,size = [1000, 2000] 
2019-10-11 10:50:29 :: ** Measure performance WITHOUT rebooting DUTs 
==============================================================================================
**** REMINDER **** 	**** REMINDER ****	**** REMINDER ****	**** REMINDER ****	 
Please make sure to execute the following procedures before running the test:
	1)Make sure sensitive micro-usb console cables are connected well. 
	2)Make sure IXIA port connection is good. A bad connection will fail the script.
	3)Remember to move the 3rd and 4th IXIA port from 548D setup to 448D or visa versa 
	when switching to differrent testbed
	4)Make sure the have -e option at CLI to run sw1 and sw2 setup
	5)Make sure to uncomment of lines under the <official run> marker 
===============================================================================================
2019-10-11 10:50:29 :: ============================== Pre-test setup and configuration =================== 

		1) SW1: shut down port13 and port14
		2) sw1: enable port 7
		3) 424D: enable port 1
		4) DUT1: enable port49, port 50
		5) DUT2: enable port49, port 50
		6) TBD: FGT configuration
		7) TBD: DUT1, DUT2, DUT3, DUT4 ICL and other configuration.  
		
2019-10-11 10:50:29 :: console server ip =10.105.50.3 
2019-10-11 10:50:29 :: console port=2057 
2019-10-11 10:50:42 :: Info: Login without password 


2019-10-11 10:50:42 :: configuring: config system global 
2019-10-11 10:50:42 :: configuring: set admintimeout 480 
2019-10-11 10:50:43 :: configuring: end 
2019-10-11 10:50:43 :: get_switch_telnet_connection_new: Login sucessful!
 
2019-10-11 10:50:43 :: console server ip =10.105.50.3 
2019-10-11 10:50:43 :: console port=2056 
2019-10-11 10:50:56 :: Info: Login without password 


2019-10-11 10:50:56 :: configuring: config system global 
2019-10-11 10:50:57 :: configuring: set admintimeout 480 
2019-10-11 10:50:57 :: configuring: end 
2019-10-11 10:50:58 :: get_switch_telnet_connection_new: Login sucessful!
 
2019-10-11 10:50:58 :: console server ip =10.105.50.1 
2019-10-11 10:50:58 :: console port=2075 
2019-10-11 10:51:05 :: Info: Login without password 


2019-10-11 10:51:05 :: configuring: config system global 
2019-10-11 10:51:05 :: configuring: set admintimeout 480 
2019-10-11 10:51:06 :: configuring: end 
2019-10-11 10:51:07 :: get_switch_telnet_connection_new: Login sucessful!
 
2019-10-11 10:51:07 :: console server ip =10.105.50.1 
2019-10-11 10:51:07 :: console port=2078 
2019-10-11 10:51:20 :: Info: Login without password 


2019-10-11 10:51:20 :: configuring: config system global 
2019-10-11 10:51:22 :: configuring: set admintimeout 480 
2019-10-11 10:51:23 :: configuring: end 
2019-10-11 10:51:23 :: get_switch_telnet_connection_new: Login sucessful!
 
2019-10-11 10:51:25 :: ============================ dut1-548d software image = v6.2.0,build0190,191001 (Interim) 
2019-10-11 10:51:27 :: ============================ dut2-548d software image = v6.2.0,build0190,191001 (Interim) 
2019-10-11 10:51:29 :: ============================ dut3-548d software image = v6.2.0,build0190,191001 (Interim) 
2019-10-11 10:51:31 :: ============================ dut4-548d software image = v6.2.0,build0190,191001 (Interim) 

1. Reboot FGTs
2. Factory reset all switches
3. Configure physical ports to ldp-profile default-auto-isl
4. Configure mclag-isl and auto-isl-port-group
5. Configure switch trunk port via FGT
6. Upgrade switches 
7. Configure log-mac-event
8. Close consoles for FGT and FSW
9. Start test loops
for each mac_size:
	-setup ixia and ensure initial traffic flow is ok 
	-setup log files for process
	-start cpu monitoring process 
	-start background delete-mac process
	-Main process loop: 
		-measure traffic loss 
	
2019-10-11 10:51:31 :: ------------------------------ login Fortigate devices ----------------------- 
2019-10-11 10:51:31 :: console server ip =10.105.50.1 
2019-10-11 10:51:31 :: console port=2066 
2019-10-11 10:51:44 :: Info: Login without password 


2019-10-11 10:51:44 :: configuring: config system global 
2019-10-11 10:51:45 :: configuring: set admintimeout 480 
2019-10-11 10:51:45 :: configuring: end 
2019-10-11 10:51:46 :: get_switch_telnet_connection_new: Login sucessful!
 
2019-10-11 10:51:46 :: console server ip =10.105.50.2 
2019-10-11 10:51:46 :: console port=2074 
2019-10-11 10:51:54 :: Info: Login without password 


2019-10-11 10:51:54 :: configuring: config system global 
2019-10-11 10:51:54 :: configuring: set admintimeout 480 
2019-10-11 10:51:55 :: configuring: end 
2019-10-11 10:51:55 :: get_switch_telnet_connection_new: Login sucessful!
 
2019-10-11 10:51:55 :: configuring 3960E: config switch-controller security-policy local-access 
2019-10-11 10:51:56 :: configuring 3960E: edit "default" 
2019-10-11 10:51:56 :: configuring 3960E: set mgmt-allowaccess https ping ssh telnet 
2019-10-11 10:51:57 :: configuring 3960E: next 
2019-10-11 10:51:57 :: configuring 3960E: end 
2019-10-11 10:51:58 :: -------- Rebooting device : 3960E 
2019-10-11 10:52:02 :: -------- Rebooting device : 3960E 
2019-10-11 10:52:06 :: ========================= After rebooting FGTs, wait for 600 sec ========================== 
============================ Timer:600 seconds remaining =================================================== Timer:599 seconds remaining =================================================== Timer:598 seconds remaining =================================================== Timer:597 seconds remaining =================================================== Timer:596 seconds remaining =================================================== Timer:595 seconds remaining =================================================== Timer:594 seconds remaining =================================================== Timer:593 seconds remaining =================================================== Timer:592 seconds remaining =================================================== Timer:591 seconds remaining =================================================== Timer:590 seconds remaining =================================================== Timer:589 seconds remaining =================================================== Timer:588 seconds remaining =================================================== Timer:587 seconds remaining =================================================== Timer:586 seconds remaining =================================================== Timer:585 seconds remaining =================================================== Timer:584 seconds remaining =================================================== Timer:583 seconds remaining =================================================== Timer:582 seconds remaining =================================================== Timer:581 seconds remaining =================================================== Timer:580 seconds remaining =================================================== Timer:579 seconds remaining =================================================== Timer:578 seconds remaining =================================================== Timer:577 seconds remaining =================================================== Timer:576 seconds remaining =================================================== Timer:575 seconds remaining =================================================== Timer:574 seconds remaining =================================================== Timer:573 seconds remaining =================================================== Timer:572 seconds remaining =================================================== Timer:571 seconds remaining =================================================== Timer:570 seconds remaining =================================================== Timer:569 seconds remaining =================================================== Timer:568 seconds remaining =================================================== Timer:567 seconds remaining =================================================== Timer:566 seconds remaining =================================================== Timer:565 seconds remaining =================================================== Timer:564 seconds remaining =================================================== Timer:563 seconds remaining =================================================== Timer:562 seconds remaining =================================================== Timer:561 seconds remaining =================================================== Timer:560 seconds remaining =================================================== Timer:559 seconds remaining =================================================== Timer:558 seconds remaining =================================================== Timer:557 seconds remaining =================================================== Timer:556 seconds remaining =================================================== Timer:555 seconds remaining =================================================== Timer:554 seconds remaining =================================================== Timer:553 seconds remaining =================================================== Timer:552 seconds remaining =================================================== Timer:551 seconds remaining =================================================== Timer:550 seconds remaining =================================================== Timer:549 seconds remaining =================================================== Timer:548 seconds remaining =================================================== Timer:547 seconds remaining =================================================== Timer:546 seconds remaining =================================================== Timer:545 seconds remaining =================================================== Timer:544 seconds remaining =================================================== Timer:543 seconds remaining =================================================== Timer:542 seconds remaining =================================================== Timer:541 seconds remaining =================================================== Timer:540 seconds remaining =================================================== Timer:539 seconds remaining =================================================== Timer:538 seconds remaining =================================================== Timer:537 seconds remaining =================================================== Timer:536 seconds remaining =================================================== Timer:535 seconds remaining =================================================== Timer:534 seconds remaining =================================================== Timer:533 seconds remaining =================================================== Timer:532 seconds remaining =================================================== Timer:531 seconds remaining =================================================== Timer:530 seconds remaining =================================================== Timer:529 seconds remaining =================================================== Timer:528 seconds remaining =================================================== Timer:527 seconds remaining =================================================== Timer:526 seconds remaining =================================================== Timer:525 seconds remaining =================================================== Timer:524 seconds remaining =================================================== Timer:523 seconds remaining =================================================== Timer:522 seconds remaining =================================================== Timer:521 seconds remaining =================================================== Timer:520 seconds remaining =================================================== Timer:519 seconds remaining =================================================== Timer:518 seconds remaining =================================================== Timer:517 seconds remaining =================================================== Timer:516 seconds remaining =================================================== Timer:515 seconds remaining =================================================== Timer:514 seconds remaining =================================================== Timer:513 seconds remaining =================================================== Timer:512 seconds remaining =================================================== Timer:511 seconds remaining =================================================== Timer:510 seconds remaining =================================================== Timer:509 seconds remaining =================================================== Timer:508 seconds remaining =================================================== Timer:507 seconds remaining =================================================== Timer:506 seconds remaining =================================================== Timer:505 seconds remaining =================================================== Timer:504 seconds remaining =================================================== Timer:503 seconds remaining =================================================== Timer:502 seconds remaining =================================================== Timer:501 seconds remaining =================================================== Timer:500 seconds remaining =================================================== Timer:499 seconds remaining =================================================== Timer:498 seconds remaining =================================================== Timer:497 seconds remaining =================================================== Timer:496 seconds remaining =================================================== Timer:495 seconds remaining =================================================== Timer:494 seconds remaining =================================================== Timer:493 seconds remaining =================================================== Timer:492 seconds remaining =================================================== Timer:491 seconds remaining =================================================== Timer:490 seconds remaining =================================================== Timer:489 seconds remaining =================================================== Timer:488 seconds remaining =================================================== Timer:487 seconds remaining =================================================== Timer:486 seconds remaining =================================================== Timer:485 seconds remaining =================================================== Timer:484 seconds remaining =================================================== Timer:483 seconds remaining =================================================== Timer:482 seconds remaining =================================================== Timer:481 seconds remaining =================================================== Timer:480 seconds remaining =================================================== Timer:479 seconds remaining =================================================== Timer:478 seconds remaining =================================================== Timer:477 seconds remaining =================================================== Timer:476 seconds remaining =================================================== Timer:475 seconds remaining =================================================== Timer:474 seconds remaining =================================================== Timer:473 seconds remaining =================================================== Timer:472 seconds remaining =================================================== Timer:471 seconds remaining =================================================== Timer:470 seconds remaining =================================================== Timer:469 seconds remaining =================================================== Timer:468 seconds remaining =================================================== Timer:467 seconds remaining =================================================== Timer:466 seconds remaining =================================================== Timer:465 seconds remaining =================================================== Timer:464 seconds remaining =================================================== Timer:463 seconds remaining =================================================== Timer:462 seconds remaining =================================================== Timer:461 seconds remaining =================================================== Timer:460 seconds remaining =================================================== Timer:459 seconds remaining =================================================== Timer:458 seconds remaining =================================================== Timer:457 seconds remaining =================================================== Timer:456 seconds remaining =================================================== Timer:455 seconds remaining =================================================== Timer:454 seconds remaining =================================================== Timer:453 seconds remaining =================================================== Timer:452 seconds remaining =================================================== Timer:451 seconds remaining =================================================== Timer:450 seconds remaining =================================================== Timer:449 seconds remaining =================================================== Timer:448 seconds remaining =================================================== Timer:447 seconds remaining =================================================== Timer:446 seconds remaining =================================================== Timer:445 seconds remaining =================================================== Timer:444 seconds remaining =================================================== Timer:443 seconds remaining =================================================== Timer:442 seconds remaining =================================================== Timer:441 seconds remaining =================================================== Timer:440 seconds remaining =================================================== Timer:439 seconds remaining =================================================== Timer:438 seconds remaining =================================================== Timer:437 seconds remaining =================================================== Timer:436 seconds remaining =================================================== Timer:435 seconds remaining =================================================== Timer:434 seconds remaining =================================================== Timer:433 seconds remaining =================================================== Timer:432 seconds remaining =================================================== Timer:431 seconds remaining =================================================== Timer:430 seconds remaining =================================================== Timer:429 seconds remaining =================================================== Timer:428 seconds remaining =================================================== Timer:427 seconds remaining =================================================== Timer:426 seconds remaining =================================================== Timer:425 seconds remaining =================================================== Timer:424 seconds remaining =================================================== Timer:423 seconds remaining =================================================== Timer:422 seconds remaining =================================================== Timer:421 seconds remaining =================================================== Timer:420 seconds remaining =================================================== Timer:419 seconds remaining =================================================== Timer:418 seconds remaining =================================================== Timer:417 seconds remaining =================================================== Timer:416 seconds remaining =================================================== Timer:415 seconds remaining =================================================== Timer:414 seconds remaining =================================================== Timer:413 seconds remaining =================================================== Timer:412 seconds remaining =================================================== Timer:411 seconds remaining =================================================== Timer:410 seconds remaining =================================================== Timer:409 seconds remaining =================================================== Timer:408 seconds remaining =================================================== Timer:407 seconds remaining =================================================== Timer:406 seconds remaining =================================================== Timer:405 seconds remaining =================================================== Timer:404 seconds remaining =================================================== Timer:403 seconds remaining =================================================== Timer:402 seconds remaining =================================================== Timer:401 seconds remaining =================================================== Timer:400 seconds remaining =================================================== Timer:399 seconds remaining =================================================== Timer:398 seconds remaining =================================================== Timer:397 seconds remaining =================================================== Timer:396 seconds remaining =================================================== Timer:395 seconds remaining =================================================== Timer:394 seconds remaining =================================================== Timer:393 seconds remaining =================================================== Timer:392 seconds remaining =================================================== Timer:391 seconds remaining =================================================== Timer:390 seconds remaining =================================================== Timer:389 seconds remaining =================================================== Timer:388 seconds remaining =================================================== Timer:387 seconds remaining =================================================== Timer:386 seconds remaining =================================================== Timer:385 seconds remaining =================================================== Timer:384 seconds remaining =================================================== Timer:383 seconds remaining =================================================== Timer:382 seconds remaining =================================================== Timer:381 seconds remaining =================================================== Timer:380 seconds remaining =================================================== Timer:379 seconds remaining =================================================== Timer:378 seconds remaining =================================================== Timer:377 seconds remaining =================================================== Timer:376 seconds remaining =================================================== Timer:375 seconds remaining =================================================== Timer:374 seconds remaining =================================================== Timer:373 seconds remaining =================================================== Timer:372 seconds remaining =================================================== Timer:371 seconds remaining =================================================== Timer:370 seconds remaining =================================================== Timer:369 seconds remaining =================================================== Timer:368 seconds remaining =================================================== Timer:367 seconds remaining =================================================== Timer:366 seconds remaining =================================================== Timer:365 seconds remaining =================================================== Timer:364 seconds remaining =================================================== Timer:363 seconds remaining =================================================== Timer:362 seconds remaining =================================================== Timer:361 seconds remaining =================================================== Timer:360 seconds remaining =================================================== Timer:359 seconds remaining =================================================== Timer:358 seconds remaining =================================================== Timer:357 seconds remaining =================================================== Timer:356 seconds remaining =================================================== Timer:355 seconds remaining =================================================== Timer:354 seconds remaining =================================================== Timer:353 seconds remaining =================================================== Timer:352 seconds remaining =================================================== Timer:351 seconds remaining =================================================== Timer:350 seconds remaining =================================================== Timer:349 seconds remaining =================================================== Timer:348 seconds remaining =================================================== Timer:347 seconds remaining =================================================== Timer:346 seconds remaining =================================================== Timer:345 seconds remaining =================================================== Timer:344 seconds remaining =================================================== Timer:343 seconds remaining =================================================== Timer:342 seconds remaining =================================================== Timer:341 seconds remaining =================================================== Timer:340 seconds remaining =================================================== Timer:339 seconds remaining =================================================== Timer:338 seconds remaining =================================================== Timer:337 seconds remaining =================================================== Timer:336 seconds remaining =================================================== Timer:335 seconds remaining =================================================== Timer:334 seconds remaining =================================================== Timer:333 seconds remaining =================================================== Timer:332 seconds remaining =================================================== Timer:331 seconds remaining =================================================== Timer:330 seconds remaining =================================================== Timer:329 seconds remaining =================================================== Timer:328 seconds remaining =================================================== Timer:327 seconds remaining =================================================== Timer:326 seconds remaining =================================================== Timer:325 seconds remaining =================================================== Timer:324 seconds remaining =================================================== Timer:323 seconds remaining =================================================== Timer:322 seconds remaining =================================================== Timer:321 seconds remaining =================================================== Timer:320 seconds remaining =================================================== Timer:319 seconds remaining =================================================== Timer:318 seconds remaining =================================================== Timer:317 seconds remaining =================================================== Timer:316 seconds remaining =================================================== Timer:315 seconds remaining =================================================== Timer:314 seconds remaining =================================================== Timer:313 seconds remaining =================================================== Timer:312 seconds remaining =================================================== Timer:311 seconds remaining =================================================== Timer:310 seconds remaining =================================================== Timer:309 seconds remaining =================================================== Timer:308 seconds remaining =================================================== Timer:307 seconds remaining =================================================== Timer:306 seconds remaining =================================================== Timer:305 seconds remaining =================================================== Timer:304 seconds remaining =================================================== Timer:303 seconds remaining =================================================== Timer:302 seconds remaining =================================================== Timer:301 seconds remaining =================================================== Timer:300 seconds remaining =================================================== Timer:299 seconds remaining =================================================== Timer:298 seconds remaining =================================================== Timer:297 seconds remaining =================================================== Timer:296 seconds remaining =================================================== Timer:295 seconds remaining =================================================== Timer:294 seconds remaining =================================================== Timer:293 seconds remaining =================================================== Timer:292 seconds remaining =================================================== Timer:291 seconds remaining =================================================== Timer:290 seconds remaining =================================================== Timer:289 seconds remaining =================================================== Timer:288 seconds remaining =================================================== Timer:287 seconds remaining =================================================== Timer:286 seconds remaining =================================================== Timer:285 seconds remaining =================================================== Timer:284 seconds remaining =================================================== Timer:283 seconds remaining =================================================== Timer:282 seconds remaining =================================================== Timer:281 seconds remaining =================================================== Timer:280 seconds remaining =================================================== Timer:279 seconds remaining =================================================== Timer:278 seconds remaining =================================================== Timer:277 seconds remaining =================================================== Timer:276 seconds remaining =================================================== Timer:275 seconds remaining =================================================== Timer:274 seconds remaining =================================================== Timer:273 seconds remaining =================================================== Timer:272 seconds remaining =================================================== Timer:271 seconds remaining =================================================== Timer:270 seconds remaining =================================================== Timer:269 seconds remaining =================================================== Timer:268 seconds remaining =================================================== Timer:267 seconds remaining =================================================== Timer:266 seconds remaining =================================================== Timer:265 seconds remaining =================================================== Timer:264 seconds remaining =================================================== Timer:263 seconds remaining =================================================== Timer:262 seconds remaining =================================================== Timer:261 seconds remaining =================================================== Timer:260 seconds remaining =================================================== Timer:259 seconds remaining =================================================== Timer:258 seconds remaining =================================================== Timer:257 seconds remaining =================================================== Timer:256 seconds remaining =================================================== Timer:255 seconds remaining =================================================== Timer:254 seconds remaining =================================================== Timer:253 seconds remaining =================================================== Timer:252 seconds remaining =================================================== Timer:251 seconds remaining =================================================== Timer:250 seconds remaining =================================================== Timer:249 seconds remaining =================================================== Timer:248 seconds remaining =================================================== Timer:247 seconds remaining =================================================== Timer:246 seconds remaining =================================================== Timer:245 seconds remaining =================================================== Timer:244 seconds remaining =================================================== Timer:243 seconds remaining =================================================== Timer:242 seconds remaining =================================================== Timer:241 seconds remaining =================================================== Timer:240 seconds remaining =================================================== Timer:239 seconds remaining =================================================== Timer:238 seconds remaining =================================================== Timer:237 seconds remaining =================================================== Timer:236 seconds remaining =================================================== Timer:235 seconds remaining =================================================== Timer:234 seconds remaining =================================================== Timer:233 seconds remaining =================================================== Timer:232 seconds remaining =================================================== Timer:231 seconds remaining =================================================== Timer:230 seconds remaining =================================================== Timer:229 seconds remaining =================================================== Timer:228 seconds remaining =================================================== Timer:227 seconds remaining =================================================== Timer:226 seconds remaining =================================================== Timer:225 seconds remaining =================================================== Timer:224 seconds remaining =================================================== Timer:223 seconds remaining =================================================== Timer:222 seconds remaining =================================================== Timer:221 seconds remaining =================================================== Timer:220 seconds remaining =================================================== Timer:219 seconds remaining =================================================== Timer:218 seconds remaining =================================================== Timer:217 seconds remaining =================================================== Timer:216 seconds remaining =================================================== Timer:215 seconds remaining =================================================== Timer:214 seconds remaining =================================================== Timer:213 seconds remaining =================================================== Timer:212 seconds remaining =================================================== Timer:211 seconds remaining =================================================== Timer:210 seconds remaining =================================================== Timer:209 seconds remaining =================================================== Timer:208 seconds remaining =================================================== Timer:207 seconds remaining =================================================== Timer:206 seconds remaining =================================================== Timer:205 seconds remaining =================================================== Timer:204 seconds remaining =================================================== Timer:203 seconds remaining =================================================== Timer:202 seconds remaining =================================================== Timer:201 seconds remaining =================================================== Timer:200 seconds remaining =================================================== Timer:199 seconds remaining =================================================== Timer:198 seconds remaining =================================================== Timer:197 seconds remaining =================================================== Timer:196 seconds remaining =================================================== Timer:195 seconds remaining =================================================== Timer:194 seconds remaining =================================================== Timer:193 seconds remaining =================================================== Timer:192 seconds remaining =================================================== Timer:191 seconds remaining =================================================== Timer:190 seconds remaining =================================================== Timer:189 seconds remaining =================================================== Timer:188 seconds remaining =================================================== Timer:187 seconds remaining =================================================== Timer:186 seconds remaining =================================================== Timer:185 seconds remaining =================================================== Timer:184 seconds remaining =================================================== Timer:183 seconds remaining =================================================== Timer:182 seconds remaining =================================================== Timer:181 seconds remaining =================================================== Timer:180 seconds remaining =================================================== Timer:179 seconds remaining =================================================== Timer:178 seconds remaining =================================================== Timer:177 seconds remaining =================================================== Timer:176 seconds remaining =================================================== Timer:175 seconds remaining =================================================== Timer:174 seconds remaining =================================================== Timer:173 seconds remaining =================================================== Timer:172 seconds remaining =================================================== Timer:171 seconds remaining =================================================== Timer:170 seconds remaining =================================================== Timer:169 seconds remaining =================================================== Timer:168 seconds remaining =================================================== Timer:167 seconds remaining =================================================== Timer:166 seconds remaining =================================================== Timer:165 seconds remaining =================================================== Timer:164 seconds remaining =================================================== Timer:163 seconds remaining =================================================== Timer:162 seconds remaining =================================================== Timer:161 seconds remaining =================================================== Timer:160 seconds remaining =================================================== Timer:159 seconds remaining =================================================== Timer:158 seconds remaining =================================================== Timer:157 seconds remaining =================================================== Timer:156 seconds remaining =================================================== Timer:155 seconds remaining =================================================== Timer:154 seconds remaining =================================================== Timer:153 seconds remaining =================================================== Timer:152 seconds remaining =================================================== Timer:151 seconds remaining =================================================== Timer:150 seconds remaining =================================================== Timer:149 seconds remaining =================================================== Timer:148 seconds remaining =================================================== Timer:147 seconds remaining =================================================== Timer:146 seconds remaining =================================================== Timer:145 seconds remaining =================================================== Timer:144 seconds remaining =================================================== Timer:143 seconds remaining =================================================== Timer:142 seconds remaining =================================================== Timer:141 seconds remaining =================================================== Timer:140 seconds remaining =================================================== Timer:139 seconds remaining =================================================== Timer:138 seconds remaining =================================================== Timer:137 seconds remaining =================================================== Timer:136 seconds remaining =================================================== Timer:135 seconds remaining =================================================== Timer:134 seconds remaining =================================================== Timer:133 seconds remaining =================================================== Timer:132 seconds remaining =================================================== Timer:131 seconds remaining =================================================== Timer:130 seconds remaining =================================================== Timer:129 seconds remaining =================================================== Timer:128 seconds remaining =================================================== Timer:127 seconds remaining =================================================== Timer:126 seconds remaining =================================================== Timer:125 seconds remaining =================================================== Timer:124 seconds remaining =================================================== Timer:123 seconds remaining =================================================== Timer:122 seconds remaining =================================================== Timer:121 seconds remaining =================================================== Timer:120 seconds remaining =================================================== Timer:119 seconds remaining =================================================== Timer:118 seconds remaining =================================================== Timer:117 seconds remaining =================================================== Timer:116 seconds remaining =================================================== Timer:115 seconds remaining =================================================== Timer:114 seconds remaining =================================================== Timer:113 seconds remaining =================================================== Timer:112 seconds remaining =================================================== Timer:111 seconds remaining =================================================== Timer:110 seconds remaining =================================================== Timer:109 seconds remaining =================================================== Timer:108 seconds remaining =================================================== Timer:107 seconds remaining =================================================== Timer:106 seconds remaining =================================================== Timer:105 seconds remaining =================================================== Timer:104 seconds remaining =================================================== Timer:103 seconds remaining =================================================== Timer:102 seconds remaining =================================================== Timer:101 seconds remaining =================================================== Timer:100 seconds remaining =================================================== Timer:99 seconds remaining =================================================== Timer:98 seconds remaining =================================================== Timer:97 seconds remaining =================================================== Timer:96 seconds remaining =================================================== Timer:95 seconds remaining =================================================== Timer:94 seconds remaining =================================================== Timer:93 seconds remaining =================================================== Timer:92 seconds remaining =================================================== Timer:91 seconds remaining =================================================== Timer:90 seconds remaining =================================================== Timer:89 seconds remaining =================================================== Timer:88 seconds remaining =================================================== Timer:87 seconds remaining =================================================== Timer:86 seconds remaining =================================================== Timer:85 seconds remaining =================================================== Timer:84 seconds remaining =================================================== Timer:83 seconds remaining =================================================== Timer:82 seconds remaining =================================================== Timer:81 seconds remaining =================================================== Timer:80 seconds remaining =================================================== Timer:79 seconds remaining =================================================== Timer:78 seconds remaining =================================================== Timer:77 seconds remaining =================================================== Timer:76 seconds remaining =================================================== Timer:75 seconds remaining =================================================== Timer:74 seconds remaining =================================================== Timer:73 seconds remaining =================================================== Timer:72 seconds remaining =================================================== Timer:71 seconds remaining =================================================== Timer:70 seconds remaining =================================================== Timer:69 seconds remaining =================================================== Timer:68 seconds remaining =================================================== Timer:67 seconds remaining =================================================== Timer:66 seconds remaining =================================================== Timer:65 seconds remaining =================================================== Timer:64 seconds remaining =================================================== Timer:63 seconds remaining =================================================== Timer:62 seconds remaining =================================================== Timer:61 seconds remaining =================================================== Timer:60 seconds remaining =================================================== Timer:59 seconds remaining =================================================== Timer:58 seconds remaining =================================================== Timer:57 seconds remaining =================================================== Timer:56 seconds remaining =================================================== Timer:55 seconds remaining =================================================== Timer:54 seconds remaining =================================================== Timer:53 seconds remaining =================================================== Timer:52 seconds remaining =================================================== Timer:51 seconds remaining =================================================== Timer:50 seconds remaining =================================================== Timer:49 seconds remaining =================================================== Timer:48 seconds remaining =================================================== Timer:47 seconds remaining =================================================== Timer:46 seconds remaining =================================================== Timer:45 seconds remaining =================================================== Timer:44 seconds remaining =================================================== Timer:43 seconds remaining =================================================== Timer:42 seconds remaining =================================================== Timer:41 seconds remaining =================================================== Timer:40 seconds remaining =================================================== Timer:39 seconds remaining =================================================== Timer:38 seconds remaining =================================================== Timer:37 seconds remaining =================================================== Timer:36 seconds remaining =================================================== Timer:35 seconds remaining =================================================== Timer:34 seconds remaining =================================================== Timer:33 seconds remaining =================================================== Timer:32 seconds remaining =================================================== Timer:31 seconds remaining =================================================== Timer:30 seconds remaining =================================================== Timer:29 seconds remaining =================================================== Timer:28 seconds remaining =================================================== Timer:27 seconds remaining =================================================== Timer:26 seconds remaining =================================================== Timer:25 seconds remaining =================================================== Timer:24 seconds remaining =================================================== Timer:23 seconds remaining =================================================== Timer:22 seconds remaining =================================================== Timer:21 seconds remaining =================================================== Timer:20 seconds remaining =================================================== Timer:19 seconds remaining =================================================== Timer:18 seconds remaining =================================================== Timer:17 seconds remaining =================================================== Timer:16 seconds remaining =================================================== Timer:15 seconds remaining =================================================== Timer:14 seconds remaining =================================================== Timer:13 seconds remaining =================================================== Timer:12 seconds remaining =================================================== Timer:11 seconds remaining =================================================== Timer:10 seconds remaining =================================================== Timer: 9 seconds remaining =================================================== Timer: 8 seconds remaining =================================================== Timer: 7 seconds remaining =================================================== Timer: 6 seconds remaining =================================================== Timer: 5 seconds remaining =================================================== Timer: 4 seconds remaining =================================================== Timer: 3 seconds remaining =================================================== Timer: 2 seconds remaining =================================================== Timer: 1 seconds remaining =======================
2019-10-11 11:03:19 :: configuring: config system global 
2019-10-11 11:03:20 :: configuring: set admintimeout 480 
2019-10-11 11:03:20 :: configuring: end 
2019-10-11 11:03:21 :: configuring: config system global 
2019-10-11 11:03:21 :: configuring: set admintimeout 480 
2019-10-11 11:03:22 :: configuring: end 
2019-10-11 11:03:22 :: configuring: config system interface 
2019-10-11 11:03:23 :: configuring: edit Agg-424D-1 
2019-10-11 11:03:23 :: configuring: set status down 
2019-10-11 11:03:24 :: configuring: end 
2019-10-11 11:03:26 :: configuring: config system interface 
2019-10-11 11:03:27 :: configuring: edit Agg-424D-1 
2019-10-11 11:03:27 :: configuring: set status up 
2019-10-11 11:03:28 :: configuring: end 
2019-10-11 11:03:30 :: =============== resetting all switches to factory default =========== 
after reset sleep 5 min
2019-10-11 11:03:46 :: ========================= Wait for 5 min after reset factory default ========================== 
============================ Timer:300 seconds remaining =================================================== Timer:299 seconds remaining =================================================== Timer:298 seconds remaining =================================================== Timer:297 seconds remaining =================================================== Timer:296 seconds remaining =================================================== Timer:295 seconds remaining =================================================== Timer:294 seconds remaining =================================================== Timer:293 seconds remaining =================================================== Timer:292 seconds remaining =================================================== Timer:291 seconds remaining =================================================== Timer:290 seconds remaining =================================================== Timer:289 seconds remaining =================================================== Timer:288 seconds remaining =================================================== Timer:287 seconds remaining =================================================== Timer:286 seconds remaining =================================================== Timer:285 seconds remaining =================================================== Timer:284 seconds remaining =================================================== Timer:283 seconds remaining =================================================== Timer:282 seconds remaining =================================================== Timer:281 seconds remaining =================================================== Timer:280 seconds remaining =================================================== Timer:279 seconds remaining =================================================== Timer:278 seconds remaining =================================================== Timer:277 seconds remaining =================================================== Timer:276 seconds remaining =================================================== Timer:275 seconds remaining =================================================== Timer:274 seconds remaining =================================================== Timer:273 seconds remaining =================================================== Timer:272 seconds remaining =================================================== Timer:271 seconds remaining =================================================== Timer:270 seconds remaining =================================================== Timer:269 seconds remaining =================================================== Timer:268 seconds remaining =================================================== Timer:267 seconds remaining =================================================== Timer:266 seconds remaining =================================================== Timer:265 seconds remaining =================================================== Timer:264 seconds remaining =================================================== Timer:263 seconds remaining =================================================== Timer:262 seconds remaining =================================================== Timer:261 seconds remaining =================================================== Timer:260 seconds remaining =================================================== Timer:259 seconds remaining =================================================== Timer:258 seconds remaining =================================================== Timer:257 seconds remaining =================================================== Timer:256 seconds remaining =================================================== Timer:255 seconds remaining =================================================== Timer:254 seconds remaining =================================================== Timer:253 seconds remaining =================================================== Timer:252 seconds remaining =================================================== Timer:251 seconds remaining =================================================== Timer:250 seconds remaining =================================================== Timer:249 seconds remaining =================================================== Timer:248 seconds remaining =================================================== Timer:247 seconds remaining =================================================== Timer:246 seconds remaining =================================================== Timer:245 seconds remaining =================================================== Timer:244 seconds remaining =================================================== Timer:243 seconds remaining =================================================== Timer:242 seconds remaining =================================================== Timer:241 seconds remaining =================================================== Timer:240 seconds remaining =================================================== Timer:239 seconds remaining =================================================== Timer:238 seconds remaining =================================================== Timer:237 seconds remaining =================================================== Timer:236 seconds remaining =================================================== Timer:235 seconds remaining =================================================== Timer:234 seconds remaining =================================================== Timer:233 seconds remaining =================================================== Timer:232 seconds remaining =================================================== Timer:231 seconds remaining =================================================== Timer:230 seconds remaining =================================================== Timer:229 seconds remaining =================================================== Timer:228 seconds remaining =================================================== Timer:227 seconds remaining =================================================== Timer:226 seconds remaining =================================================== Timer:225 seconds remaining =================================================== Timer:224 seconds remaining =================================================== Timer:223 seconds remaining =================================================== Timer:222 seconds remaining =================================================== Timer:221 seconds remaining =================================================== Timer:220 seconds remaining =================================================== Timer:219 seconds remaining =================================================== Timer:218 seconds remaining =================================================== Timer:217 seconds remaining =================================================== Timer:216 seconds remaining =================================================== Timer:215 seconds remaining =================================================== Timer:214 seconds remaining =================================================== Timer:213 seconds remaining =================================================== Timer:212 seconds remaining =================================================== Timer:211 seconds remaining =================================================== Timer:210 seconds remaining =================================================== Timer:209 seconds remaining =================================================== Timer:208 seconds remaining =================================================== Timer:207 seconds remaining =================================================== Timer:206 seconds remaining =================================================== Timer:205 seconds remaining =================================================== Timer:204 seconds remaining =================================================== Timer:203 seconds remaining =================================================== Timer:202 seconds remaining =================================================== Timer:201 seconds remaining =================================================== Timer:200 seconds remaining =================================================== Timer:199 seconds remaining =================================================== Timer:198 seconds remaining =================================================== Timer:197 seconds remaining =================================================== Timer:196 seconds remaining =================================================== Timer:195 seconds remaining =================================================== Timer:194 seconds remaining =================================================== Timer:193 seconds remaining =================================================== Timer:192 seconds remaining =================================================== Timer:191 seconds remaining =================================================== Timer:190 seconds remaining =================================================== Timer:189 seconds remaining =================================================== Timer:188 seconds remaining =================================================== Timer:187 seconds remaining =================================================== Timer:186 seconds remaining =================================================== Timer:185 seconds remaining =================================================== Timer:184 seconds remaining =================================================== Timer:183 seconds remaining =================================================== Timer:182 seconds remaining =================================================== Timer:181 seconds remaining =================================================== Timer:180 seconds remaining =================================================== Timer:179 seconds remaining =================================================== Timer:178 seconds remaining =================================================== Timer:177 seconds remaining =================================================== Timer:176 seconds remaining =================================================== Timer:175 seconds remaining =================================================== Timer:174 seconds remaining =================================================== Timer:173 seconds remaining =================================================== Timer:172 seconds remaining =================================================== Timer:171 seconds remaining =================================================== Timer:170 seconds remaining =================================================== Timer:169 seconds remaining =================================================== Timer:168 seconds remaining =================================================== Timer:167 seconds remaining =================================================== Timer:166 seconds remaining =================================================== Timer:165 seconds remaining =================================================== Timer:164 seconds remaining =================================================== Timer:163 seconds remaining =================================================== Timer:162 seconds remaining =================================================== Timer:161 seconds remaining =================================================== Timer:160 seconds remaining =================================================== Timer:159 seconds remaining =================================================== Timer:158 seconds remaining =================================================== Timer:157 seconds remaining =================================================== Timer:156 seconds remaining =================================================== Timer:155 seconds remaining =================================================== Timer:154 seconds remaining =================================================== Timer:153 seconds remaining =================================================== Timer:152 seconds remaining =================================================== Timer:151 seconds remaining =================================================== Timer:150 seconds remaining =================================================== Timer:149 seconds remaining =================================================== Timer:148 seconds remaining =================================================== Timer:147 seconds remaining =================================================== Timer:146 seconds remaining =================================================== Timer:145 seconds remaining =================================================== Timer:144 seconds remaining =================================================== Timer:143 seconds remaining =================================================== Timer:142 seconds remaining =================================================== Timer:141 seconds remaining =================================================== Timer:140 seconds remaining =================================================== Timer:139 seconds remaining =================================================== Timer:138 seconds remaining =================================================== Timer:137 seconds remaining =================================================== Timer:136 seconds remaining =================================================== Timer:135 seconds remaining =================================================== Timer:134 seconds remaining =================================================== Timer:133 seconds remaining =================================================== Timer:132 seconds remaining =================================================== Timer:131 seconds remaining =================================================== Timer:130 seconds remaining =================================================== Timer:129 seconds remaining =================================================== Timer:128 seconds remaining =================================================== Timer:127 seconds remaining =================================================== Timer:126 seconds remaining =================================================== Timer:125 seconds remaining =================================================== Timer:124 seconds remaining =================================================== Timer:123 seconds remaining =================================================== Timer:122 seconds remaining =================================================== Timer:121 seconds remaining =================================================== Timer:120 seconds remaining =================================================== Timer:119 seconds remaining =================================================== Timer:118 seconds remaining =================================================== Timer:117 seconds remaining =================================================== Timer:116 seconds remaining =================================================== Timer:115 seconds remaining =================================================== Timer:114 seconds remaining =================================================== Timer:113 seconds remaining =================================================== Timer:112 seconds remaining =================================================== Timer:111 seconds remaining =================================================== Timer:110 seconds remaining =================================================== Timer:109 seconds remaining =================================================== Timer:108 seconds remaining =================================================== Timer:107 seconds remaining =================================================== Timer:106 seconds remaining =================================================== Timer:105 seconds remaining =================================================== Timer:104 seconds remaining =================================================== Timer:103 seconds remaining =================================================== Timer:102 seconds remaining =================================================== Timer:101 seconds remaining =================================================== Timer:100 seconds remaining =================================================== Timer:99 seconds remaining =================================================== Timer:98 seconds remaining =================================================== Timer:97 seconds remaining =================================================== Timer:96 seconds remaining =================================================== Timer:95 seconds remaining =================================================== Timer:94 seconds remaining =================================================== Timer:93 seconds remaining =================================================== Timer:92 seconds remaining =================================================== Timer:91 seconds remaining =================================================== Timer:90 seconds remaining =================================================== Timer:89 seconds remaining =================================================== Timer:88 seconds remaining =================================================== Timer:87 seconds remaining =================================================== Timer:86 seconds remaining =================================================== Timer:85 seconds remaining =================================================== Timer:84 seconds remaining =================================================== Timer:83 seconds remaining =================================================== Timer:82 seconds remaining =================================================== Timer:81 seconds remaining =================================================== Timer:80 seconds remaining =================================================== Timer:79 seconds remaining =================================================== Timer:78 seconds remaining =================================================== Timer:77 seconds remaining =================================================== Timer:76 seconds remaining =================================================== Timer:75 seconds remaining =================================================== Timer:74 seconds remaining =================================================== Timer:73 seconds remaining =================================================== Timer:72 seconds remaining =================================================== Timer:71 seconds remaining =================================================== Timer:70 seconds remaining =================================================== Timer:69 seconds remaining =================================================== Timer:68 seconds remaining =================================================== Timer:67 seconds remaining =================================================== Timer:66 seconds remaining =================================================== Timer:65 seconds remaining =================================================== Timer:64 seconds remaining =================================================== Timer:63 seconds remaining =================================================== Timer:62 seconds remaining =================================================== Timer:61 seconds remaining =================================================== Timer:60 seconds remaining =================================================== Timer:59 seconds remaining =================================================== Timer:58 seconds remaining =================================================== Timer:57 seconds remaining =================================================== Timer:56 seconds remaining =================================================== Timer:55 seconds remaining =================================================== Timer:54 seconds remaining =================================================== Timer:53 seconds remaining =================================================== Timer:52 seconds remaining =================================================== Timer:51 seconds remaining =================================================== Timer:50 seconds remaining =================================================== Timer:49 seconds remaining =================================================== Timer:48 seconds remaining =================================================== Timer:47 seconds remaining =================================================== Timer:46 seconds remaining =================================================== Timer:45 seconds remaining =================================================== Timer:44 seconds remaining =================================================== Timer:43 seconds remaining =================================================== Timer:42 seconds remaining =================================================== Timer:41 seconds remaining =================================================== Timer:40 seconds remaining =================================================== Timer:39 seconds remaining =================================================== Timer:38 seconds remaining =================================================== Timer:37 seconds remaining =================================================== Timer:36 seconds remaining =================================================== Timer:35 seconds remaining =================================================== Timer:34 seconds remaining =================================================== Timer:33 seconds remaining =================================================== Timer:32 seconds remaining =================================================== Timer:31 seconds remaining =================================================== Timer:30 seconds remaining =================================================== Timer:29 seconds remaining =================================================== Timer:28 seconds remaining =================================================== Timer:27 seconds remaining =================================================== Timer:26 seconds remaining =================================================== Timer:25 seconds remaining =================================================== Timer:24 seconds remaining =================================================== Timer:23 seconds remaining =================================================== Timer:22 seconds remaining =================================================== Timer:21 seconds remaining =================================================== Timer:20 seconds remaining =================================================== Timer:19 seconds remaining =================================================== Timer:18 seconds remaining =================================================== Timer:17 seconds remaining =================================================== Timer:16 seconds remaining =================================================== Timer:15 seconds remaining =================================================== Timer:14 seconds remaining =================================================== Timer:13 seconds remaining =================================================== Timer:12 seconds remaining =================================================== Timer:11 seconds remaining =================================================== Timer:10 seconds remaining =================================================== Timer: 9 seconds remaining =================================================== Timer: 8 seconds remaining =================================================== Timer: 7 seconds remaining =================================================== Timer: 6 seconds remaining =================================================== Timer: 5 seconds remaining =================================================== Timer: 4 seconds remaining =================================================== Timer: 3 seconds remaining =================================================== Timer: 2 seconds remaining =================================================== Timer: 1 seconds remaining =======================
after sleep, relogin, should change password 
2019-10-11 11:08:47 :: -------------------- re-login Fortigate devices after factory rest----------------------- 
2019-10-11 11:08:47 :: console server ip =10.105.50.3 
2019-10-11 11:08:47 :: console port=2057 
2019-10-11 11:08:47 :: !!!!!!!!!!!the console is being used, need to clear it first 
Trying to clear line on comm_server: 10.105.50.3 port: 2057
login sucessfully into 10.105.50.3
2019-10-11 11:08:59 :: Info: This first time login to image not allowing blank password, password has been changed to <admin> 


2019-10-11 11:08:59 :: configuring: config system global 
2019-10-11 11:09:00 :: configuring: set admintimeout 480 
2019-10-11 11:09:00 :: configuring: end 
2019-10-11 11:09:01 :: get_switch_telnet_connection_new: Login sucessful!
 
2019-10-11 11:09:01 :: console server ip =10.105.50.3 
2019-10-11 11:09:01 :: console port=2056 
2019-10-11 11:09:01 :: !!!!!!!!!!!the console is being used, need to clear it first 
Trying to clear line on comm_server: 10.105.50.3 port: 2056
login sucessfully into 10.105.50.3
2019-10-11 11:09:09 :: Info: This first time login to image not allowing blank password, password has been changed to <admin> 


2019-10-11 11:09:09 :: configuring: config system global 
2019-10-11 11:09:10 :: configuring: set admintimeout 480 
2019-10-11 11:09:10 :: configuring: end 
2019-10-11 11:09:11 :: get_switch_telnet_connection_new: Login sucessful!
 
2019-10-11 11:09:11 :: console server ip =10.105.50.1 
2019-10-11 11:09:11 :: console port=2075 
2019-10-11 11:09:11 :: !!!!!!!!!!!the console is being used, need to clear it first 
Trying to clear line on comm_server: 10.105.50.1 port: 2075
login sucessfully into 10.105.50.1
2019-10-11 11:09:19 :: Info: This first time login to image not allowing blank password, password has been changed to <admin> 


2019-10-11 11:09:19 :: configuring: config system global 
2019-10-11 11:09:19 :: configuring: set admintimeout 480 
2019-10-11 11:09:20 :: configuring: end 
2019-10-11 11:09:20 :: get_switch_telnet_connection_new: Login sucessful!
 
2019-10-11 11:09:20 :: console server ip =10.105.50.1 
2019-10-11 11:09:20 :: console port=2078 
2019-10-11 11:09:20 :: !!!!!!!!!!!the console is being used, need to clear it first 
Trying to clear line on comm_server: 10.105.50.1 port: 2078
login sucessfully into 10.105.50.1
2019-10-11 11:09:33 :: Info: This first time login to image not allowing blank password, password has been changed to <admin> 


2019-10-11 11:09:33 :: configuring: config system global 
2019-10-11 11:09:33 :: configuring: set admintimeout 480 
2019-10-11 11:09:34 :: configuring: end 
2019-10-11 11:09:34 :: get_switch_telnet_connection_new: Login sucessful!
 
2019-10-11 11:09:34 ::  -------------- After factory reset, find out FSW images ------------------------ 
2019-10-11 11:09:36 :: ============================ dut1-548d software image = v6.2.0,build0190,191001 (Interim)================ 
2019-10-11 11:09:38 :: ============================ dut2-548d software image = v6.2.0,build0190,191001 (Interim)================ 
2019-10-11 11:09:40 :: ============================ dut3-548d software image = v6.2.0,build0190,191001 (Interim)================ 
2019-10-11 11:09:42 :: ============================ dut4-548d software image = v6.2.0,build0190,191001 (Interim)================ 
2019-10-11 11:09:42 :: ------------ configure port lldp profile to auto-isl -------------------- 
2019-10-11 11:09:42 :: configuring dut1-548d: config switch physical-port 
2019-10-11 11:09:43 :: configuring dut1-548d: edit port1 
2019-10-11 11:09:43 :: configuring dut1-548d: set lldp-profile default-auto-isl 
2019-10-11 11:09:44 :: configuring dut1-548d: next 
2019-10-11 11:09:44 :: configuring dut1-548d: edit port2 
2019-10-11 11:09:45 :: configuring dut1-548d: set lldp-profile default-auto-isl 
2019-10-11 11:09:45 :: configuring dut1-548d: next 
2019-10-11 11:09:46 :: configuring dut1-548d: edit port3 
2019-10-11 11:09:46 :: configuring dut1-548d: set lldp-profile default-auto-isl 
2019-10-11 11:09:47 :: configuring dut1-548d: next 
2019-10-11 11:09:47 :: configuring dut1-548d: edit port4 
2019-10-11 11:09:48 :: configuring dut1-548d: set lldp-profile default-auto-isl 
2019-10-11 11:09:48 :: configuring dut1-548d: next 
2019-10-11 11:09:49 :: configuring dut1-548d: end 
2019-10-11 11:09:49 :: configuring dut2-548d: config switch physical-port 
2019-10-11 11:09:50 :: configuring dut2-548d: edit port1 
2019-10-11 11:09:50 :: configuring dut2-548d: set lldp-profile default-auto-isl 
2019-10-11 11:09:51 :: configuring dut2-548d: next 
2019-10-11 11:09:51 :: configuring dut2-548d: edit port2 
2019-10-11 11:09:52 :: configuring dut2-548d: set lldp-profile default-auto-isl 
2019-10-11 11:09:52 :: configuring dut2-548d: next 
2019-10-11 11:09:53 :: configuring dut2-548d: edit port3 
2019-10-11 11:09:53 :: configuring dut2-548d: set lldp-profile default-auto-isl 
2019-10-11 11:09:54 :: configuring dut2-548d: next 
2019-10-11 11:09:54 :: configuring dut2-548d: edit port4 
2019-10-11 11:09:55 :: configuring dut2-548d: set lldp-profile default-auto-isl 
2019-10-11 11:09:55 :: configuring dut2-548d: next 
2019-10-11 11:09:56 :: configuring dut2-548d: end 
2019-10-11 11:09:56 :: configuring dut3-548d: config switch physical-port 
2019-10-11 11:09:57 :: configuring dut3-548d: edit port1 
2019-10-11 11:09:57 :: configuring dut3-548d: set lldp-profile default-auto-isl 
2019-10-11 11:09:58 :: configuring dut3-548d: next 
2019-10-11 11:09:58 :: configuring dut3-548d: edit port2 
2019-10-11 11:09:59 :: configuring dut3-548d: set lldp-profile default-auto-isl 
2019-10-11 11:09:59 :: configuring dut3-548d: next 
2019-10-11 11:10:00 :: configuring dut3-548d: edit port3 
2019-10-11 11:10:00 :: configuring dut3-548d: set lldp-profile default-auto-isl 
2019-10-11 11:10:01 :: configuring dut3-548d: next 
2019-10-11 11:10:01 :: configuring dut3-548d: edit port4 
2019-10-11 11:10:02 :: configuring dut3-548d: set lldp-profile default-auto-isl 
2019-10-11 11:10:02 :: configuring dut3-548d: next 
2019-10-11 11:10:03 :: configuring dut3-548d: end 
2019-10-11 11:10:03 :: configuring dut4-548d: config switch physical-port 
2019-10-11 11:10:04 :: configuring dut4-548d: edit port1 
2019-10-11 11:10:04 :: configuring dut4-548d: set lldp-profile default-auto-isl 
2019-10-11 11:10:05 :: configuring dut4-548d: next 
2019-10-11 11:10:05 :: configuring dut4-548d: edit port2 
2019-10-11 11:10:06 :: configuring dut4-548d: set lldp-profile default-auto-isl 
2019-10-11 11:10:06 :: configuring dut4-548d: next 
2019-10-11 11:10:07 :: configuring dut4-548d: edit port3 
2019-10-11 11:10:07 :: configuring dut4-548d: set lldp-profile default-auto-isl 
2019-10-11 11:10:08 :: configuring dut4-548d: next 
2019-10-11 11:10:08 :: configuring dut4-548d: edit port4 
2019-10-11 11:10:09 :: configuring dut4-548d: set lldp-profile default-auto-isl 
2019-10-11 11:10:09 :: configuring dut4-548d: next 
2019-10-11 11:10:10 :: configuring dut4-548d: end 
2019-10-11 11:10:10 :: ------------  After configuring lldp profile to auto-isl, wait for 180 seconds  -------------------- 
============================ Timer:180 seconds remaining =================================================== Timer:179 seconds remaining =================================================== Timer:178 seconds remaining =================================================== Timer:177 seconds remaining =================================================== Timer:176 seconds remaining =================================================== Timer:175 seconds remaining =================================================== Timer:174 seconds remaining =================================================== Timer:173 seconds remaining =================================================== Timer:172 seconds remaining =================================================== Timer:171 seconds remaining =================================================== Timer:170 seconds remaining =================================================== Timer:169 seconds remaining =================================================== Timer:168 seconds remaining =================================================== Timer:167 seconds remaining =================================================== Timer:166 seconds remaining =================================================== Timer:165 seconds remaining =================================================== Timer:164 seconds remaining =================================================== Timer:163 seconds remaining =================================================== Timer:162 seconds remaining =================================================== Timer:161 seconds remaining =================================================== Timer:160 seconds remaining =================================================== Timer:159 seconds remaining =================================================== Timer:158 seconds remaining =================================================== Timer:157 seconds remaining =================================================== Timer:156 seconds remaining =================================================== Timer:155 seconds remaining =================================================== Timer:154 seconds remaining =================================================== Timer:153 seconds remaining =================================================== Timer:152 seconds remaining =================================================== Timer:151 seconds remaining =================================================== Timer:150 seconds remaining =================================================== Timer:149 seconds remaining =================================================== Timer:148 seconds remaining =================================================== Timer:147 seconds remaining =================================================== Timer:146 seconds remaining =================================================== Timer:145 seconds remaining =================================================== Timer:144 seconds remaining =================================================== Timer:143 seconds remaining =================================================== Timer:142 seconds remaining =================================================== Timer:141 seconds remaining =================================================== Timer:140 seconds remaining =================================================== Timer:139 seconds remaining =================================================== Timer:138 seconds remaining =================================================== Timer:137 seconds remaining =================================================== Timer:136 seconds remaining =================================================== Timer:135 seconds remaining =================================================== Timer:134 seconds remaining =================================================== Timer:133 seconds remaining =================================================== Timer:132 seconds remaining =================================================== Timer:131 seconds remaining =================================================== Timer:130 seconds remaining =================================================== Timer:129 seconds remaining =================================================== Timer:128 seconds remaining =================================================== Timer:127 seconds remaining =================================================== Timer:126 seconds remaining =================================================== Timer:125 seconds remaining =================================================== Timer:124 seconds remaining =================================================== Timer:123 seconds remaining =================================================== Timer:122 seconds remaining =================================================== Timer:121 seconds remaining =================================================== Timer:120 seconds remaining =================================================== Timer:119 seconds remaining =================================================== Timer:118 seconds remaining =================================================== Timer:117 seconds remaining =================================================== Timer:116 seconds remaining =================================================== Timer:115 seconds remaining =================================================== Timer:114 seconds remaining =================================================== Timer:113 seconds remaining =================================================== Timer:112 seconds remaining =================================================== Timer:111 seconds remaining =================================================== Timer:110 seconds remaining =================================================== Timer:109 seconds remaining =================================================== Timer:108 seconds remaining =================================================== Timer:107 seconds remaining =================================================== Timer:106 seconds remaining =================================================== Timer:105 seconds remaining =================================================== Timer:104 seconds remaining =================================================== Timer:103 seconds remaining =================================================== Timer:102 seconds remaining =================================================== Timer:101 seconds remaining =================================================== Timer:100 seconds remaining =================================================== Timer:99 seconds remaining =================================================== Timer:98 seconds remaining =================================================== Timer:97 seconds remaining =================================================== Timer:96 seconds remaining =================================================== Timer:95 seconds remaining =================================================== Timer:94 seconds remaining =================================================== Timer:93 seconds remaining =================================================== Timer:92 seconds remaining =================================================== Timer:91 seconds remaining =================================================== Timer:90 seconds remaining =================================================== Timer:89 seconds remaining =================================================== Timer:88 seconds remaining =================================================== Timer:87 seconds remaining =================================================== Timer:86 seconds remaining =================================================== Timer:85 seconds remaining =================================================== Timer:84 seconds remaining =================================================== Timer:83 seconds remaining =================================================== Timer:82 seconds remaining =================================================== Timer:81 seconds remaining =================================================== Timer:80 seconds remaining =================================================== Timer:79 seconds remaining =================================================== Timer:78 seconds remaining =================================================== Timer:77 seconds remaining =================================================== Timer:76 seconds remaining =================================================== Timer:75 seconds remaining =================================================== Timer:74 seconds remaining =================================================== Timer:73 seconds remaining =================================================== Timer:72 seconds remaining =================================================== Timer:71 seconds remaining =================================================== Timer:70 seconds remaining =================================================== Timer:69 seconds remaining =================================================== Timer:68 seconds remaining =================================================== Timer:67 seconds remaining =================================================== Timer:66 seconds remaining =================================================== Timer:65 seconds remaining =================================================== Timer:64 seconds remaining =================================================== Timer:63 seconds remaining =================================================== Timer:62 seconds remaining =================================================== Timer:61 seconds remaining =================================================== Timer:60 seconds remaining =================================================== Timer:59 seconds remaining =================================================== Timer:58 seconds remaining =================================================== Timer:57 seconds remaining =================================================== Timer:56 seconds remaining =================================================== Timer:55 seconds remaining =================================================== Timer:54 seconds remaining =================================================== Timer:53 seconds remaining =================================================== Timer:52 seconds remaining =================================================== Timer:51 seconds remaining =================================================== Timer:50 seconds remaining =================================================== Timer:49 seconds remaining =================================================== Timer:48 seconds remaining =================================================== Timer:47 seconds remaining =================================================== Timer:46 seconds remaining =================================================== Timer:45 seconds remaining =================================================== Timer:44 seconds remaining =================================================== Timer:43 seconds remaining =================================================== Timer:42 seconds remaining =================================================== Timer:41 seconds remaining =================================================== Timer:40 seconds remaining =================================================== Timer:39 seconds remaining =================================================== Timer:38 seconds remaining =================================================== Timer:37 seconds remaining =================================================== Timer:36 seconds remaining =================================================== Timer:35 seconds remaining =================================================== Timer:34 seconds remaining =================================================== Timer:33 seconds remaining =================================================== Timer:32 seconds remaining =================================================== Timer:31 seconds remaining =================================================== Timer:30 seconds remaining =================================================== Timer:29 seconds remaining =================================================== Timer:28 seconds remaining =================================================== Timer:27 seconds remaining =================================================== Timer:26 seconds remaining =================================================== Timer:25 seconds remaining =================================================== Timer:24 seconds remaining =================================================== Timer:23 seconds remaining =================================================== Timer:22 seconds remaining =================================================== Timer:21 seconds remaining =================================================== Timer:20 seconds remaining =================================================== Timer:19 seconds remaining =================================================== Timer:18 seconds remaining =================================================== Timer:17 seconds remaining =================================================== Timer:16 seconds remaining =================================================== Timer:15 seconds remaining =================================================== Timer:14 seconds remaining =================================================== Timer:13 seconds remaining =================================================== Timer:12 seconds remaining =================================================== Timer:11 seconds remaining =================================================== Timer:10 seconds remaining =================================================== Timer: 9 seconds remaining =================================================== Timer: 8 seconds remaining =================================================== Timer: 7 seconds remaining =================================================== Timer: 6 seconds remaining =================================================== Timer: 5 seconds remaining =================================================== Timer: 4 seconds remaining =================================================== Timer: 3 seconds remaining =================================================== Timer: 2 seconds remaining =================================================== Timer: 1 seconds remaining =======================
2019-10-11 11:13:54 :: configuring: config system global 
2019-10-11 11:13:55 :: configuring: set admintimeout 480 
2019-10-11 11:13:55 :: configuring: end 
2019-10-11 11:13:56 :: configuring: config system global 
2019-10-11 11:13:56 :: configuring: set admintimeout 480 
2019-10-11 11:13:57 :: configuring: end 
2019-10-11 11:13:57 :: configuring: config system global 
2019-10-11 11:13:58 :: configuring: set admintimeout 480 
2019-10-11 11:13:58 :: configuring: end 
2019-10-11 11:13:59 :: configuring: config system global 
2019-10-11 11:13:59 :: configuring: set admintimeout 480 
2019-10-11 11:14:00 :: configuring: end 
2019-10-11 11:14:02 :: ============================ dut4-548d software image = v6.2.0,build0190,191001 (Interim)================ 
2019-10-11 11:14:04 :: ============================ dut4-548d software image = v6.2.0,build0190,191001 (Interim)================ 
2019-10-11 11:14:06 :: ============================ dut4-548d software image = v6.2.0,build0190,191001 (Interim)================ 
2019-10-11 11:14:08 :: ============================ dut4-548d software image = v6.2.0,build0190,191001 (Interim)================ 
2019-10-11 11:14:29 :: Configuring MCLAG-ICL, if icl trunk is not found, maybe auto-discovery is not done yet 
2019-10-11 11:14:31 :: Info: ICL ports = ['port47', 'port48'] 


2019-10-11 11:14:31 :: configuring dut1-548d: config switch trunk 
2019-10-11 11:14:31 :: configuring dut1-548d: edit 8DF4K17000028-0 
2019-10-11 11:14:32 :: configuring dut1-548d: set mclag-icl enable 
2019-10-11 11:14:32 :: configuring dut1-548d: end 
2019-10-11 11:14:37 :: show switch trunk 
2019-10-11 11:14:37 :: config switch trunk 
2019-10-11 11:14:37 ::     edit "704CA5CBC3DC-0" 
2019-10-11 11:14:37 ::         set mode lacp-active 
2019-10-11 11:14:37 ::         set auto-isl 1 
2019-10-11 11:14:37 ::         set isl-fortilink 1 
2019-10-11 11:14:37 ::         set mclag enable 
2019-10-11 11:14:37 ::             set members "port50" 
2019-10-11 11:14:37 ::     next 
2019-10-11 11:14:37 ::     edit "8DF4K17000028-0" 
2019-10-11 11:14:37 ::         set mode lacp-active 
2019-10-11 11:14:37 ::         set auto-isl 1 
2019-10-11 11:14:37 ::         set mclag-icl enable 
2019-10-11 11:14:37 ::             set members "port47" "port48" 
2019-10-11 11:14:37 ::     next 
2019-10-11 11:14:37 ::     edit "704CA5A8FCFA-0" 
2019-10-11 11:14:37 ::         set mode lacp-active 
2019-10-11 11:14:37 ::         set auto-isl 1 
2019-10-11 11:14:37 ::         set isl-fortilink 1 
2019-10-11 11:14:37 ::         set mclag enable 
2019-10-11 11:14:37 ::             set members "port49" 
2019-10-11 11:14:37 ::     next 
2019-10-11 11:14:37 ::     edit "sw1-trunk" 
2019-10-11 11:14:37 ::         set mode lacp-active 
2019-10-11 11:14:37 ::         set mclag enable 
2019-10-11 11:14:37 :: --More--                      set members "port13" 
2019-10-11 11:14:37 ::     next 
2019-10-11 11:14:37 ::     edit "8DF4K16000653-0" 
2019-10-11 11:14:37 ::         set mode lacp-active 
2019-10-11 11:14:37 ::         set auto-isl 1 
2019-10-11 11:14:37 ::         set mclag enable 
2019-10-11 11:14:37 ::             set members "port1" "port2" 
2019-10-11 11:14:37 ::     next 
2019-10-11 11:14:37 ::     edit "8DN4K17000133-0" 
2019-10-11 11:14:37 ::         set mode lacp-active 
2019-10-11 11:14:37 ::         set auto-isl 1 
2019-10-11 11:14:37 ::         set mclag enable 
2019-10-11 11:14:37 ::             set members "port3" "port4" 
2019-10-11 11:14:37 ::     next 
2019-10-11 11:14:37 :: end 
2019-10-11 11:14:37 ::  
2019-10-11 11:14:37 :: S548DF4K17000014 # 
2019-10-11 11:14:39 :: Info: mclag-icl is configured correctly at dut1-548d 


2019-10-11 11:14:39 :: configuring dut1-548d: config switch auto-isl-port-group 
2019-10-11 11:14:39 :: configuring dut1-548d: edit core1 
2019-10-11 11:14:40 :: configuring dut1-548d: set members port1 port2 port3 port4 
2019-10-11 11:14:40 :: configuring dut1-548d: end 
2019-10-11 11:15:01 :: Configuring MCLAG-ICL, if icl trunk is not found, maybe auto-discovery is not done yet 
2019-10-11 11:15:03 :: Info: ICL ports = ['port47', 'port48'] 


2019-10-11 11:15:03 :: configuring dut2-548d: config switch trunk 
2019-10-11 11:15:04 :: configuring dut2-548d: edit 8DF4K17000014-0 
2019-10-11 11:15:04 :: configuring dut2-548d: set mclag-icl enable 
2019-10-11 11:15:05 :: configuring dut2-548d: end 
2019-10-11 11:15:09 :: show switch trunk 
2019-10-11 11:15:09 :: config switch trunk 
2019-10-11 11:15:09 ::     edit "8DF4K17000014-0" 
2019-10-11 11:15:09 ::         set mode lacp-active 
2019-10-11 11:15:09 ::         set auto-isl 1 
2019-10-11 11:15:09 ::         set mclag-icl enable 
2019-10-11 11:15:09 ::             set members "port47" "port48" 
2019-10-11 11:15:09 ::     next 
2019-10-11 11:15:09 ::     edit "704CA5A8FCFA-0" 
2019-10-11 11:15:09 ::         set mode lacp-active 
2019-10-11 11:15:09 ::         set auto-isl 1 
2019-10-11 11:15:09 ::         set isl-fortilink 1 
2019-10-11 11:15:09 ::         set mclag enable 
2019-10-11 11:15:09 ::             set members "port49" 
2019-10-11 11:15:09 ::     next 
2019-10-11 11:15:09 ::     edit "704CA5CBC3DC-0" 
2019-10-11 11:15:09 ::         set mode lacp-active 
2019-10-11 11:15:09 ::         set auto-isl 1 
2019-10-11 11:15:09 ::         set isl-fortilink 1 
2019-10-11 11:15:09 ::         set mclag enable 
2019-10-11 11:15:09 ::             set members "port50" 
2019-10-11 11:15:09 ::     next 
2019-10-11 11:15:09 ::     edit "sw1-trunk" 
2019-10-11 11:15:09 ::         set mode lacp-active 
2019-10-11 11:15:09 ::         set mclag enable 
2019-10-11 11:15:09 :: --More--                      set members "port13" 
2019-10-11 11:15:09 ::     next 
2019-10-11 11:15:09 ::     edit "8DF4K16000653-0" 
2019-10-11 11:15:09 ::         set mode lacp-active 
2019-10-11 11:15:09 ::         set auto-isl 1 
2019-10-11 11:15:09 ::         set mclag enable 
2019-10-11 11:15:09 ::             set members "port3" "port4" 
2019-10-11 11:15:09 ::     next 
2019-10-11 11:15:09 ::     edit "8DN4K17000133-0" 
2019-10-11 11:15:09 ::         set mode lacp-active 
2019-10-11 11:15:09 ::         set auto-isl 1 
2019-10-11 11:15:09 ::         set mclag enable 
2019-10-11 11:15:09 ::             set members "port1" "port2" 
2019-10-11 11:15:09 ::     next 
2019-10-11 11:15:09 :: end 
2019-10-11 11:15:09 ::  
2019-10-11 11:15:09 :: S548DF4K17000028 # 
2019-10-11 11:15:11 :: Info: mclag-icl is configured correctly at dut2-548d 


2019-10-11 11:15:11 :: configuring dut2-548d: config switch auto-isl-port-group 
2019-10-11 11:15:12 :: configuring dut2-548d: edit core1 
2019-10-11 11:15:12 :: configuring dut2-548d: set members port1 port2 port3 port4 
2019-10-11 11:15:13 :: configuring dut2-548d: end 
2019-10-11 11:15:34 :: Configuring MCLAG-ICL, if icl trunk is not found, maybe auto-discovery is not done yet 
2019-10-11 11:15:36 :: Info: ICL ports = ['port47', 'port48'] 


2019-10-11 11:15:36 :: configuring dut3-548d: config switch trunk 
2019-10-11 11:15:36 :: configuring dut3-548d: edit 8DN4K17000133-0 
2019-10-11 11:15:37 :: configuring dut3-548d: set mclag-icl enable 
2019-10-11 11:15:37 :: configuring dut3-548d: end 
2019-10-11 11:15:42 :: show switch trunk 
2019-10-11 11:15:42 :: config switch trunk 
2019-10-11 11:15:42 ::     edit "8DN4K17000133-0" 
2019-10-11 11:15:42 ::         set mode lacp-active 
2019-10-11 11:15:42 ::         set auto-isl 1 
2019-10-11 11:15:42 ::         set mclag-icl enable 
2019-10-11 11:15:42 ::             set members "port47" "port48" 
2019-10-11 11:15:42 ::     next 
2019-10-11 11:15:42 ::     edit "trunk1" 
2019-10-11 11:15:42 ::         set mode lacp-active 
2019-10-11 11:15:42 ::         set mclag enable 
2019-10-11 11:15:42 ::             set members "port13" 
2019-10-11 11:15:42 ::     next 
2019-10-11 11:15:42 ::     edit "8DF4K17000028-0" 
2019-10-11 11:15:42 ::         set mode lacp-active 
2019-10-11 11:15:42 ::         set auto-isl 1 
2019-10-11 11:15:42 ::         set mclag enable 
2019-10-11 11:15:42 ::             set members "port3" "port4" 
2019-10-11 11:15:42 ::     next 
2019-10-11 11:15:42 ::     edit "_FlInK1_MLAG0_" 
2019-10-11 11:15:42 ::         set mode lacp-active 
2019-10-11 11:15:42 ::         set auto-isl 1 
2019-10-11 11:15:42 ::         set mclag enable 
2019-10-11 11:15:42 ::             set members "port1" "port2" 
2019-10-11 11:15:42 ::     next 
2019-10-11 11:15:42 :: --More-- 
2019-10-11 11:15:44 :: Error: mclag-icl is not configured properly at dut3-548d and need to re-do 
2019-10-11 11:15:44 :: Executing command: execute log filter start-line 1 
2019-10-11 11:15:44 :: Executing command: execute log filter view-lines 1000 
2019-10-11 11:15:47 :: execute log display 
2019-10-11 11:15:47 :: execute log display 
2019-10-11 11:15:47 :: 50 logs found. 
2019-10-11 11:15:47 :: 50 logs returned. 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 1: 2019-10-11 11:15:44 log_id=0105008255 type=event subtype=spanning_tree pri=notice vd=root user="stp_daemon" action=role-change unit="primary" switch.physical-port="_FlInK1_MLAG0_" instanceid="15" event="role migration" oldrole="designated" newrole="disabled" msg="primary port _FlInK1_MLAG0_ instance 15 changed role from designated to disabled" 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 2: 2019-10-11 11:15:44 log_id=0105008255 type=event subtype=spanning_tree pri=notice vd=root user="stp_daemon" action=state-change unit="primary" switch.physical-port="8DF4K17000028-0" instanceid="0" event="state migration" oldstate="learning" newstate="forwarding" msg="primary port 8DF4K17000028-0 instance 0 changed state from learning to forwarding" 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 3: 2019-10-11 11:15:44 log_id=0105008255 type=event subtype=spanning_tree pri=notice vd=root user="__switch_stp_port_set_state" inst_id="0" intf_id="2051" member_port="4" stp_state="4" hw_state="4" 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 4: 2019-10-11 11:15:44 log_id=0105008255 type=event subtype=spanning_tree pri=notice vd=root user="__switch_stp_port_set_state" inst_id="0" intf_id="2051" member_port="3" stp_state="4" hw_state="4" 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 5: 2019-10-11 11:15:44 log_id=0105008255 type=event subtype=spanning_tree pri=notice vd=root user="stp_daemon" action=state-change unit="primary" switch.physical-port="8DF4K17000028-0" instanceid="0" event="state migration" oldstate="discarding" newstate="learning" msg="primary port 8DF4K17000028-0 instance 0 changed state from discarding to learning" 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 6: 2019-10-11 11:15:44 log_id=0105008255 type=event subtype=spanning_tree pri=notice vd=root user="stp_daemon" action=role-change unit="primary" switch.physical-port="8DF4K17000028-0" instanceid="0" event="role migration" oldrole="alternative" newrole="root" msg="primary port 8DF4K17000028-0 instance 0 changed role from alternative to root" 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 7: 2019-10-11 11:15:44 log_id=0105008255 type=event subtype=spanning_tree pri=notice vd=root user="stp_daemon" action=state-change unit="primary" switch.physical-port="_FlInK1_MLAG0_" instanceid="0" event="state migration" oldstate="forwarding" newstate="discarding" msg="primary port _FlInK1_MLAG0_ instance 0 changed state from forwarding to discarding" 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 8: 2019-10-11 11:15:44 log_id=0105008255 type=event subtype=spanning_tree pri=notice vd=root user="stp_daemon" action=role-change unit="primary" switch.physical-port="_FlInK1_MLAG0_" instanceid="0" event="role migration" oldrole="root" newrole="disabled" msg="primary port _FlInK1_MLAG0_ instance 0 changed role from root to disabled" 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 9: 2019-10-11 11:15:44 log_id=0106009008 type=event subtype=switch_controller pri=notice vd=root msg="FortiLink: ISL timing-out for trunk(8DF4K17000028-0) member port(4) did not receive ISL pkt for(30) sec" 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 10: 2019-10-11 11:15:44 log_id=0106009008 type=event subtype=switch_controller pri=notice vd=root msg="FortiLink: ISL timing-out for trunk(8DF4K17000028-0) member port(3) did not receive ISL pkt for(30) sec" 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 11: 2019-10-11 11:15:44 log_id=0100001000 type=event subtype=link pri=notice vd=root msg="Physical port (port2) became non-active member of trunk (_FlInK1_MLAG0_)" 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 12: 2019-10-11 11:15:43 log_id=0105008255 type=event subtype=spanning_tree pri=notice vd=root user="__switch_stp_port_set_state" inst_id="0" intf_id="2049" member_port="2" stp_state="4" hw_state="4" 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 13: 2019-10-11 11:15:43 log_id=0105008255 type=event subtype=spanning_tree pri=notice vd=root user="__switch_stp_port_set_state" inst_id="0" intf_id="2049" member_port="1" stp_state="4" hw_state="1" 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 14: 2019-10-11 11:15:43 log_id=0105008255 type=event subtype=spanning_tree pri=notice vd=root user="__check_stp_intf_change" trunk _FlInK1_MLAG0_ (intf_id 2049) effective members change detected: effective members in hw port2 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 15: 2019-10-11 11:15:43 log_id=0106009008 type=event subtype=switch_controller pri=notice vd=root msg="FortiLink: ISL timing-out for trunk(8DF4K17000028-0) member port(4) did not receive ISL pkt for(30) sec" 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 16: 2019-10-11 11:15:43 log_id=0106009008 type=event subtype=switch_controller pri=notice vd=root msg="FortiLink: ISL timing-out for trunk(8DF4K17000028-0) member port(3) did not receive ISL pkt for(30) sec" 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 17: 2019-10-11 11:15:42 log_id=0100001000 type=event subtype=link pri=notice vd=root msg="Physical port (port1) became non-active member of trunk (_FlInK1_MLAG0_)" 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 18: 2019-10-11 11:15:42 log_id=0106009008 type=event subtype=switch_controller pri=notice vd=root msg="FortiLink: ISL timing-out for trunk(8DF4K17000028-0) member port(4) did not receive ISL pkt for(30) sec" 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 19: 2019-10-11 11:15:42 log_id=0106009008 type=event subtype=switch_controller pri=notice vd=root msg="FortiLink: ISL timing-out for trunk(8DF4K17000028-0) member port(3) did not receive ISL pkt for(30) sec" 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 20: 2019-10-11 11:15:41 log_id=0103030531 type=event subtype=system pri=information vd="root" user="FortiLink" ui="httpsd" action=edit cfg_tid=51511915 cfg_path="switch.physical-port" cfg_obj="port48" cfg_attr="link-status[up (1Gbps full-duplex)->up (1Gbps full-duplex)]poe-status[enable->disable]" msg="Edit switch.physical-port port48" 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 21: 2019-10-11 11:15:41 log_id=0103030531 type=event subtype=system pri=information vd="root" user="FortiLink" ui="httpsd" action=edit cfg_tid=51511914 cfg_path="switch.physical-port" cfg_obj="port47" cfg_attr="link-status[up (1Gbps full-duplex)->up (1Gbps full-duplex)]poe-status[enable->disable]" msg="Edit switch.physical-port port47" 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 22: 2019-10-11 11:15:41 log_id=0103030531 type=event subtype=system pri=information vd="root" user="FortiLink" ui="httpsd" action=edit cfg_tid=51511913 cfg_path="switch.physical-port" cfg_obj="port4" cfg_attr="link-status[up (1Gbps full-duplex)->up (1Gbps full-duplex)]" msg="Edit switch.physical-port port4" 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 23: 2019-10-11 11:15:41 log_id=0106009008 type=event subtype=switch_controller pri=notice vd=root msg="FortiLink: ISL timing-out for trunk(8DF4K17000028-0) member port(4) did not receive ISL pkt for(30) sec" 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 24: 2019-10-11 11:15:41 log_id=0106009008 type=event subtype=switch_controller pri=notice vd=root msg="FortiLink: ISL timing-out for trunk(8DF4K17000028-0) member port(3) did not receive ISL pkt for(30) sec" 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 25: 2019-10-11 11:15:40 log_id=0103030531 type=event subtype=system pri=information vd="root" user="FortiLink" ui="httpsd" action=edit cfg_tid=51511910 cfg_path="switch.physical-port" cfg_obj="port3" cfg_attr="link-status[up (1Gbps full-duplex)->up (1Gbps full-duplex)]" msg="Edit switch.physical-port port3" 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 26: 2019-10-11 11:15:40 log_id=0103030531 type=event subtype=system pri=information vd="root" user="FortiLink" ui="httpsd" action=edit cfg_tid=51511909 cfg_path="switch.physical-port" cfg_obj="port2" cfg_attr="link-status[up (1Gbps full-duplex)->up (1Gbps full-duplex)]" msg="Edit switch.physical-port port2" 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 27: 2019-10-11 11:15:40 log_id=0103030531 type=event subtype=system pri=information vd="root" user="FortiLink" ui="httpsd" action=edit cfg_tid=51511908 cfg_path="switch.physical-port" cfg_obj="port1" cfg_attr="link-status[up (1Gbps full-duplex)->up (1Gbps full-duplex)]" msg="Edit switch.physical-port port1" 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 28: 2019-10-11 11:15:40 log_id=0105008255 type=event subtype=spanning_tree pri=notice vd=root user="__switch_stp_port_set_state" inst_id="0" intf_id="2049" member_port="2" stp_state="4" hw_state="4" 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 29: 2019-10-11 11:15:40 log_id=0105008255 type=event subtype=spanning_tree pri=notice vd=root user="__switch_stp_port_set_state" inst_id="0" intf_id="2049" member_port="1" stp_state="4" hw_state="4" 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 30: 2019-10-11 11:15:40 log_id=0105008255 type=event subtype=spanning_tree pri=notice vd=root user="__check_stp_intf_change" trunk _FlInK1_MLAG0_ (intf_id 2049) effective members change detected: effective members in hw port2 port1 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 31: 2019-10-11 11:15:40 log_id=0106009008 type=event subtype=switch_controller pri=notice vd=root msg="FortiLink: ISL timing-out for trunk(8DF4K17000028-0) member port(4) did not receive ISL pkt for(30) sec" 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 32: 2019-10-11 11:15:40 log_id=0106009008 type=event subtype=switch_controller pri=notice vd=root msg="FortiLink: ISL timing-out for trunk(8DF4K17000028-0) member port(3) did not receive ISL pkt for(30) sec" 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 33: 2019-10-11 11:15:39 log_id=0100001000 type=event subtype=link pri=notice vd=root msg="Physical port (port2) became active member of trunk (_FlInK1_MLAG0_)" 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 34: 2019-10-11 11:15:39 log_id=0105008255 type=event subtype=spanning_tree pri=notice vd=root user="stp_daemon" action=role-change unit="primary" switch.physical-port="8DN4K17000133-0" instanceid="15" event="role migration" oldrole="alternative" newrole="designated" msg="primary port 8DN4K17000133-0 instance 15 changed role from alternative to designated" 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 35: 2019-10-11 11:15:39 log_id=0105008255 type=event subtype=spanning_tree pri=notice vd=root user="stp_daemon" action=state-change unit="primary" switch.physical-port="_FlInK1_MLAG0_" instanceid="0" event="state migration" oldstate="learning" newstate="forwarding" msg="primary port _FlInK1_MLAG0_ instance 0 changed state from learning to forwarding" 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 36: 2019-10-11 11:15:39 log_id=0105008255 type=event subtype=spanning_tree pri=notice vd=root user="__switch_stp_port_set_state" inst_id="0" intf_id="2049" member_port="2" stp_state="4" hw_state="1" 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 37: 2019-10-11 11:15:39 log_id=0105008255 type=event subtype=spanning_tree pri=notice vd=root user="__switch_stp_port_set_state" inst_id="0" intf_id="2049" member_port="1" stp_state="4" hw_state="4" 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 38: 2019-10-11 11:15:39 log_id=0105008255 type=event subtype=spanning_tree pri=notice vd=root user="stp_daemon" action=state-change unit="primary" switch.physical-port="_FlInK1_MLAG0_" instanceid="0" event="state migration" oldstate="discarding" newstate="learning" msg="primary port _FlInK1_MLAG0_ instance 0 changed state from discarding to learning" 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 39: 2019-10-11 11:15:39 log_id=0105008255 type=event subtype=spanning_tree pri=notice vd=root user="stp_daemon" action=state-change unit="primary" switch.physical-port="8DF4K17000028-0" instanceid="0" event="state migration" oldstate="forwarding" newstate="discarding" msg="primary port 8DF4K17000028-0 instance 0 changed state from forwarding to discarding" 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 40: 2019-10-11 11:15:39 log_id=0105008255 type=event subtype=spanning_tree pri=notice vd=root user="stp_daemon" action=role-change unit="primary" switch.physical-port="8DF4K17000028-0" instanceid="0" event="role migration" oldrole="root" newrole="alternative" msg="primary port 8DF4K17000028-0 instance 0 changed role from root to alternative" 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 41: 2019-10-11 11:15:39 log_id=0105008255 type=event subtype=spanning_tree pri=notice vd=root user="stp_daemon" action=role-change unit="primary" switch.physical-port="_FlInK1_MLAG0_" instanceid="0" event="role migration" oldrole="designated" newrole="root" msg="primary port _FlInK1_MLAG0_ instance 0 changed role from designated to root" 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 42: 2019-10-11 11:15:39 log_id=0106009008 type=event subtype=switch_controller pri=notice vd=root msg="FortiLink: ISL timing-out for trunk(8DF4K17000028-0) member port(4) did not receive ISL pkt for(30) sec" 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 43: 2019-10-11 11:15:39 log_id=0106009008 type=event subtype=switch_controller pri=notice vd=root msg="FortiLink: ISL timing-out for trunk(8DF4K17000028-0) member port(3) did not receive ISL pkt for(30) sec" 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 44: 2019-10-11 11:15:39 log_id=0105008255 type=event subtype=spanning_tree pri=notice vd=root user="stp_daemon" action=role-change unit="primary" switch.physical-port="_FlInK1_MLAG0_" instanceid="15" event="role migration" oldrole="disabled" newrole="designated" msg="primary port _FlInK1_MLAG0_ instance 15 changed role from disabled to designated" 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 45: 2019-10-11 11:15:39 log_id=0105008255 type=event subtype=spanning_tree pri=notice vd=root user="stp_daemon" action=role-change unit="primary" switch.physical-port="_FlInK1_MLAG0_" instanceid="0" event="role migration" oldrole="disabled" newrole="designated" msg="primary port _FlInK1_MLAG0_ instance 0 changed role from disabled to designated" 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 46: 2019-10-11 11:15:39 log_id=0105008255 type=event subtype=spanning_tree pri=notice vd=root user="__check_stp_intf_change" trunk _FlInK1_MLAG0_ (intf_id 2049) effective members change detected: effective members in hw port1 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 47: 2019-10-11 11:15:39 log_id=0105008255 type=event subtype=spanning_tree pri=notice vd=root user="stp_daemon" action=role-change unit="primary" switch.physical-port="8DN4K17000133-0" instanceid="0" event="role migration" oldrole="alternative" newrole="designated" msg="primary port 8DN4K17000133-0 instance 0 changed role from alternative to designated" 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 48: 2019-10-11 11:15:38 log_id=0100001000 type=event subtype=link pri=notice vd=root msg="Physical port (port1) became active member of trunk (_FlInK1_MLAG0_)" 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 49: 2019-10-11 11:15:38 log_id=0100001300 type=event subtype=link pri=notice vd=root msg="MCLAG: ICL ACL change inggress-port-bitmap=0x7ffffffffffffe, egress-block-port-bitmap=0x7ffffffffffffe" 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: 50: 2019-10-11 11:15:38 log_id=0103030531 type=event subtype=system pri=information vd="root" user="admin" ui="console" action=edit cfg_tid=82247684 cfg_path="switch.trunk" cfg_obj="8DN4K17000133-0" cfg_attr="mclag-icl[disable->enable]" msg="Edit switch.trunk 8DN4K17000133-0" 
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 ::  
2019-10-11 11:15:47 :: S548DF4K16000653 #  
2019-10-11 11:15:47 :: S548DF4K16000653 #  
2019-10-11 11:15:47 :: S548DF4K16000653 # 
2019-10-11 11:15:57 :: Configuring MCLAG-ICL, if icl trunk is not found, maybe auto-discovery is not done yet 
2019-10-11 11:15:59 :: Info: ICL ports = ['port47', 'port48'] 


2019-10-11 11:15:59 :: configuring dut3-548d: config switch trunk 
2019-10-11 11:16:00 :: configuring dut3-548d: edit 8DN4K17000133-0 
2019-10-11 11:16:00 :: configuring dut3-548d: set mclag-icl enable 
2019-10-11 11:16:01 :: configuring dut3-548d: end 
2019-10-11 11:16:05 :: show switch trunk 
2019-10-11 11:16:05 :: config switch trunk 
2019-10-11 11:16:05 ::     edit "8DN4K17000133-0" 
2019-10-11 11:16:05 ::         set mode lacp-active 
2019-10-11 11:16:05 ::         set auto-isl 1 
2019-10-11 11:16:05 ::         set mclag-icl enable 
2019-10-11 11:16:05 ::             set members "port47" "port48" 
2019-10-11 11:16:05 ::     next 
2019-10-11 11:16:05 ::     edit "trunk1" 
2019-10-11 11:16:05 ::         set mode lacp-active 
2019-10-11 11:16:05 ::         set mclag enable 
2019-10-11 11:16:05 ::             set members "port13" 
2019-10-11 11:16:05 ::     next 
2019-10-11 11:16:05 ::     edit "_FlInK1_MLAG0_" 
2019-10-11 11:16:05 ::         set mode lacp-active 
2019-10-11 11:16:05 ::         set auto-isl 1 
2019-10-11 11:16:05 ::         set mclag enable 
2019-10-11 11:16:05 ::             set members "port1" "port2" 
2019-10-11 11:16:05 ::     next 
2019-10-11 11:16:05 :: end 
2019-10-11 11:16:05 ::  
2019-10-11 11:16:05 :: S548DF4K16000653 # 
2019-10-11 11:16:07 :: Info: mclag-icl is configured correctly at dut3-548d 


2019-10-11 11:16:28 :: Configuring MCLAG-ICL, if icl trunk is not found, maybe auto-discovery is not done yet 
2019-10-11 11:16:30 :: Info: ICL ports = ['port47', 'port48'] 


2019-10-11 11:16:30 :: configuring dut4-548d: config switch trunk 
2019-10-11 11:16:30 :: configuring dut4-548d: edit 8DF4K16000653-0 
2019-10-11 11:16:31 :: configuring dut4-548d: set mclag-icl enable 
2019-10-11 11:16:31 :: configuring dut4-548d: end 
2019-10-11 11:16:36 :: show switch trunk 
2019-10-11 11:16:36 :: config switch trunk 
2019-10-11 11:16:36 ::     edit "8DF4K16000653-0" 
2019-10-11 11:16:36 ::         set mode lacp-active 
2019-10-11 11:16:36 ::         set auto-isl 1 
2019-10-11 11:16:36 ::         set mclag-icl enable 
2019-10-11 11:16:36 ::             set members "port47" "port48" 
2019-10-11 11:16:36 ::     next 
2019-10-11 11:16:36 ::     edit "trunk1" 
2019-10-11 11:16:36 ::         set mode lacp-active 
2019-10-11 11:16:36 ::         set mclag enable 
2019-10-11 11:16:36 ::             set members "port13" 
2019-10-11 11:16:36 ::     next 
2019-10-11 11:16:36 ::     edit "_FlInK1_MLAG0_" 
2019-10-11 11:16:36 ::         set mode lacp-active 
2019-10-11 11:16:36 ::         set auto-isl 1 
2019-10-11 11:16:36 ::         set mclag enable 
2019-10-11 11:16:36 ::             set members "port1" "port2" "port3" "port4" 
2019-10-11 11:16:36 ::     next 
2019-10-11 11:16:36 :: end 
2019-10-11 11:16:36 ::  
2019-10-11 11:16:36 :: S548DN4K17000133 # 
2019-10-11 11:16:38 :: Info: mclag-icl is configured correctly at dut4-548d 


2019-10-11 11:16:38 :: ========================= after configure auto-isl-port-group wait for 300s, check out the mclag-icl is NOT missing ========================== 
============================ Timer:300 seconds remaining =================================================== Timer:299 seconds remaining =================================================== Timer:298 seconds remaining =================================================== Timer:297 seconds remaining =================================================== Timer:296 seconds remaining =================================================== Timer:295 seconds remaining =================================================== Timer:294 seconds remaining =================================================== Timer:293 seconds remaining =================================================== Timer:292 seconds remaining =================================================== Timer:291 seconds remaining =================================================== Timer:290 seconds remaining =================================================== Timer:289 seconds remaining =================================================== Timer:288 seconds remaining =================================================== Timer:287 seconds remaining =================================================== Timer:286 seconds remaining =================================================== Timer:285 seconds remaining =================================================== Timer:284 seconds remaining =================================================== Timer:283 seconds remaining =================================================== Timer:282 seconds remaining =================================================== Timer:281 seconds remaining =================================================== Timer:280 seconds remaining =================================================== Timer:279 seconds remaining =================================================== Timer:278 seconds remaining =================================================== Timer:277 seconds remaining =================================================== Timer:276 seconds remaining =================================================== Timer:275 seconds remaining =================================================== Timer:274 seconds remaining =================================================== Timer:273 seconds remaining =================================================== Timer:272 seconds remaining =================================================== Timer:271 seconds remaining =================================================== Timer:270 seconds remaining =================================================== Timer:269 seconds remaining =================================================== Timer:268 seconds remaining =================================================== Timer:267 seconds remaining =================================================== Timer:266 seconds remaining =================================================== Timer:265 seconds remaining =================================================== Timer:264 seconds remaining =================================================== Timer:263 seconds remaining =================================================== Timer:262 seconds remaining =================================================== Timer:261 seconds remaining =================================================== Timer:260 seconds remaining =================================================== Timer:259 seconds remaining =================================================== Timer:258 seconds remaining =================================================== Timer:257 seconds remaining =================================================== Timer:256 seconds remaining =================================================== Timer:255 seconds remaining =================================================== Timer:254 seconds remaining =================================================== Timer:253 seconds remaining =================================================== Timer:252 seconds remaining =================================================== Timer:251 seconds remaining =================================================== Timer:250 seconds remaining =================================================== Timer:249 seconds remaining =================================================== Timer:248 seconds remaining =================================================== Timer:247 seconds remaining =================================================== Timer:246 seconds remaining =================================================== Timer:245 seconds remaining =================================================== Timer:244 seconds remaining =================================================== Timer:243 seconds remaining =================================================== Timer:242 seconds remaining =================================================== Timer:241 seconds remaining =================================================== Timer:240 seconds remaining =================================================== Timer:239 seconds remaining =================================================== Timer:238 seconds remaining =================================================== Timer:237 seconds remaining =================================================== Timer:236 seconds remaining =================================================== Timer:235 seconds remaining =================================================== Timer:234 seconds remaining =================================================== Timer:233 seconds remaining =================================================== Timer:232 seconds remaining =================================================== Timer:231 seconds remaining =================================================== Timer:230 seconds remaining =================================================== Timer:229 seconds remaining =================================================== Timer:228 seconds remaining =================================================== Timer:227 seconds remaining =================================================== Timer:226 seconds remaining =================================================== Timer:225 seconds remaining =================================================== Timer:224 seconds remaining =================================================== Timer:223 seconds remaining =================================================== Timer:222 seconds remaining =================================================== Timer:221 seconds remaining =================================================== Timer:220 seconds remaining =================================================== Timer:219 seconds remaining =================================================== Timer:218 seconds remaining =================================================== Timer:217 seconds remaining =================================================== Timer:216 seconds remaining =================================================== Timer:215 seconds remaining =================================================== Timer:214 seconds remaining =================================================== Timer:213 seconds remaining =================================================== Timer:212 seconds remaining =================================================== Timer:211 seconds remaining =================================================== Timer:210 seconds remaining =================================================== Timer:209 seconds remaining =================================================== Timer:208 seconds remaining =================================================== Timer:207 seconds remaining =================================================== Timer:206 seconds remaining =================================================== Timer:205 seconds remaining =================================================== Timer:204 seconds remaining =================================================== Timer:203 seconds remaining =================================================== Timer:202 seconds remaining =================================================== Timer:201 seconds remaining =================================================== Timer:200 seconds remaining =================================================== Timer:199 seconds remaining =================================================== Timer:198 seconds remaining =================================================== Timer:197 seconds remaining =================================================== Timer:196 seconds remaining =================================================== Timer:195 seconds remaining =================================================== Timer:194 seconds remaining =================================================== Timer:193 seconds remaining =================================================== Timer:192 seconds remaining =================================================== Timer:191 seconds remaining =================================================== Timer:190 seconds remaining =================================================== Timer:189 seconds remaining =================================================== Timer:188 seconds remaining =================================================== Timer:187 seconds remaining =================================================== Timer:186 seconds remaining =================================================== Timer:185 seconds remaining =================================================== Timer:184 seconds remaining =================================================== Timer:183 seconds remaining =================================================== Timer:182 seconds remaining =================================================== Timer:181 seconds remaining =================================================== Timer:180 seconds remaining =================================================== Timer:179 seconds remaining =================================================== Timer:178 seconds remaining =================================================== Timer:177 seconds remaining =================================================== Timer:176 seconds remaining =================================================== Timer:175 seconds remaining =================================================== Timer:174 seconds remaining =================================================== Timer:173 seconds remaining =================================================== Timer:172 seconds remaining =================================================== Timer:171 seconds remaining =================================================== Timer:170 seconds remaining =================================================== Timer:169 seconds remaining =================================================== Timer:168 seconds remaining =================================================== Timer:167 seconds remaining =================================================== Timer:166 seconds remaining =================================================== Timer:165 seconds remaining =================================================== Timer:164 seconds remaining =================================================== Timer:163 seconds remaining =================================================== Timer:162 seconds remaining =================================================== Timer:161 seconds remaining =================================================== Timer:160 seconds remaining =================================================== Timer:159 seconds remaining =================================================== Timer:158 seconds remaining =================================================== Timer:157 seconds remaining =================================================== Timer:156 seconds remaining =================================================== Timer:155 seconds remaining =================================================== Timer:154 seconds remaining =================================================== Timer:153 seconds remaining =================================================== Timer:152 seconds remaining =================================================== Timer:151 seconds remaining =================================================== Timer:150 seconds remaining =================================================== Timer:149 seconds remaining =================================================== Timer:148 seconds remaining =================================================== Timer:147 seconds remaining =================================================== Timer:146 seconds remaining =================================================== Timer:145 seconds remaining =================================================== Timer:144 seconds remaining =================================================== Timer:143 seconds remaining =================================================== Timer:142 seconds remaining =================================================== Timer:141 seconds remaining =================================================== Timer:140 seconds remaining =================================================== Timer:139 seconds remaining =================================================== Timer:138 seconds remaining =================================================== Timer:137 seconds remaining =================================================== Timer:136 seconds remaining =================================================== Timer:135 seconds remaining =================================================== Timer:134 seconds remaining =================================================== Timer:133 seconds remaining =================================================== Timer:132 seconds remaining =================================================== Timer:131 seconds remaining =================================================== Timer:130 seconds remaining =================================================== Timer:129 seconds remaining =================================================== Timer:128 seconds remaining =================================================== Timer:127 seconds remaining =================================================== Timer:126 seconds remaining =================================================== Timer:125 seconds remaining =================================================== Timer:124 seconds remaining =================================================== Timer:123 seconds remaining =================================================== Timer:122 seconds remaining =================================================== Timer:121 seconds remaining =================================================== Timer:120 seconds remaining =================================================== Timer:119 seconds remaining =================================================== Timer:118 seconds remaining =================================================== Timer:117 seconds remaining =================================================== Timer:116 seconds remaining =================================================== Timer:115 seconds remaining =================================================== Timer:114 seconds remaining =================================================== Timer:113 seconds remaining =================================================== Timer:112 seconds remaining =================================================== Timer:111 seconds remaining =================================================== Timer:110 seconds remaining =================================================== Timer:109 seconds remaining =================================================== Timer:108 seconds remaining =================================================== Timer:107 seconds remaining =================================================== Timer:106 seconds remaining =================================================== Timer:105 seconds remaining =================================================== Timer:104 seconds remaining =================================================== Timer:103 seconds remaining =================================================== Timer:102 seconds remaining =================================================== Timer:101 seconds remaining =================================================== Timer:100 seconds remaining =================================================== Timer:99 seconds remaining =================================================== Timer:98 seconds remaining =================================================== Timer:97 seconds remaining =================================================== Timer:96 seconds remaining =================================================== Timer:95 seconds remaining =================================================== Timer:94 seconds remaining =================================================== Timer:93 seconds remaining =================================================== Timer:92 seconds remaining =================================================== Timer:91 seconds remaining =================================================== Timer:90 seconds remaining =================================================== Timer:89 seconds remaining =================================================== Timer:88 seconds remaining =================================================== Timer:87 seconds remaining =================================================== Timer:86 seconds remaining =================================================== Timer:85 seconds remaining =================================================== Timer:84 seconds remaining =================================================== Timer:83 seconds remaining =================================================== Timer:82 seconds remaining =================================================== Timer:81 seconds remaining =================================================== Timer:80 seconds remaining =================================================== Timer:79 seconds remaining =================================================== Timer:78 seconds remaining =================================================== Timer:77 seconds remaining =================================================== Timer:76 seconds remaining =================================================== Timer:75 seconds remaining =================================================== Timer:74 seconds remaining =================================================== Timer:73 seconds remaining =================================================== Timer:72 seconds remaining =================================================== Timer:71 seconds remaining =================================================== Timer:70 seconds remaining =================================================== Timer:69 seconds remaining =================================================== Timer:68 seconds remaining =================================================== Timer:67 seconds remaining =================================================== Timer:66 seconds remaining =================================================== Timer:65 seconds remaining =================================================== Timer:64 seconds remaining =================================================== Timer:63 seconds remaining =================================================== Timer:62 seconds remaining =================================================== Timer:61 seconds remaining =================================================== Timer:60 seconds remaining =================================================== Timer:59 seconds remaining =================================================== Timer:58 seconds remaining =================================================== Timer:57 seconds remaining =================================================== Timer:56 seconds remaining =================================================== Timer:55 seconds remaining =================================================== Timer:54 seconds remaining =================================================== Timer:53 seconds remaining =================================================== Timer:52 seconds remaining =================================================== Timer:51 seconds remaining =================================================== Timer:50 seconds remaining =================================================== Timer:49 seconds remaining =================================================== Timer:48 seconds remaining =================================================== Timer:47 seconds remaining =================================================== Timer:46 seconds remaining =================================================== Timer:45 seconds remaining =================================================== Timer:44 seconds remaining =================================================== Timer:43 seconds remaining =================================================== Timer:42 seconds remaining =================================================== Timer:41 seconds remaining =================================================== Timer:40 seconds remaining =================================================== Timer:39 seconds remaining =================================================== Timer:38 seconds remaining =================================================== Timer:37 seconds remaining =================================================== Timer:36 seconds remaining =================================================== Timer:35 seconds remaining =================================================== Timer:34 seconds remaining =================================================== Timer:33 seconds remaining =================================================== Timer:32 seconds remaining =================================================== Timer:31 seconds remaining =================================================== Timer:30 seconds remaining =================================================== Timer:29 seconds remaining =================================================== Timer:28 seconds remaining =================================================== Timer:27 seconds remaining =================================================== Timer:26 seconds remaining =================================================== Timer:25 seconds remaining =================================================== Timer:24 seconds remaining =================================================== Timer:23 seconds remaining =================================================== Timer:22 seconds remaining =================================================== Timer:21 seconds remaining =================================================== Timer:20 seconds remaining =================================================== Timer:19 seconds remaining =================================================== Timer:18 seconds remaining =================================================== Timer:17 seconds remaining =================================================== Timer:16 seconds remaining =================================================== Timer:15 seconds remaining =================================================== Timer:14 seconds remaining =================================================== Timer:13 seconds remaining =================================================== Timer:12 seconds remaining =================================================== Timer:11 seconds remaining =================================================== Timer:10 seconds remaining =================================================== Timer: 9 seconds remaining =================================================== Timer: 8 seconds remaining =================================================== Timer: 7 seconds remaining =================================================== Timer: 6 seconds remaining =================================================== Timer: 5 seconds remaining =================================================== Timer: 4 seconds remaining =================================================== Timer: 3 seconds remaining =================================================== Timer: 2 seconds remaining =================================================== Timer: 1 seconds remaining =======================
2019-10-11 11:22:05 :: configuring: config system global 
2019-10-11 11:22:05 :: configuring: set admintimeout 480 
2019-10-11 11:22:06 :: configuring: end 
2019-10-11 11:22:06 :: configuring: config system global 
2019-10-11 11:22:07 :: configuring: set admintimeout 480 
2019-10-11 11:22:07 :: configuring: end 
2019-10-11 11:22:08 :: configuring: config system global 
2019-10-11 11:22:08 :: configuring: set admintimeout 480 
2019-10-11 11:22:09 :: configuring: end 
2019-10-11 11:22:09 :: configuring: config system global 
2019-10-11 11:22:10 :: configuring: set admintimeout 480 
2019-10-11 11:22:10 :: configuring: end 
2019-10-11 11:22:11 :: After configuring MCLAG and wait for 5 min, check the configuration  
2019-10-11 11:22:13 :: ----------------dut1-548d: show switch trunk --------------- 
2019-10-11 11:22:13 :: show switch trunk 
2019-10-11 11:22:13 :: config switch trunk 
2019-10-11 11:22:13 ::     edit "704CA5CBC3DC-0" 
2019-10-11 11:22:13 ::         set mode lacp-active 
2019-10-11 11:22:13 ::         set auto-isl 1 
2019-10-11 11:22:13 ::         set isl-fortilink 1 
2019-10-11 11:22:13 ::         set mclag enable 
2019-10-11 11:22:13 ::             set members "port50" 
2019-10-11 11:22:13 ::     next 
2019-10-11 11:22:13 ::     edit "8DF4K17000028-0" 
2019-10-11 11:22:13 ::         set mode lacp-active 
2019-10-11 11:22:13 ::         set auto-isl 1 
2019-10-11 11:22:13 ::         set mclag-icl enable 
2019-10-11 11:22:13 ::             set members "port47" "port48" 
2019-10-11 11:22:13 ::     next 
2019-10-11 11:22:13 ::     edit "704CA5A8FCFA-0" 
2019-10-11 11:22:13 ::         set mode lacp-active 
2019-10-11 11:22:13 ::         set auto-isl 1 
2019-10-11 11:22:13 ::         set isl-fortilink 1 
2019-10-11 11:22:13 ::         set mclag enable 
2019-10-11 11:22:13 ::             set members "port49" 
2019-10-11 11:22:13 ::     next 
2019-10-11 11:22:13 ::     edit "sw1-trunk" 
2019-10-11 11:22:13 ::         set mode lacp-active 
2019-10-11 11:22:13 ::         set mclag enable 
2019-10-11 11:22:13 :: --More--                      set members "port13" 
2019-10-11 11:22:13 ::     next 
2019-10-11 11:22:13 ::     edit "core1" 
2019-10-11 11:22:13 ::         set mode lacp-active 
2019-10-11 11:22:13 ::         set auto-isl 1 
2019-10-11 11:22:13 ::         set mclag enable 
2019-10-11 11:22:13 ::             set members "port1" "port2" "port3" "port4" 
2019-10-11 11:22:13 ::     next 
2019-10-11 11:22:13 :: end 
2019-10-11 11:22:13 ::  
2019-10-11 11:22:13 :: S548DF4K17000014 # 
2019-10-11 11:22:15 :: ----------------dut1-548d: show switch auto-isl-port-group --------------- 
2019-10-11 11:22:15 :: show switch auto-isl-port-group 
2019-10-11 11:22:15 :: config switch auto-isl-port-group 
2019-10-11 11:22:15 ::     edit "core1" 
2019-10-11 11:22:15 ::             set members "port1" "port2" "port3" "port4" 
2019-10-11 11:22:15 ::     next 
2019-10-11 11:22:15 :: end 
2019-10-11 11:22:15 ::  
2019-10-11 11:22:15 :: S548DF4K17000014 # 
2019-10-11 11:22:17 :: ----------------dut2-548d: show switch trunk --------------- 
2019-10-11 11:22:17 :: show switch trunk 
2019-10-11 11:22:17 :: config switch trunk 
2019-10-11 11:22:17 ::     edit "8DF4K17000014-0" 
2019-10-11 11:22:17 ::         set mode lacp-active 
2019-10-11 11:22:17 ::         set auto-isl 1 
2019-10-11 11:22:17 ::         set mclag-icl enable 
2019-10-11 11:22:17 ::             set members "port47" "port48" 
2019-10-11 11:22:17 ::     next 
2019-10-11 11:22:17 ::     edit "704CA5A8FCFA-0" 
2019-10-11 11:22:17 ::         set mode lacp-active 
2019-10-11 11:22:17 ::         set auto-isl 1 
2019-10-11 11:22:17 ::         set isl-fortilink 1 
2019-10-11 11:22:17 ::         set mclag enable 
2019-10-11 11:22:17 ::             set members "port49" 
2019-10-11 11:22:17 ::     next 
2019-10-11 11:22:17 ::     edit "704CA5CBC3DC-0" 
2019-10-11 11:22:17 ::         set mode lacp-active 
2019-10-11 11:22:17 ::         set auto-isl 1 
2019-10-11 11:22:17 ::         set isl-fortilink 1 
2019-10-11 11:22:17 ::         set mclag enable 
2019-10-11 11:22:17 ::             set members "port50" 
2019-10-11 11:22:17 ::     next 
2019-10-11 11:22:17 ::     edit "sw1-trunk" 
2019-10-11 11:22:17 ::         set mode lacp-active 
2019-10-11 11:22:17 ::         set mclag enable 
2019-10-11 11:22:17 :: --More--                      set members "port13" 
2019-10-11 11:22:17 ::     next 
2019-10-11 11:22:17 ::     edit "_FlInK1_MLAG0_" 
2019-10-11 11:22:17 ::         set mode lacp-active 
2019-10-11 11:22:17 ::         set auto-isl 1 
2019-10-11 11:22:17 ::         set mclag enable 
2019-10-11 11:22:17 ::             set members "port3" "port4" "port2" "port1" 
2019-10-11 11:22:17 ::     next 
2019-10-11 11:22:17 :: end 
2019-10-11 11:22:17 ::  
2019-10-11 11:22:17 :: S548DF4K17000028 # 
2019-10-11 11:22:19 :: ----------------dut2-548d: show switch auto-isl-port-group --------------- 
2019-10-11 11:22:19 :: show switch auto-isl-port-group 
2019-10-11 11:22:19 ::  
2019-10-11 11:22:19 :: S548DF4K17000028 # 
2019-10-11 11:22:21 :: ----------------dut3-548d: show switch trunk --------------- 
2019-10-11 11:22:21 :: show switch trunk 
2019-10-11 11:22:21 :: config switch trunk 
2019-10-11 11:22:21 ::     edit "8DN4K17000133-0" 
2019-10-11 11:22:21 ::         set mode lacp-active 
2019-10-11 11:22:21 ::         set auto-isl 1 
2019-10-11 11:22:21 ::         set mclag-icl enable 
2019-10-11 11:22:21 ::             set members "port47" "port48" 
2019-10-11 11:22:21 ::     next 
2019-10-11 11:22:21 ::     edit "trunk1" 
2019-10-11 11:22:21 ::         set mode lacp-active 
2019-10-11 11:22:21 ::         set mclag enable 
2019-10-11 11:22:21 ::             set members "port13" 
2019-10-11 11:22:21 ::     next 
2019-10-11 11:22:21 ::     edit "_FlInK1_MLAG0_" 
2019-10-11 11:22:21 ::         set mode lacp-active 
2019-10-11 11:22:21 ::         set auto-isl 1 
2019-10-11 11:22:21 ::         set mclag enable 
2019-10-11 11:22:21 ::             set members "port1" "port2" "port3" "port4" 
2019-10-11 11:22:21 ::     next 
2019-10-11 11:22:21 :: end 
2019-10-11 11:22:21 ::  
2019-10-11 11:22:21 :: S548DF4K16000653 # 
2019-10-11 11:22:23 :: ----------------dut3-548d: show switch auto-isl-port-group --------------- 
2019-10-11 11:22:23 :: show switch auto-isl-port-group 
2019-10-11 11:22:23 ::  
2019-10-11 11:22:23 :: S548DF4K16000653 # 
2019-10-11 11:22:25 :: ----------------dut4-548d: show switch trunk --------------- 
2019-10-11 11:22:25 :: show switch trunk 
2019-10-11 11:22:25 :: config switch trunk 
2019-10-11 11:22:25 ::     edit "8DF4K16000653-0" 
2019-10-11 11:22:25 ::         set mode lacp-active 
2019-10-11 11:22:25 ::         set auto-isl 1 
2019-10-11 11:22:25 ::         set mclag-icl enable 
2019-10-11 11:22:25 ::             set members "port47" "port48" 
2019-10-11 11:22:25 ::     next 
2019-10-11 11:22:25 ::     edit "trunk1" 
2019-10-11 11:22:25 ::         set mode lacp-active 
2019-10-11 11:22:25 ::         set mclag enable 
2019-10-11 11:22:25 ::             set members "port13" 
2019-10-11 11:22:25 ::     next 
2019-10-11 11:22:25 ::     edit "_FlInK1_MLAG0_" 
2019-10-11 11:22:25 ::         set mode lacp-active 
2019-10-11 11:22:25 ::         set auto-isl 1 
2019-10-11 11:22:25 ::         set mclag enable 
2019-10-11 11:22:25 ::             set members "port1" "port2" "port3" "port4" 
2019-10-11 11:22:25 ::     next 
2019-10-11 11:22:25 :: end 
2019-10-11 11:22:25 ::  
2019-10-11 11:22:25 :: S548DN4K17000133 # 
2019-10-11 11:22:27 :: ----------------dut4-548d: show switch auto-isl-port-group --------------- 
2019-10-11 11:22:27 :: show switch auto-isl-port-group 
2019-10-11 11:22:27 ::  
2019-10-11 11:22:27 :: S548DN4K17000133 # 
2019-10-11 11:22:27 :: ------------  start configuring fortigate  -------------------- 
2019-10-11 11:22:27 :: configuring 3960E: config switch-controller managed-switch 
2019-10-11 11:22:28 :: configuring 3960E: edit S548DF4K16000653 
2019-10-11 11:22:28 :: configuring 3960E: config ports 
2019-10-11 11:22:29 :: configuring 3960E: delete trunk1 
2019-10-11 11:22:29 :: configuring 3960E: edit trunk1 
2019-10-11 11:22:30 :: configuring 3960E: set type trunk 
2019-10-11 11:22:30 :: configuring 3960E: set mode lacp-active 
2019-10-11 11:22:31 :: configuring 3960E: set mclag enable 
2019-10-11 11:22:31 :: configuring 3960E: set members port13 
2019-10-11 11:22:32 :: configuring 3960E: next 
2019-10-11 11:22:32 :: configuring 3960E: end 
2019-10-11 11:22:33 :: configuring 3960E: next 
2019-10-11 11:22:33 :: configuring 3960E: edit S548DN4K17000133 
2019-10-11 11:22:34 :: configuring 3960E: config ports 
2019-10-11 11:22:34 :: configuring 3960E: delete trunk1 
2019-10-11 11:22:35 :: configuring 3960E: edit trunk1 
2019-10-11 11:22:35 :: configuring 3960E: set type trunk 
2019-10-11 11:22:36 :: configuring 3960E: set mode lacp-active 
2019-10-11 11:22:36 :: configuring 3960E: set mclag enable 
2019-10-11 11:22:37 :: configuring 3960E: set members port13 
2019-10-11 11:22:37 :: configuring 3960E: next 
2019-10-11 11:22:38 :: configuring 3960E: end 
2019-10-11 11:22:38 :: configuring 3960E: end 
2019-10-11 11:22:39 :: ========================= after configuring managed FSW and FGT, wait for 300 sec ========================== 
============================ Timer:300 seconds remaining =================================================== Timer:299 seconds remaining =================================================== Timer:298 seconds remaining =================================================== Timer:297 seconds remaining =================================================== Timer:296 seconds remaining =================================================== Timer:295 seconds remaining =================================================== Timer:294 seconds remaining =================================================== Timer:293 seconds remaining =================================================== Timer:292 seconds remaining =================================================== Timer:291 seconds remaining =================================================== Timer:290 seconds remaining =================================================== Timer:289 seconds remaining =================================================== Timer:288 seconds remaining =================================================== Timer:287 seconds remaining =================================================== Timer:286 seconds remaining =================================================== Timer:285 seconds remaining =================================================== Timer:284 seconds remaining =================================================== Timer:283 seconds remaining =================================================== Timer:282 seconds remaining =================================================== Timer:281 seconds remaining =================================================== Timer:280 seconds remaining =================================================== Timer:279 seconds remaining =================================================== Timer:278 seconds remaining =================================================== Timer:277 seconds remaining =================================================== Timer:276 seconds remaining =================================================== Timer:275 seconds remaining =================================================== Timer:274 seconds remaining =================================================== Timer:273 seconds remaining =================================================== Timer:272 seconds remaining =================================================== Timer:271 seconds remaining =================================================== Timer:270 seconds remaining =================================================== Timer:269 seconds remaining =================================================== Timer:268 seconds remaining =================================================== Timer:267 seconds remaining =================================================== Timer:266 seconds remaining =================================================== Timer:265 seconds remaining =================================================== Timer:264 seconds remaining =================================================== Timer:263 seconds remaining =================================================== Timer:262 seconds remaining =================================================== Timer:261 seconds remaining =================================================== Timer:260 seconds remaining =================================================== Timer:259 seconds remaining =================================================== Timer:258 seconds remaining =================================================== Timer:257 seconds remaining =================================================== Timer:256 seconds remaining =================================================== Timer:255 seconds remaining =================================================== Timer:254 seconds remaining =================================================== Timer:253 seconds remaining =================================================== Timer:252 seconds remaining =================================================== Timer:251 seconds remaining =================================================== Timer:250 seconds remaining =================================================== Timer:249 seconds remaining =================================================== Timer:248 seconds remaining =================================================== Timer:247 seconds remaining =================================================== Timer:246 seconds remaining =================================================== Timer:245 seconds remaining =================================================== Timer:244 seconds remaining =================================================== Timer:243 seconds remaining =================================================== Timer:242 seconds remaining =================================================== Timer:241 seconds remaining =================================================== Timer:240 seconds remaining =================================================== Timer:239 seconds remaining =================================================== Timer:238 seconds remaining =================================================== Timer:237 seconds remaining =================================================== Timer:236 seconds remaining =================================================== Timer:235 seconds remaining =================================================== Timer:234 seconds remaining =================================================== Timer:233 seconds remaining =================================================== Timer:232 seconds remaining =================================================== Timer:231 seconds remaining =================================================== Timer:230 seconds remaining =================================================== Timer:229 seconds remaining =================================================== Timer:228 seconds remaining =================================================== Timer:227 seconds remaining =================================================== Timer:226 seconds remaining =================================================== Timer:225 seconds remaining =================================================== Timer:224 seconds remaining =================================================== Timer:223 seconds remaining =================================================== Timer:222 seconds remaining =================================================== Timer:221 seconds remaining =================================================== Timer:220 seconds remaining =================================================== Timer:219 seconds remaining =================================================== Timer:218 seconds remaining =================================================== Timer:217 seconds remaining =================================================== Timer:216 seconds remaining =================================================== Timer:215 seconds remaining =================================================== Timer:214 seconds remaining =================================================== Timer:213 seconds remaining =================================================== Timer:212 seconds remaining =================================================== Timer:211 seconds remaining =================================================== Timer:210 seconds remaining =================================================== Timer:209 seconds remaining =================================================== Timer:208 seconds remaining =================================================== Timer:207 seconds remaining =================================================== Timer:206 seconds remaining =================================================== Timer:205 seconds remaining =================================================== Timer:204 seconds remaining =================================================== Timer:203 seconds remaining =================================================== Timer:202 seconds remaining =================================================== Timer:201 seconds remaining =================================================== Timer:200 seconds remaining =================================================== Timer:199 seconds remaining =================================================== Timer:198 seconds remaining =================================================== Timer:197 seconds remaining =================================================== Timer:196 seconds remaining =================================================== Timer:195 seconds remaining =================================================== Timer:194 seconds remaining =================================================== Timer:193 seconds remaining =================================================== Timer:192 seconds remaining =================================================== Timer:191 seconds remaining =================================================== Timer:190 seconds remaining =================================================== Timer:189 seconds remaining =================================================== Timer:188 seconds remaining =================================================== Timer:187 seconds remaining =================================================== Timer:186 seconds remaining =================================================== Timer:185 seconds remaining =================================================== Timer:184 seconds remaining =================================================== Timer:183 seconds remaining =================================================== Timer:182 seconds remaining =================================================== Timer:181 seconds remaining =================================================== Timer:180 seconds remaining =================================================== Timer:179 seconds remaining =================================================== Timer:178 seconds remaining =================================================== Timer:177 seconds remaining =================================================== Timer:176 seconds remaining =================================================== Timer:175 seconds remaining =================================================== Timer:174 seconds remaining =================================================== Timer:173 seconds remaining =================================================== Timer:172 seconds remaining =================================================== Timer:171 seconds remaining =================================================== Timer:170 seconds remaining =================================================== Timer:169 seconds remaining =================================================== Timer:168 seconds remaining =================================================== Timer:167 seconds remaining =================================================== Timer:166 seconds remaining =================================================== Timer:165 seconds remaining =================================================== Timer:164 seconds remaining =================================================== Timer:163 seconds remaining =================================================== Timer:162 seconds remaining =================================================== Timer:161 seconds remaining =================================================== Timer:160 seconds remaining =================================================== Timer:159 seconds remaining =================================================== Timer:158 seconds remaining =================================================== Timer:157 seconds remaining =================================================== Timer:156 seconds remaining =================================================== Timer:155 seconds remaining =================================================== Timer:154 seconds remaining =================================================== Timer:153 seconds remaining =================================================== Timer:152 seconds remaining =================================================== Timer:151 seconds remaining =================================================== Timer:150 seconds remaining =================================================== Timer:149 seconds remaining =================================================== Timer:148 seconds remaining =================================================== Timer:147 seconds remaining =================================================== Timer:146 seconds remaining =================================================== Timer:145 seconds remaining =================================================== Timer:144 seconds remaining =================================================== Timer:143 seconds remaining =================================================== Timer:142 seconds remaining =================================================== Timer:141 seconds remaining =================================================== Timer:140 seconds remaining =================================================== Timer:139 seconds remaining =================================================== Timer:138 seconds remaining =================================================== Timer:137 seconds remaining =================================================== Timer:136 seconds remaining =================================================== Timer:135 seconds remaining =================================================== Timer:134 seconds remaining =================================================== Timer:133 seconds remaining =================================================== Timer:132 seconds remaining =================================================== Timer:131 seconds remaining =================================================== Timer:130 seconds remaining =================================================== Timer:129 seconds remaining =================================================== Timer:128 seconds remaining =================================================== Timer:127 seconds remaining =================================================== Timer:126 seconds remaining =================================================== Timer:125 seconds remaining =================================================== Timer:124 seconds remaining =================================================== Timer:123 seconds remaining =================================================== Timer:122 seconds remaining =================================================== Timer:121 seconds remaining =================================================== Timer:120 seconds remaining =================================================== Timer:119 seconds remaining =================================================== Timer:118 seconds remaining =================================================== Timer:117 seconds remaining =================================================== Timer:116 seconds remaining =================================================== Timer:115 seconds remaining =================================================== Timer:114 seconds remaining =================================================== Timer:113 seconds remaining =================================================== Timer:112 seconds remaining =================================================== Timer:111 seconds remaining =================================================== Timer:110 seconds remaining =================================================== Timer:109 seconds remaining =================================================== Timer:108 seconds remaining =================================================== Timer:107 seconds remaining =================================================== Timer:106 seconds remaining =================================================== Timer:105 seconds remaining =================================================== Timer:104 seconds remaining =================================================== Timer:103 seconds remaining =================================================== Timer:102 seconds remaining =================================================== Timer:101 seconds remaining =================================================== Timer:100 seconds remaining =================================================== Timer:99 seconds remaining =================================================== Timer:98 seconds remaining =================================================== Timer:97 seconds remaining =================================================== Timer:96 seconds remaining =================================================== Timer:95 seconds remaining =================================================== Timer:94 seconds remaining =================================================== Timer:93 seconds remaining =================================================== Timer:92 seconds remaining =================================================== Timer:91 seconds remaining =================================================== Timer:90 seconds remaining =================================================== Timer:89 seconds remaining =================================================== Timer:88 seconds remaining =================================================== Timer:87 seconds remaining =================================================== Timer:86 seconds remaining =================================================== Timer:85 seconds remaining =================================================== Timer:84 seconds remaining =================================================== Timer:83 seconds remaining =================================================== Timer:82 seconds remaining =================================================== Timer:81 seconds remaining =================================================== Timer:80 seconds remaining =================================================== Timer:79 seconds remaining =================================================== Timer:78 seconds remaining =================================================== Timer:77 seconds remaining =================================================== Timer:76 seconds remaining =================================================== Timer:75 seconds remaining =================================================== Timer:74 seconds remaining =================================================== Timer:73 seconds remaining =================================================== Timer:72 seconds remaining =================================================== Timer:71 seconds remaining =================================================== Timer:70 seconds remaining =================================================== Timer:69 seconds remaining =================================================== Timer:68 seconds remaining =================================================== Timer:67 seconds remaining =================================================== Timer:66 seconds remaining =================================================== Timer:65 seconds remaining =================================================== Timer:64 seconds remaining =================================================== Timer:63 seconds remaining =================================================== Timer:62 seconds remaining =================================================== Timer:61 seconds remaining =================================================== Timer:60 seconds remaining =================================================== Timer:59 seconds remaining =================================================== Timer:58 seconds remaining =================================================== Timer:57 seconds remaining =================================================== Timer:56 seconds remaining =================================================== Timer:55 seconds remaining =================================================== Timer:54 seconds remaining =================================================== Timer:53 seconds remaining =================================================== Timer:52 seconds remaining =================================================== Timer:51 seconds remaining =================================================== Timer:50 seconds remaining =================================================== Timer:49 seconds remaining =================================================== Timer:48 seconds remaining =================================================== Timer:47 seconds remaining =================================================== Timer:46 seconds remaining =================================================== Timer:45 seconds remaining =================================================== Timer:44 seconds remaining =================================================== Timer:43 seconds remaining =================================================== Timer:42 seconds remaining =================================================== Timer:41 seconds remaining =================================================== Timer:40 seconds remaining =================================================== Timer:39 seconds remaining =================================================== Timer:38 seconds remaining =================================================== Timer:37 seconds remaining =================================================== Timer:36 seconds remaining =================================================== Timer:35 seconds remaining =================================================== Timer:34 seconds remaining =================================================== Timer:33 seconds remaining =================================================== Timer:32 seconds remaining =================================================== Timer:31 seconds remaining =================================================== Timer:30 seconds remaining =================================================== Timer:29 seconds remaining =================================================== Timer:28 seconds remaining =================================================== Timer:27 seconds remaining =================================================== Timer:26 seconds remaining =================================================== Timer:25 seconds remaining =================================================== Timer:24 seconds remaining =================================================== Timer:23 seconds remaining =================================================== Timer:22 seconds remaining =================================================== Timer:21 seconds remaining =================================================== Timer:20 seconds remaining =================================================== Timer:19 seconds remaining =================================================== Timer:18 seconds remaining =================================================== Timer:17 seconds remaining =================================================== Timer:16 seconds remaining =================================================== Timer:15 seconds remaining =================================================== Timer:14 seconds remaining =================================================== Timer:13 seconds remaining =================================================== Timer:12 seconds remaining =================================================== Timer:11 seconds remaining =================================================== Timer:10 seconds remaining =================================================== Timer: 9 seconds remaining =================================================== Timer: 8 seconds remaining =================================================== Timer: 7 seconds remaining =================================================== Timer: 6 seconds remaining =================================================== Timer: 5 seconds remaining =================================================== Timer: 4 seconds remaining =================================================== Timer: 3 seconds remaining =================================================== Timer: 2 seconds remaining =================================================== Timer: 1 seconds remaining =======================
2019-10-11 11:27:40 :: ================ Upgrading FSWs via Fortigate ============= 
2019-10-11 11:27:40 :: Executing command: execute switch-controller switch-software upload tftp FSW_548D_FPOE-v6-build0192-FORTINET.out 10.105.19.19 
2019-10-11 11:27:50 :: Executing command: execute switch-controller switch-software upload tftp FSW_548D-v6-build0192-FORTINET.out 10.105.19.19 
2019-10-11 11:27:55 :: ----------------3960E: execute switch-controller switch-software list-available --------------- 
2019-10-11 11:27:55 :: execute switch-controller switch-software upload tftp FSW_548D -v6-build0192-FORTINET.out 10.105.19.19 
2019-10-11 11:27:55 ::  
2019-10-11 11:27:55 :: Downloading file FSW_548D-v6-build0192-FORTINET.out from tftp server 10.105.19.19... 
2019-10-11 11:27:55 :: #### 
2019-10-11 11:27:55 :: Executing command: execute switch-controller switch-software upgrade S548DN4K17000133 S548DN-IMG.swtp 
2019-10-11 11:28:05 :: ========================= upgrading S548DN4K17000133 S548DN-IMG.swtp ========================== 
============================ Timer:10 seconds remaining =================================================== Timer: 9 seconds remaining =================================================== Timer: 8 seconds remaining =================================================== Timer: 7 seconds remaining =================================================== Timer: 6 seconds remaining =================================================== Timer: 5 seconds remaining =================================================== Timer: 4 seconds remaining =================================================== Timer: 3 seconds remaining =================================================== Timer: 2 seconds remaining =================================================== Timer: 1 seconds remaining =======================
2019-10-11 11:28:15 :: Executing command: execute switch-controller switch-software upgrade S548DF4K16000653 S548DF-IMG.swtp 
2019-10-11 11:28:15 :: ========================= upgrading S548DF4K16000653 S548DF-IMG.swtp, wait for 200 secs for tier-2 switches to download image ========================== 
============================ Timer:200 seconds remaining =================================================== Timer:199 seconds remaining =================================================== Timer:198 seconds remaining =================================================== Timer:197 seconds remaining =================================================== Timer:196 seconds remaining =================================================== Timer:195 seconds remaining =================================================== Timer:194 seconds remaining =================================================== Timer:193 seconds remaining =================================================== Timer:192 seconds remaining =================================================== Timer:191 seconds remaining =================================================== Timer:190 seconds remaining =================================================== Timer:189 seconds remaining =================================================== Timer:188 seconds remaining =================================================== Timer:187 seconds remaining =================================================== Timer:186 seconds remaining =================================================== Timer:185 seconds remaining =================================================== Timer:184 seconds remaining =================================================== Timer:183 seconds remaining =================================================== Timer:182 seconds remaining =================================================== Timer:181 seconds remaining =================================================== Timer:180 seconds remaining =================================================== Timer:179 seconds remaining =================================================== Timer:178 seconds remaining =================================================== Timer:177 seconds remaining =================================================== Timer:176 seconds remaining =================================================== Timer:175 seconds remaining =================================================== Timer:174 seconds remaining =================================================== Timer:173 seconds remaining =================================================== Timer:172 seconds remaining =================================================== Timer:171 seconds remaining =================================================== Timer:170 seconds remaining =================================================== Timer:169 seconds remaining =================================================== Timer:168 seconds remaining =================================================== Timer:167 seconds remaining =================================================== Timer:166 seconds remaining =================================================== Timer:165 seconds remaining =================================================== Timer:164 seconds remaining =================================================== Timer:163 seconds remaining =================================================== Timer:162 seconds remaining =================================================== Timer:161 seconds remaining =================================================== Timer:160 seconds remaining =================================================== Timer:159 seconds remaining =================================================== Timer:158 seconds remaining =================================================== Timer:157 seconds remaining =================================================== Timer:156 seconds remaining =================================================== Timer:155 seconds remaining =================================================== Timer:154 seconds remaining =================================================== Timer:153 seconds remaining =================================================== Timer:152 seconds remaining =================================================== Timer:151 seconds remaining =================================================== Timer:150 seconds remaining =================================================== Timer:149 seconds remaining =================================================== Timer:148 seconds remaining =================================================== Timer:147 seconds remaining =================================================== Timer:146 seconds remaining =================================================== Timer:145 seconds remaining =================================================== Timer:144 seconds remaining =================================================== Timer:143 seconds remaining =================================================== Timer:142 seconds remaining =================================================== Timer:141 seconds remaining =================================================== Timer:140 seconds remaining =================================================== Timer:139 seconds remaining =================================================== Timer:138 seconds remaining =================================================== Timer:137 seconds remaining =================================================== Timer:136 seconds remaining =================================================== Timer:135 seconds remaining =================================================== Timer:134 seconds remaining =================================================== Timer:133 seconds remaining =================================================== Timer:132 seconds remaining =================================================== Timer:131 seconds remaining =================================================== Timer:130 seconds remaining =================================================== Timer:129 seconds remaining =================================================== Timer:128 seconds remaining =================================================== Timer:127 seconds remaining =================================================== Timer:126 seconds remaining =================================================== Timer:125 seconds remaining =================================================== Timer:124 seconds remaining =================================================== Timer:123 seconds remaining =================================================== Timer:122 seconds remaining =================================================== Timer:121 seconds remaining =================================================== Timer:120 seconds remaining =================================================== Timer:119 seconds remaining =================================================== Timer:118 seconds remaining =================================================== Timer:117 seconds remaining =================================================== Timer:116 seconds remaining =================================================== Timer:115 seconds remaining =================================================== Timer:114 seconds remaining =================================================== Timer:113 seconds remaining =================================================== Timer:112 seconds remaining =================================================== Timer:111 seconds remaining =================================================== Timer:110 seconds remaining =================================================== Timer:109 seconds remaining =================================================== Timer:108 seconds remaining =================================================== Timer:107 seconds remaining =================================================== Timer:106 seconds remaining =================================================== Timer:105 seconds remaining =================================================== Timer:104 seconds remaining =================================================== Timer:103 seconds remaining =================================================== Timer:102 seconds remaining =================================================== Timer:101 seconds remaining =================================================== Timer:100 seconds remaining =================================================== Timer:99 seconds remaining =================================================== Timer:98 seconds remaining =================================================== Timer:97 seconds remaining =================================================== Timer:96 seconds remaining =================================================== Timer:95 seconds remaining =================================================== Timer:94 seconds remaining =================================================== Timer:93 seconds remaining =================================================== Timer:92 seconds remaining =================================================== Timer:91 seconds remaining =================================================== Timer:90 seconds remaining =================================================== Timer:89 seconds remaining =================================================== Timer:88 seconds remaining =================================================== Timer:87 seconds remaining =================================================== Timer:86 seconds remaining =================================================== Timer:85 seconds remaining =================================================== Timer:84 seconds remaining =================================================== Timer:83 seconds remaining =================================================== Timer:82 seconds remaining =================================================== Timer:81 seconds remaining =================================================== Timer:80 seconds remaining =================================================== Timer:79 seconds remaining =================================================== Timer:78 seconds remaining =================================================== Timer:77 seconds remaining =================================================== Timer:76 seconds remaining =================================================== Timer:75 seconds remaining =================================================== Timer:74 seconds remaining =================================================== Timer:73 seconds remaining =================================================== Timer:72 seconds remaining =================================================== Timer:71 seconds remaining =================================================== Timer:70 seconds remaining =================================================== Timer:69 seconds remaining =================================================== Timer:68 seconds remaining =================================================== Timer:67 seconds remaining =================================================== Timer:66 seconds remaining =================================================== Timer:65 seconds remaining =================================================== Timer:64 seconds remaining =================================================== Timer:63 seconds remaining =================================================== Timer:62 seconds remaining =================================================== Timer:61 seconds remaining =================================================== Timer:60 seconds remaining =================================================== Timer:59 seconds remaining =================================================== Timer:58 seconds remaining =================================================== Timer:57 seconds remaining =================================================== Timer:56 seconds remaining =================================================== Timer:55 seconds remaining =================================================== Timer:54 seconds remaining =================================================== Timer:53 seconds remaining =================================================== Timer:52 seconds remaining =================================================== Timer:51 seconds remaining =================================================== Timer:50 seconds remaining =================================================== Timer:49 seconds remaining =================================================== Timer:48 seconds remaining =================================================== Timer:47 seconds remaining =================================================== Timer:46 seconds remaining =================================================== Timer:45 seconds remaining =================================================== Timer:44 seconds remaining =================================================== Timer:43 seconds remaining =================================================== Timer:42 seconds remaining =================================================== Timer:41 seconds remaining =================================================== Timer:40 seconds remaining =================================================== Timer:39 seconds remaining =================================================== Timer:38 seconds remaining =================================================== Timer:37 seconds remaining =================================================== Timer:36 seconds remaining =================================================== Timer:35 seconds remaining =================================================== Timer:34 seconds remaining =================================================== Timer:33 seconds remaining =================================================== Timer:32 seconds remaining =================================================== Timer:31 seconds remaining =================================================== Timer:30 seconds remaining =================================================== Timer:29 seconds remaining =================================================== Timer:28 seconds remaining =================================================== Timer:27 seconds remaining =================================================== Timer:26 seconds remaining =================================================== Timer:25 seconds remaining =================================================== Timer:24 seconds remaining =================================================== Timer:23 seconds remaining =================================================== Timer:22 seconds remaining =================================================== Timer:21 seconds remaining =================================================== Timer:20 seconds remaining =================================================== Timer:19 seconds remaining =================================================== Timer:18 seconds remaining =================================================== Timer:17 seconds remaining =================================================== Timer:16 seconds remaining =================================================== Timer:15 seconds remaining =================================================== Timer:14 seconds remaining =================================================== Timer:13 seconds remaining =================================================== Timer:12 seconds remaining =================================================== Timer:11 seconds remaining =================================================== Timer:10 seconds remaining =================================================== Timer: 9 seconds remaining =================================================== Timer: 8 seconds remaining =================================================== Timer: 7 seconds remaining =================================================== Timer: 6 seconds remaining =================================================== Timer: 5 seconds remaining =================================================== Timer: 4 seconds remaining =================================================== Timer: 3 seconds remaining =================================================== Timer: 2 seconds remaining =================================================== Timer: 1 seconds remaining =======================
2019-10-11 11:31:36 :: Executing command: execute switch-controller switch-software upgrade S548DF4K17000028 S548DF-IMG.swtp 
2019-10-11 11:31:36 :: ========================= upgrading S548DF4K17000028 S548DF-IMG.swtp ========================== 
============================ Timer:10 seconds remaining =================================================== Timer: 9 seconds remaining =================================================== Timer: 8 seconds remaining =================================================== Timer: 7 seconds remaining =================================================== Timer: 6 seconds remaining =================================================== Timer: 5 seconds remaining =================================================== Timer: 4 seconds remaining =================================================== Timer: 3 seconds remaining =================================================== Timer: 2 seconds remaining =================================================== Timer: 1 seconds remaining =======================
2019-10-11 11:31:46 :: Executing command: execute switch-controller switch-software upgrade S548DF4K17000014 S548DF-IMG.swtp 
2019-10-11 11:31:46 :: ========================= upgrading S548DF4K17000014 S548DF-IMG.swtp ========================== 
============================ Timer:10 seconds remaining =================================================== Timer: 9 seconds remaining =================================================== Timer: 8 seconds remaining =================================================== Timer: 7 seconds remaining =================================================== Timer: 6 seconds remaining =================================================== Timer: 5 seconds remaining =================================================== Timer: 4 seconds remaining =================================================== Timer: 3 seconds remaining =================================================== Timer: 2 seconds remaining =================================================== Timer: 1 seconds remaining =======================
2019-10-11 11:31:58 :: ----------------3960E: execute switch-controller get-upgrade-status --------------- 
2019-10-11 11:31:58 :: execute switch-controller switch-software upgrade S548DF4K1600 0653 S548DF-IMG.swtp 
2019-10-11 11:31:58 :: Image download process: 9  %15 %19 %24 %29 %34 %40 %44 %49 %54 %59 %64 %69 %74 %78 %83 %89 %93 %98 %100% 
2019-10-11 11:31:58 ::  
2019-10-11 11:31:58 :: FortiGate-3960E # execute switch-controller switch-software upgrade S548DF4K1700 0028 S548DF-IMG.swtp 
2019-10-11 11:31:58 :: Image download process: 9  %14 %19 %24 %29 %33 %38 %43 %execute switch-controller switch-software upgrade S548DF48 %4K17000014 S548DF-IMG.swtp 
2019-10-11 11:31:58 :: 53 %58 %63 %68 %73 %77 %82 %87 %92 %97 %execute switch-controller get-upgrade-status 
2019-10-11 11:31:58 :: 100% 
2019-10-11 11:31:58 ::  
2019-10-11 11:31:58 :: FortiGate-3960E # execute switch-controller switch-software upgrade S548DF4K1700 0014 S548DF-IMG.swtp 
2019-10-11 11:31:58 ::  
2019-10-11 11:31:58 :: ========================= After software upgrade, wait for 400 seconds ========================== 
============================ Timer:400 seconds remaining =================================================== Timer:399 seconds remaining =================================================== Timer:398 seconds remaining =================================================== Timer:397 seconds remaining =================================================== Timer:396 seconds remaining =================================================== Timer:395 seconds remaining =================================================== Timer:394 seconds remaining =================================================== Timer:393 seconds remaining =================================================== Timer:392 seconds remaining =================================================== Timer:391 seconds remaining =================================================== Timer:390 seconds remaining =================================================== Timer:389 seconds remaining =================================================== Timer:388 seconds remaining =================================================== Timer:387 seconds remaining =================================================== Timer:386 seconds remaining =================================================== Timer:385 seconds remaining =================================================== Timer:384 seconds remaining =================================================== Timer:383 seconds remaining =================================================== Timer:382 seconds remaining =================================================== Timer:381 seconds remaining =================================================== Timer:380 seconds remaining =================================================== Timer:379 seconds remaining =================================================== Timer:378 seconds remaining =================================================== Timer:377 seconds remaining =================================================== Timer:376 seconds remaining =================================================== Timer:375 seconds remaining =================================================== Timer:374 seconds remaining =================================================== Timer:373 seconds remaining =================================================== Timer:372 seconds remaining =================================================== Timer:371 seconds remaining =================================================== Timer:370 seconds remaining =================================================== Timer:369 seconds remaining =================================================== Timer:368 seconds remaining =================================================== Timer:367 seconds remaining =================================================== Timer:366 seconds remaining =================================================== Timer:365 seconds remaining =================================================== Timer:364 seconds remaining =================================================== Timer:363 seconds remaining =================================================== Timer:362 seconds remaining =================================================== Timer:361 seconds remaining =================================================== Timer:360 seconds remaining =================================================== Timer:359 seconds remaining =================================================== Timer:358 seconds remaining =================================================== Timer:357 seconds remaining =================================================== Timer:356 seconds remaining =================================================== Timer:355 seconds remaining =================================================== Timer:354 seconds remaining =================================================== Timer:353 seconds remaining =================================================== Timer:352 seconds remaining =================================================== Timer:351 seconds remaining =================================================== Timer:350 seconds remaining =================================================== Timer:349 seconds remaining =================================================== Timer:348 seconds remaining =================================================== Timer:347 seconds remaining =================================================== Timer:346 seconds remaining =================================================== Timer:345 seconds remaining =================================================== Timer:344 seconds remaining =================================================== Timer:343 seconds remaining =================================================== Timer:342 seconds remaining =================================================== Timer:341 seconds remaining =================================================== Timer:340 seconds remaining =================================================== Timer:339 seconds remaining =================================================== Timer:338 seconds remaining =================================================== Timer:337 seconds remaining =================================================== Timer:336 seconds remaining =================================================== Timer:335 seconds remaining =================================================== Timer:334 seconds remaining =================================================== Timer:333 seconds remaining =================================================== Timer:332 seconds remaining =================================================== Timer:331 seconds remaining =================================================== Timer:330 seconds remaining =================================================== Timer:329 seconds remaining =================================================== Timer:328 seconds remaining =================================================== Timer:327 seconds remaining =================================================== Timer:326 seconds remaining =================================================== Timer:325 seconds remaining =================================================== Timer:324 seconds remaining =================================================== Timer:323 seconds remaining =================================================== Timer:322 seconds remaining =================================================== Timer:321 seconds remaining =================================================== Timer:320 seconds remaining =================================================== Timer:319 seconds remaining =================================================== Timer:318 seconds remaining =================================================== Timer:317 seconds remaining =================================================== Timer:316 seconds remaining =================================================== Timer:315 seconds remaining =================================================== Timer:314 seconds remaining =================================================== Timer:313 seconds remaining =================================================== Timer:312 seconds remaining =================================================== Timer:311 seconds remaining =================================================== Timer:310 seconds remaining =================================================== Timer:309 seconds remaining =================================================== Timer:308 seconds remaining =================================================== Timer:307 seconds remaining =================================================== Timer:306 seconds remaining =================================================== Timer:305 seconds remaining =================================================== Timer:304 seconds remaining =================================================== Timer:303 seconds remaining =================================================== Timer:302 seconds remaining =================================================== Timer:301 seconds remaining =================================================== Timer:300 seconds remaining =================================================== Timer:299 seconds remaining =================================================== Timer:298 seconds remaining =================================================== Timer:297 seconds remaining =================================================== Timer:296 seconds remaining =================================================== Timer:295 seconds remaining =================================================== Timer:294 seconds remaining =================================================== Timer:293 seconds remaining =================================================== Timer:292 seconds remaining =================================================== Timer:291 seconds remaining =================================================== Timer:290 seconds remaining =================================================== Timer:289 seconds remaining =================================================== Timer:288 seconds remaining =================================================== Timer:287 seconds remaining =================================================== Timer:286 seconds remaining =================================================== Timer:285 seconds remaining =================================================== Timer:284 seconds remaining =================================================== Timer:283 seconds remaining =================================================== Timer:282 seconds remaining =================================================== Timer:281 seconds remaining =================================================== Timer:280 seconds remaining =================================================== Timer:279 seconds remaining =================================================== Timer:278 seconds remaining =================================================== Timer:277 seconds remaining =================================================== Timer:276 seconds remaining =================================================== Timer:275 seconds remaining =================================================== Timer:274 seconds remaining =================================================== Timer:273 seconds remaining =================================================== Timer:272 seconds remaining =================================================== Timer:271 seconds remaining =================================================== Timer:270 seconds remaining =================================================== Timer:269 seconds remaining =================================================== Timer:268 seconds remaining =================================================== Timer:267 seconds remaining =================================================== Timer:266 seconds remaining =================================================== Timer:265 seconds remaining =================================================== Timer:264 seconds remaining =================================================== Timer:263 seconds remaining =================================================== Timer:262 seconds remaining =================================================== Timer:261 seconds remaining =================================================== Timer:260 seconds remaining =================================================== Timer:259 seconds remaining =================================================== Timer:258 seconds remaining =================================================== Timer:257 seconds remaining =================================================== Timer:256 seconds remaining =================================================== Timer:255 seconds remaining =================================================== Timer:254 seconds remaining =================================================== Timer:253 seconds remaining =================================================== Timer:252 seconds remaining =================================================== Timer:251 seconds remaining =================================================== Timer:250 seconds remaining =================================================== Timer:249 seconds remaining =================================================== Timer:248 seconds remaining =================================================== Timer:247 seconds remaining =================================================== Timer:246 seconds remaining =================================================== Timer:245 seconds remaining =================================================== Timer:244 seconds remaining =================================================== Timer:243 seconds remaining =================================================== Timer:242 seconds remaining =================================================== Timer:241 seconds remaining =================================================== Timer:240 seconds remaining =================================================== Timer:239 seconds remaining =================================================== Timer:238 seconds remaining =================================================== Timer:237 seconds remaining =================================================== Timer:236 seconds remaining =================================================== Timer:235 seconds remaining =================================================== Timer:234 seconds remaining =================================================== Timer:233 seconds remaining =================================================== Timer:232 seconds remaining =================================================== Timer:231 seconds remaining =================================================== Timer:230 seconds remaining =================================================== Timer:229 seconds remaining =================================================== Timer:228 seconds remaining =================================================== Timer:227 seconds remaining =================================================== Timer:226 seconds remaining =================================================== Timer:225 seconds remaining =================================================== Timer:224 seconds remaining =================================================== Timer:223 seconds remaining =================================================== Timer:222 seconds remaining =================================================== Timer:221 seconds remaining =================================================== Timer:220 seconds remaining =================================================== Timer:219 seconds remaining =================================================== Timer:218 seconds remaining =================================================== Timer:217 seconds remaining =================================================== Timer:216 seconds remaining =================================================== Timer:215 seconds remaining =================================================== Timer:214 seconds remaining =================================================== Timer:213 seconds remaining =================================================== Timer:212 seconds remaining =================================================== Timer:211 seconds remaining =================================================== Timer:210 seconds remaining =================================================== Timer:209 seconds remaining =================================================== Timer:208 seconds remaining =================================================== Timer:207 seconds remaining =================================================== Timer:206 seconds remaining =================================================== Timer:205 seconds remaining =================================================== Timer:204 seconds remaining =================================================== Timer:203 seconds remaining =================================================== Timer:202 seconds remaining =================================================== Timer:201 seconds remaining =================================================== Timer:200 seconds remaining =================================================== Timer:199 seconds remaining =================================================== Timer:198 seconds remaining =================================================== Timer:197 seconds remaining =================================================== Timer:196 seconds remaining =================================================== Timer:195 seconds remaining =================================================== Timer:194 seconds remaining =================================================== Timer:193 seconds remaining =================================================== Timer:192 seconds remaining =================================================== Timer:191 seconds remaining =================================================== Timer:190 seconds remaining =================================================== Timer:189 seconds remaining =================================================== Timer:188 seconds remaining =================================================== Timer:187 seconds remaining =================================================== Timer:186 seconds remaining =================================================== Timer:185 seconds remaining =================================================== Timer:184 seconds remaining =================================================== Timer:183 seconds remaining =================================================== Timer:182 seconds remaining =================================================== Timer:181 seconds remaining =================================================== Timer:180 seconds remaining =================================================== Timer:179 seconds remaining =================================================== Timer:178 seconds remaining =================================================== Timer:177 seconds remaining =================================================== Timer:176 seconds remaining =================================================== Timer:175 seconds remaining =================================================== Timer:174 seconds remaining =================================================== Timer:173 seconds remaining =================================================== Timer:172 seconds remaining =================================================== Timer:171 seconds remaining =================================================== Timer:170 seconds remaining =================================================== Timer:169 seconds remaining =================================================== Timer:168 seconds remaining =================================================== Timer:167 seconds remaining =================================================== Timer:166 seconds remaining =================================================== Timer:165 seconds remaining =================================================== Timer:164 seconds remaining =================================================== Timer:163 seconds remaining =================================================== Timer:162 seconds remaining =================================================== Timer:161 seconds remaining =================================================== Timer:160 seconds remaining =================================================== Timer:159 seconds remaining =================================================== Timer:158 seconds remaining =================================================== Timer:157 seconds remaining =================================================== Timer:156 seconds remaining =================================================== Timer:155 seconds remaining =================================================== Timer:154 seconds remaining =================================================== Timer:153 seconds remaining =================================================== Timer:152 seconds remaining =================================================== Timer:151 seconds remaining =================================================== Timer:150 seconds remaining =================================================== Timer:149 seconds remaining =================================================== Timer:148 seconds remaining =================================================== Timer:147 seconds remaining =================================================== Timer:146 seconds remaining =================================================== Timer:145 seconds remaining =================================================== Timer:144 seconds remaining =================================================== Timer:143 seconds remaining =================================================== Timer:142 seconds remaining =================================================== Timer:141 seconds remaining =================================================== Timer:140 seconds remaining =================================================== Timer:139 seconds remaining =================================================== Timer:138 seconds remaining =================================================== Timer:137 seconds remaining =================================================== Timer:136 seconds remaining =================================================== Timer:135 seconds remaining =================================================== Timer:134 seconds remaining =================================================== Timer:133 seconds remaining =================================================== Timer:132 seconds remaining =================================================== Timer:131 seconds remaining =================================================== Timer:130 seconds remaining =================================================== Timer:129 seconds remaining =================================================== Timer:128 seconds remaining =================================================== Timer:127 seconds remaining =================================================== Timer:126 seconds remaining =================================================== Timer:125 seconds remaining =================================================== Timer:124 seconds remaining =================================================== Timer:123 seconds remaining =================================================== Timer:122 seconds remaining =================================================== Timer:121 seconds remaining =================================================== Timer:120 seconds remaining =================================================== Timer:119 seconds remaining =================================================== Timer:118 seconds remaining =================================================== Timer:117 seconds remaining =================================================== Timer:116 seconds remaining =================================================== Timer:115 seconds remaining =================================================== Timer:114 seconds remaining =================================================== Timer:113 seconds remaining =================================================== Timer:112 seconds remaining =================================================== Timer:111 seconds remaining =================================================== Timer:110 seconds remaining =================================================== Timer:109 seconds remaining =================================================== Timer:108 seconds remaining =================================================== Timer:107 seconds remaining =================================================== Timer:106 seconds remaining =================================================== Timer:105 seconds remaining =================================================== Timer:104 seconds remaining =================================================== Timer:103 seconds remaining =================================================== Timer:102 seconds remaining =================================================== Timer:101 seconds remaining =================================================== Timer:100 seconds remaining =================================================== Timer:99 seconds remaining =================================================== Timer:98 seconds remaining =================================================== Timer:97 seconds remaining =================================================== Timer:96 seconds remaining =================================================== Timer:95 seconds remaining =================================================== Timer:94 seconds remaining =================================================== Timer:93 seconds remaining =================================================== Timer:92 seconds remaining =================================================== Timer:91 seconds remaining =================================================== Timer:90 seconds remaining =================================================== Timer:89 seconds remaining =================================================== Timer:88 seconds remaining =================================================== Timer:87 seconds remaining =================================================== Timer:86 seconds remaining =================================================== Timer:85 seconds remaining =================================================== Timer:84 seconds remaining =================================================== Timer:83 seconds remaining =================================================== Timer:82 seconds remaining =================================================== Timer:81 seconds remaining =================================================== Timer:80 seconds remaining =================================================== Timer:79 seconds remaining =================================================== Timer:78 seconds remaining =================================================== Timer:77 seconds remaining =================================================== Timer:76 seconds remaining =================================================== Timer:75 seconds remaining =================================================== Timer:74 seconds remaining =================================================== Timer:73 seconds remaining =================================================== Timer:72 seconds remaining =================================================== Timer:71 seconds remaining =================================================== Timer:70 seconds remaining =================================================== Timer:69 seconds remaining =================================================== Timer:68 seconds remaining =================================================== Timer:67 seconds remaining =================================================== Timer:66 seconds remaining =================================================== Timer:65 seconds remaining =================================================== Timer:64 seconds remaining =================================================== Timer:63 seconds remaining =================================================== Timer:62 seconds remaining =================================================== Timer:61 seconds remaining =================================================== Timer:60 seconds remaining =================================================== Timer:59 seconds remaining =================================================== Timer:58 seconds remaining =================================================== Timer:57 seconds remaining =================================================== Timer:56 seconds remaining =================================================== Timer:55 seconds remaining =================================================== Timer:54 seconds remaining =================================================== Timer:53 seconds remaining =================================================== Timer:52 seconds remaining =================================================== Timer:51 seconds remaining =================================================== Timer:50 seconds remaining =================================================== Timer:49 seconds remaining =================================================== Timer:48 seconds remaining =================================================== Timer:47 seconds remaining =================================================== Timer:46 seconds remaining =================================================== Timer:45 seconds remaining =================================================== Timer:44 seconds remaining =================================================== Timer:43 seconds remaining =================================================== Timer:42 seconds remaining =================================================== Timer:41 seconds remaining =================================================== Timer:40 seconds remaining =================================================== Timer:39 seconds remaining =================================================== Timer:38 seconds remaining =================================================== Timer:37 seconds remaining =================================================== Timer:36 seconds remaining =================================================== Timer:35 seconds remaining =================================================== Timer:34 seconds remaining =================================================== Timer:33 seconds remaining =================================================== Timer:32 seconds remaining =================================================== Timer:31 seconds remaining =================================================== Timer:30 seconds remaining =================================================== Timer:29 seconds remaining =================================================== Timer:28 seconds remaining =================================================== Timer:27 seconds remaining =================================================== Timer:26 seconds remaining =================================================== Timer:25 seconds remaining =================================================== Timer:24 seconds remaining =================================================== Timer:23 seconds remaining =================================================== Timer:22 seconds remaining =================================================== Timer:21 seconds remaining =================================================== Timer:20 seconds remaining =================================================== Timer:19 seconds remaining =================================================== Timer:18 seconds remaining =================================================== Timer:17 seconds remaining =================================================== Timer:16 seconds remaining =================================================== Timer:15 seconds remaining =================================================== Timer:14 seconds remaining =================================================== Timer:13 seconds remaining =================================================== Timer:12 seconds remaining =================================================== Timer:11 seconds remaining =================================================== Timer:10 seconds remaining =================================================== Timer: 9 seconds remaining =================================================== Timer: 8 seconds remaining =================================================== Timer: 7 seconds remaining =================================================== Timer: 6 seconds remaining =================================================== Timer: 5 seconds remaining =================================================== Timer: 4 seconds remaining =================================================== Timer: 3 seconds remaining =================================================== Timer: 2 seconds remaining =================================================== Timer: 1 seconds remaining =======================
2019-10-11 11:39:59 :: configuring: config system global 
2019-10-11 11:39:59 :: configuring: set admintimeout 480 
2019-10-11 11:40:00 :: configuring: end 
2019-10-11 11:40:00 :: configuring: config system global 
2019-10-11 11:40:01 :: configuring: set admintimeout 480 
2019-10-11 11:40:01 :: configuring: end 
2019-10-11 11:40:02 :: configuring: config system global 
2019-10-11 11:40:03 :: configuring: set admintimeout 480 
2019-10-11 11:40:03 :: configuring: end 
2019-10-11 11:40:04 :: configuring: config system global 
2019-10-11 11:40:04 :: configuring: set admintimeout 480 
2019-10-11 11:40:05 :: configuring: end 
2019-10-11 11:40:05 :: *****************Configure device on comserver = 10.105.50.3,port=2057 
2019-10-11 11:40:07 :: get system status 
2019-10-11 11:40:07 :: Version: FortiSwitch-548D-FPOE v6.2.0,build0192,191005 (Interim) 
2019-10-11 11:40:07 :: Serial-Number: S548DF4K17000014 
2019-10-11 11:40:07 :: BIOS version: 04000016 
2019-10-11 11:40:07 :: System Part-Number: P18049-05 
2019-10-11 11:40:07 :: Burn in MAC: 70:4c:a5:82:96:72 
2019-10-11 11:40:07 :: Hostname: S548DF4K17000014 
2019-10-11 11:40:07 :: Distribution: International 
2019-10-11 11:40:07 :: Branch point: 192 
2019-10-11 11:40:07 :: System time: Fri Oct 11 11:40:06 2019 
2019-10-11 11:40:07 ::  
2019-10-11 11:40:07 :: S548DF4K17000014 # 
2019-10-11 11:40:07 :: configuring: config system interface
 
2019-10-11 11:40:08 :: configuring:     edit "mgmt"
 
2019-10-11 11:40:08 :: configuring: 	set mode static
 
2019-10-11 11:40:09 :: configuring: 	end
 
2019-10-11 11:40:09 :: configuring: 
 
2019-10-11 11:40:10 :: configuring: config system interface
 
2019-10-11 11:40:10 :: configuring:     edit "mgmt"
 
2019-10-11 11:40:11 :: configuring: 	set mode static
 
2019-10-11 11:40:11 :: configuring:         set ip 10.105.50.59 255.255.255.0
 
2019-10-11 11:40:12 :: configuring:         set allowaccess ping https ssh telnet 
 
2019-10-11 11:40:12 :: configuring:     next
 
2019-10-11 11:40:13 :: configuring:     
 
2019-10-11 11:40:13 :: configuring:     edit "internal"
 
2019-10-11 11:40:14 :: configuring:        unset defaultgw   
 
2019-10-11 11:40:14 :: configuring:     end
 
2019-10-11 11:40:15 :: configuring: 
 
2019-10-11 11:40:15 :: configuring: config router static
 
2019-10-11 11:40:16 :: configuring:     edit 1
 
2019-10-11 11:40:16 :: configuring:         set device "mgmt"
 
2019-10-11 11:40:17 :: configuring:         set dst 0.0.0.0 0.0.0.0
 
2019-10-11 11:40:17 :: configuring:         set gateway 10.105.50.254
 
2019-10-11 11:40:18 :: configuring:     next
 
2019-10-11 11:40:18 :: configuring: end
 
2019-10-11 11:40:19 :: configuring: config system global
 
2019-10-11 11:40:19 :: configuring:      set admintimeout 480
 
2019-10-11 11:40:20 :: configuring: end 
2019-10-11 11:40:20 :: *****************Configure device on comserver = 10.105.50.3,port=2056 
2019-10-11 11:40:22 :: get system status 
2019-10-11 11:40:22 :: Version: FortiSwitch-548D-FPOE v6.2.0,build0192,191005 (Interim) 
2019-10-11 11:40:22 :: Serial-Number: S548DF4K17000028 
2019-10-11 11:40:22 :: BIOS version: 04000016 
2019-10-11 11:40:22 :: System Part-Number: P18049-05 
2019-10-11 11:40:22 :: Burn in MAC: 70:4c:a5:82:99:82 
2019-10-11 11:40:22 :: Hostname: S548DF4K17000028 
2019-10-11 11:40:22 :: Distribution: International 
2019-10-11 11:40:22 :: Branch point: 192 
2019-10-11 11:40:22 :: System time: Fri Oct 11 11:40:21 2019 
2019-10-11 11:40:22 ::  
2019-10-11 11:40:22 :: S548DF4K17000028 # 
2019-10-11 11:40:22 :: configuring: config system interface
 
2019-10-11 11:40:23 :: configuring:     edit "mgmt"
 
2019-10-11 11:40:23 :: configuring: 	set mode static
 
2019-10-11 11:40:24 :: configuring: 	end
 
2019-10-11 11:40:24 :: configuring: config system interface
 
2019-10-11 11:40:25 :: configuring:     edit "mgmt"
 
2019-10-11 11:40:25 :: configuring: 	set mode static
 
2019-10-11 11:40:26 :: configuring:         set ip 10.105.50.60 255.255.255.0
 
2019-10-11 11:40:26 :: configuring:         set allowaccess ping https ssh telnet 
 
2019-10-11 11:40:27 :: configuring:     next
 
2019-10-11 11:40:27 :: configuring:     
 
2019-10-11 11:40:28 :: configuring:     edit "internal"
 
2019-10-11 11:40:28 :: configuring:        unset defaultgw   
 
2019-10-11 11:40:29 :: configuring:     end
 
2019-10-11 11:40:29 :: configuring: 
 
2019-10-11 11:40:30 :: configuring: config router static
 
2019-10-11 11:40:30 :: configuring:     edit 1
 
2019-10-11 11:40:31 :: configuring:         set device "mgmt"
 
2019-10-11 11:40:31 :: configuring:         set dst 0.0.0.0 0.0.0.0
 
2019-10-11 11:40:32 :: configuring:         set gateway 10.105.50.254
 
2019-10-11 11:40:32 :: configuring:     next
 
2019-10-11 11:40:33 :: configuring: end
 
2019-10-11 11:40:33 :: configuring: 
 
2019-10-11 11:40:34 :: configuring: config system global
 
2019-10-11 11:40:34 :: configuring:      set admintimeout 480
 
2019-10-11 11:40:35 :: configuring: end 
2019-10-11 11:40:35 :: *****************Configure device on comserver = 10.105.50.1,port=2075 
2019-10-11 11:40:37 :: get system status 
2019-10-11 11:40:37 :: Version: FortiSwitch-548D-FPOE v6.2.0,build0192,191005 (Interim) 
2019-10-11 11:40:37 :: Serial-Number: S548DF4K16000653 
2019-10-11 11:40:37 :: BIOS version: 04000013 
2019-10-11 11:40:37 :: System Part-Number: P18049-04 
2019-10-11 11:40:37 :: Burn in MAC: 90:6c:ac:62:14:3e 
2019-10-11 11:40:37 :: Hostname: S548DF4K16000653 
2019-10-11 11:40:37 :: Distribution: International 
2019-10-11 11:40:37 :: Branch point: 192 
2019-10-11 11:40:37 :: System time: Fri Oct 11 11:40:36 2019 
2019-10-11 11:40:37 ::  
2019-10-11 11:40:37 :: S548DF4K16000653 # 
2019-10-11 11:40:37 :: configuring: config system interface
 
2019-10-11 11:40:38 :: configuring:     edit "mgmt"
 
2019-10-11 11:40:38 :: configuring: 	set mode static
 
2019-10-11 11:40:39 :: configuring: 	end
 
2019-10-11 11:40:39 :: configuring: config system interface
 
2019-10-11 11:40:40 :: configuring:     edit "mgmt"
 
2019-10-11 11:40:40 :: configuring: 	set mode static
 
2019-10-11 11:40:41 :: configuring:         set ip 10.105.50.62 255.255.255.0
 
2019-10-11 11:40:41 :: configuring:         set allowaccess ping https ssh telnet 
 
2019-10-11 11:40:42 :: configuring:     next
 
2019-10-11 11:40:42 :: configuring:     
 
2019-10-11 11:40:43 :: configuring:     edit "internal"
 
2019-10-11 11:40:43 :: configuring:        unset defaultgw   
 
2019-10-11 11:40:44 :: configuring:     end
 
2019-10-11 11:40:44 :: configuring:     
 
2019-10-11 11:40:45 :: configuring: config router static
 
2019-10-11 11:40:45 :: configuring:     edit 1
 
2019-10-11 11:40:46 :: configuring:         set device "mgmt"
 
2019-10-11 11:40:46 :: configuring:         set dst 0.0.0.0 0.0.0.0
 
2019-10-11 11:40:47 :: configuring:         set gateway 10.105.50.254
 
2019-10-11 11:40:47 :: configuring:     next
 
2019-10-11 11:40:48 :: configuring: end
 
2019-10-11 11:40:48 :: configuring: config system global
 
2019-10-11 11:40:49 :: configuring:      set admintimeout 480
 
2019-10-11 11:40:50 :: configuring: end 
2019-10-11 11:40:50 :: *****************Configure device on comserver = 10.105.50.1,port=2078 
2019-10-11 11:40:52 :: get system status 
2019-10-11 11:40:52 :: Version: FortiSwitch-548D v6.2.0,build0192,191005 (Interim) 
2019-10-11 11:40:52 :: Serial-Number: S548DN4K17000133 
2019-10-11 11:40:52 :: BIOS version: 04000013 
2019-10-11 11:40:52 :: System Part-Number: P18057-06 
2019-10-11 11:40:52 :: Burn in MAC: 70:4c:a5:79:22:5a 
2019-10-11 11:40:52 :: Hostname: S548DN4K17000133 
2019-10-11 11:40:52 :: Distribution: International 
2019-10-11 11:40:52 :: Branch point: 192 
2019-10-11 11:40:52 :: System time: Fri Oct 11 11:40:50 2019 
2019-10-11 11:40:52 ::  
2019-10-11 11:40:52 :: S548DN4K17000133 # 
2019-10-11 11:40:52 :: configuring: config system interface
 
2019-10-11 11:40:53 :: configuring:     edit "mgmt"
 
2019-10-11 11:40:53 :: configuring: 	set mode static
 
2019-10-11 11:40:54 :: configuring: 	end
 
2019-10-11 11:40:54 :: configuring: 
 
2019-10-11 11:40:55 :: configuring: config system interface
 
2019-10-11 11:40:55 :: configuring:     edit "mgmt"
 
2019-10-11 11:40:56 :: configuring: 	set mode static
 
2019-10-11 11:40:56 :: configuring:         set ip 10.105.50.63 255.255.255.0
 
2019-10-11 11:40:57 :: configuring:         set allowaccess ping https ssh telnet 
 
2019-10-11 11:40:57 :: configuring:     next
 
2019-10-11 11:40:58 :: configuring:     
 
2019-10-11 11:40:58 :: configuring:     edit "internal"
 
2019-10-11 11:40:59 :: configuring:        unset defaultgw   
 
2019-10-11 11:40:59 :: configuring:     end
 
2019-10-11 11:41:00 :: configuring:     
 
2019-10-11 11:41:00 :: configuring: config router static
 
2019-10-11 11:41:01 :: configuring:     edit 1
 
2019-10-11 11:41:01 :: configuring:         set device "mgmt"
 
2019-10-11 11:41:02 :: configuring:         set dst 0.0.0.0 0.0.0.0
 
2019-10-11 11:41:02 :: configuring:         set gateway 10.105.50.254
 
2019-10-11 11:41:03 :: configuring:     next
 
2019-10-11 11:41:03 :: configuring: end
 
2019-10-11 11:41:04 :: configuring: 
 
2019-10-11 11:41:04 :: configuring: config system global
 
2019-10-11 11:41:05 :: configuring:      set admintimeout 480
 
2019-10-11 11:41:05 :: configuring: end 
2019-10-11 11:41:06 :: ------------  end of configuring fortigate and FSW  -------------------- 
########################################################################################
2019-10-11 11:41:08 ::        unset defaultgw    
2019-10-11 11:41:08 ::  
2019-10-11 11:41:08 :: S548DF4K17000014 (internal) #  
2019-10-11 11:41:08 :: S548DF4K17000014 (internal) #     end 
2019-10-11 11:41:08 ::  
2019-10-11 11:41:08 :: S548DF4K17000014 #  
2019-10-11 11:41:08 :: S548DF4K17000014 #  
2019-10-11 11:41:08 :: S548DF4K17000014 #  
2019-10-11 11:41:08 :: S548DF4K17000014 # config router static 
2019-10-11 11:41:08 ::  
2019-10-11 11:41:08 :: S548DF4K17000014 (static) #  
2019-10-11 11:41:08 :: S548DF4K17000014 (static) #     edit 1 
2019-10-11 11:41:08 :: new entry '1' added 
2019-10-11 11:41:08 ::  
2019-10-11 11:41:08 :: S548DF4K17000014 (1) #  
2019-10-11 11:41:08 :: S548DF4K17000014 (1) #         set device "mgmt" 
2019-10-11 11:41:08 ::  
2019-10-11 11:41:08 :: S548DF4K17000014 (1) #  
2019-10-11 11:41:08 :: S548DF4K17000014 (1) #         set dst 0.0.0.0 0.0.0.0 
2019-10-11 11:41:08 ::  
2019-10-11 11:41:08 :: S548DF4K17000014 (1) #  
2019-10-11 11:41:08 :: S548DF4K17000014 (1) #         set gateway 10.105.50.254 
2019-10-11 11:41:08 ::  
2019-10-11 11:41:08 :: S548DF4K17000014 (1) #  
2019-10-11 11:41:08 :: S548DF4K17000014 (1) #     next 
2019-10-11 11:41:08 ::  
2019-10-11 11:41:08 :: S548DF4K17000014 (static) #  
2019-10-11 11:41:08 :: S548DF4K17000014 (static) # end 
2019-10-11 11:41:08 ::  
2019-10-11 11:41:08 :: S548DF4K17000014 #  
2019-10-11 11:41:08 :: S548DF4K17000014 # config system global 
2019-10-11 11:41:08 ::  
2019-10-11 11:41:08 :: S548DF4K17000014 (global) #  
2019-10-11 11:41:08 :: S548DF4K17000014 (global) #      set admintimeout 480 
2019-10-11 11:41:08 ::  
2019-10-11 11:41:08 :: S548DF4K17000014 (global) #  
2019-10-11 11:41:08 :: S548DF4K17000014 (global) # end 
2019-10-11 11:41:08 ::  
2019-10-11 11:41:08 :: S548DF4K17000014 # get system status 
2019-10-11 11:41:08 :: Version: FortiSwitch-548D-FPOE v6.2.0,build0192,191005 (Interim) 
2019-10-11 11:41:08 :: Serial-Number: S548DF4K17000014 
2019-10-11 11:41:08 :: BIOS version: 04000016 
2019-10-11 11:41:08 :: System Part-Number: P18049-05 
2019-10-11 11:41:08 :: Burn in MAC: 70:4c:a5:82:96:72 
2019-10-11 11:41:08 :: Hostname: S548DF4K17000014 
2019-10-11 11:41:08 :: Distribution: International 
2019-10-11 11:41:08 :: Branch point: 192 
2019-10-11 11:41:08 :: System time: Fri Oct 11 11:41:06 2019 
2019-10-11 11:41:08 ::  
2019-10-11 11:41:08 :: S548DF4K17000014 # 
2019-10-11 11:41:10 :: show switch trunk 
2019-10-11 11:41:10 :: config switch trunk 
2019-10-11 11:41:10 ::     edit "704CA5CBC3DC-0" 
2019-10-11 11:41:10 ::         set mode lacp-active 
2019-10-11 11:41:10 ::         set auto-isl 1 
2019-10-11 11:41:10 ::         set isl-fortilink 1 
2019-10-11 11:41:10 ::         set mclag enable 
2019-10-11 11:41:10 ::             set members "port50" 
2019-10-11 11:41:10 ::     next 
2019-10-11 11:41:10 ::     edit "8DF4K17000028-0" 
2019-10-11 11:41:10 ::         set mode lacp-active 
2019-10-11 11:41:10 ::         set auto-isl 1 
2019-10-11 11:41:10 ::         set mclag-icl enable 
2019-10-11 11:41:10 ::             set members "port47" "port48" 
2019-10-11 11:41:10 ::     next 
2019-10-11 11:41:10 ::     edit "704CA5A8FCFA-0" 
2019-10-11 11:41:10 ::         set mode lacp-active 
2019-10-11 11:41:10 ::         set auto-isl 1 
2019-10-11 11:41:10 ::         set isl-fortilink 1 
2019-10-11 11:41:10 ::         set mclag enable 
2019-10-11 11:41:10 ::             set members "port49" 
2019-10-11 11:41:10 ::     next 
2019-10-11 11:41:10 ::     edit "sw1-trunk" 
2019-10-11 11:41:10 ::         set mode lacp-active 
2019-10-11 11:41:10 ::         set mclag enable 
2019-10-11 11:41:10 :: --More-- 
2019-10-11 11:41:12 ::                      set members "port13" 
2019-10-11 11:41:12 ::     next 
2019-10-11 11:41:12 ::     edit "core1" 
2019-10-11 11:41:12 ::         set mode lacp-active 
2019-10-11 11:41:12 ::         set auto-isl 1 
2019-10-11 11:41:12 ::         set mclag enable 
2019-10-11 11:41:12 ::             set members "port1" "port2" "port3" "port4" 
2019-10-11 11:41:12 ::     next 
2019-10-11 11:41:12 :: end 
2019-10-11 11:41:12 ::  
2019-10-11 11:41:12 :: S548DF4K17000014 # stency-check 
2019-10-11 11:41:12 :: stency-check 
2019-10-11 11:41:12 :: Unknown action 0 
2019-10-11 11:41:12 ::  
2019-10-11 11:41:12 :: S548DF4K17000014 # 
2019-10-11 11:41:14 :: get switch lldp neighbors-summary 
2019-10-11 11:41:14 ::  
2019-10-11 11:41:14 :: Capability codes: 
2019-10-11 11:41:14 :: 	R:Router, B:Bridge, T:Telephone, C:DOCSIS Cable Device 
2019-10-11 11:41:14 :: 	W:WLAN Access Point, P:Repeater, S:Station, O:Other 
2019-10-11 11:41:14 :: MED type codes: 
2019-10-11 11:41:14 :: 	Generic:Generic Endpoint (Class 1), Media:Media Endpoint (Class 2) 
2019-10-11 11:41:14 :: 	Comms:Communications Endpoint (Class 3), Network:Network Connectivity Device 
2019-10-11 11:41:14 ::  
2019-10-11 11:41:14 ::   Portname    Status   Device-name                 TTL   Capability  MED-type  Port-ID 
2019-10-11 11:41:14 ::   __________  _______  __________________________  ____  __________  ________  _______ 
2019-10-11 11:41:14 ::   port1       Up       S548DF4K16000653            120   BR          -         port1 
2019-10-11 11:41:14 ::   port2       Up       S548DF4K16000653            120   BR          -         port2 
2019-10-11 11:41:14 ::   port3       Up       S548DN4K17000133            120   BR          -         port3 
2019-10-11 11:41:14 ::   port4       Up       S548DN4K17000133            120   BR          -         port4 
2019-10-11 11:41:14 ::   port5       Down     -                           -     -           -         - 
2019-10-11 11:41:14 ::   port6       Down     -                           -     -           -         - 
2019-10-11 11:41:14 ::   port7       Down     -                           -     -           -         - 
2019-10-11 11:41:14 ::   port8       Down     -                           -     -           -         - 
2019-10-11 11:41:14 ::   port9       Down     -                           -     -           -         - 
2019-10-11 11:41:14 ::   port10      Down     -                           -     -           -         - 
2019-10-11 11:41:14 ::   port11      Down     -                           -     -           -         - 
2019-10-11 11:41:14 ::   port12      Down     -                           -     -           -         - 
2019-10-11 11:41:14 ::   port13      Down     -                           -     -           -         - 
2019-10-11 11:41:14 ::   port14      Down     -                           -     -           -         - 
2019-10-11 11:41:14 ::   port15      Down     -                           -     -           -         - 
2019-10-11 11:41:14 ::   port16      Down     -                           -     -           -         - 
2019-10-11 11:41:14 ::   port17      Down     -                           -     -           -         - 
2019-10-11 11:41:14 ::   port18      Down     -                           -     -           -         - 
2019-10-11 11:41:14 ::   port19      Down     -                           -     -           -         - 
2019-10-11 11:41:14 ::   port20      Down     -                           -     -           -         - 
2019-10-11 11:41:14 ::   port21      Down     -                           -     -           -         - 
2019-10-11 11:41:14 ::   port22      Down     -                           -     -           -         - 
2019-10-11 11:41:14 ::   port23      Down     -                           -     -           -         - 
2019-10-11 11:41:14 ::   port24      Down     -                           -     -           -         - 
2019-10-11 11:41:14 ::   port25      Down     -                           -     -           -         - 
2019-10-11 11:41:14 ::   port26      Down     -                           -     -           -         - 
2019-10-11 11:41:14 ::   port27      Down     -                           -     -           -         - 
2019-10-11 11:41:14 ::   port28      Down     -                           -     -           -         - 
2019-10-11 11:41:14 ::   port29      Down     -                           -     -           -         - 
2019-10-11 11:41:14 ::   port30      Down     -                           -     -           -         - 
2019-10-11 11:41:14 ::   port31      Down     -                           -     -           -         - 
2019-10-11 11:41:14 ::   port32      Down     -                           -     -           -         - 
2019-10-11 11:41:14 ::   port33      Down     -                           -     -           -         - 
2019-10-11 11:41:14 ::   port34      Down     -                           -     -           -         - 
2019-10-11 11:41:14 ::   port35      Down     -                           -     -           -         - 
2019-10-11 11:41:14 ::   port36      Down     -                           -     -           -         - 
2019-10-11 11:41:14 ::   port37      Down     -                           -     -           -         - 
2019-10-11 11:41:14 ::   port38      Down     -                           -     -           -         - 
2019-10-11 11:41:14 ::   port39      Down     -                           -     -           -         - 
2019-10-11 11:41:14 ::   port40      Down     -                           -     -           -         - 
2019-10-11 11:41:14 ::   port41      Down     -                           -     -           -         - 
2019-10-11 11:41:14 ::   port42      Down     -                           -     -           -         - 
2019-10-11 11:41:14 ::   port43      Down     -                           -     -           -         - 
2019-10-11 11:41:14 ::   port44      Down     -                           -     -           -         - 
2019-10-11 11:41:14 ::   port45      Down     -                           -     -           -         - 
2019-10-11 11:41:14 ::   port46      Down     -                           -     -           -         - 
2019-10-11 11:41:14 ::   port47      Up       S548DF4K17000028            120   BR          -         port47 
2019-10-11 11:41:14 ::   port48      Up       S548DF4K17000028            120   BR          -         port48 
2019-10-11 11:41:14 ::   port49      Up       FortiGate-3960E             120   BR          -         70:4c:a5:a8:fc:c6 
2019-10-11 11:41:14 ::   port50      Up       FortiGate-3960E             120   BR          -         70:4c:a5:cb:c3:a8 
2019-10-11 11:41:14 ::   port51      Down     -                           -     -           -         - 
2019-10-11 11:41:14 ::   port52      Down     -                           -     -           -         - 
2019-10-11 11:41:14 ::   port53      Down     -                           -     -           -         - 
2019-10-11 11:41:14 ::   port54      Down     -                           -     -           -         - 
2019-10-11 11:41:14 ::  
2019-10-11 11:41:14 :: S548DF4K17000014 # 
2019-10-11 11:41:16 :: show switch interface port39 
2019-10-11 11:41:16 :: config switch interface 
2019-10-11 11:41:16 ::     edit "port39" 
2019-10-11 11:41:16 ::         set allowed-vlans 4093 
2019-10-11 11:41:16 ::         set untagged-vlans 4093 
2019-10-11 11:41:16 ::         set snmp-index 39 
2019-10-11 11:41:16 ::     next 
2019-10-11 11:41:16 :: end 
2019-10-11 11:41:16 ::  
2019-10-11 11:41:16 :: S548DF4K17000014 # 
########################################################################################
2019-10-11 11:41:18 ::     end 
2019-10-11 11:41:18 ::  
2019-10-11 11:41:18 :: S548DF4K17000028 #  
2019-10-11 11:41:18 :: S548DF4K17000028 #  
2019-10-11 11:41:18 :: S548DF4K17000028 #  
2019-10-11 11:41:18 :: S548DF4K17000028 # config router static 
2019-10-11 11:41:18 ::  
2019-10-11 11:41:18 :: S548DF4K17000028 (static) #  
2019-10-11 11:41:18 :: S548DF4K17000028 (static) #     edit 1 
2019-10-11 11:41:18 :: new entry '1' added 
2019-10-11 11:41:18 ::  
2019-10-11 11:41:18 :: S548DF4K17000028 (1) #  
2019-10-11 11:41:18 :: S548DF4K17000028 (1) #         set device "mgmt" 
2019-10-11 11:41:18 ::  
2019-10-11 11:41:18 :: S548DF4K17000028 (1) #  
2019-10-11 11:41:18 :: S548DF4K17000028 (1) #         set dst 0.0.0.0 0.0.0.0 
2019-10-11 11:41:18 ::  
2019-10-11 11:41:18 :: S548DF4K17000028 (1) #  
2019-10-11 11:41:18 :: S548DF4K17000028 (1) #         set gateway 10.105.50.254 
2019-10-11 11:41:18 ::  
2019-10-11 11:41:18 :: S548DF4K17000028 (1) #  
2019-10-11 11:41:18 :: S548DF4K17000028 (1) #     next 
2019-10-11 11:41:18 ::  
2019-10-11 11:41:18 :: S548DF4K17000028 (static) #  
2019-10-11 11:41:18 :: S548DF4K17000028 (static) # end 
2019-10-11 11:41:18 ::  
2019-10-11 11:41:18 :: S548DF4K17000028 #  
2019-10-11 11:41:18 :: S548DF4K17000028 #  
2019-10-11 11:41:18 :: S548DF4K17000028 #  
2019-10-11 11:41:18 :: S548DF4K17000028 # config system global 
2019-10-11 11:41:18 ::  
2019-10-11 11:41:18 :: S548DF4K17000028 (global) #  
2019-10-11 11:41:18 :: S548DF4K17000028 (global) #      set admintimeout 480 
2019-10-11 11:41:18 ::  
2019-10-11 11:41:18 :: S548DF4K17000028 (global) #  
2019-10-11 11:41:18 :: S548DF4K17000028 (global) # end 
2019-10-11 11:41:18 ::  
2019-10-11 11:41:18 :: S548DF4K17000028 # get system status 
2019-10-11 11:41:18 :: Version: FortiSwitch-548D-FPOE v6.2.0,build0192,191005 (Interim) 
2019-10-11 11:41:18 :: Serial-Number: S548DF4K17000028 
2019-10-11 11:41:18 :: BIOS version: 04000016 
2019-10-11 11:41:18 :: System Part-Number: P18049-05 
2019-10-11 11:41:18 :: Burn in MAC: 70:4c:a5:82:99:82 
2019-10-11 11:41:18 :: Hostname: S548DF4K17000028 
2019-10-11 11:41:18 :: Distribution: International 
2019-10-11 11:41:18 :: Branch point: 192 
2019-10-11 11:41:18 :: System time: Fri Oct 11 11:41:16 2019 
2019-10-11 11:41:18 ::  
2019-10-11 11:41:18 :: S548DF4K17000028 # 
2019-10-11 11:41:20 :: show switch trunk 
2019-10-11 11:41:20 :: config switch trunk 
2019-10-11 11:41:20 ::     edit "8DF4K17000014-0" 
2019-10-11 11:41:20 ::         set mode lacp-active 
2019-10-11 11:41:20 ::         set auto-isl 1 
2019-10-11 11:41:20 ::         set mclag-icl enable 
2019-10-11 11:41:20 ::             set members "port47" "port48" 
2019-10-11 11:41:20 ::     next 
2019-10-11 11:41:20 ::     edit "704CA5A8FCFA-0" 
2019-10-11 11:41:20 ::         set mode lacp-active 
2019-10-11 11:41:20 ::         set auto-isl 1 
2019-10-11 11:41:20 ::         set isl-fortilink 1 
2019-10-11 11:41:20 ::         set mclag enable 
2019-10-11 11:41:20 ::             set members "port49" 
2019-10-11 11:41:20 ::     next 
2019-10-11 11:41:20 ::     edit "704CA5CBC3DC-0" 
2019-10-11 11:41:20 ::         set mode lacp-active 
2019-10-11 11:41:20 ::         set auto-isl 1 
2019-10-11 11:41:20 ::         set isl-fortilink 1 
2019-10-11 11:41:20 ::         set mclag enable 
2019-10-11 11:41:20 ::             set members "port50" 
2019-10-11 11:41:20 ::     next 
2019-10-11 11:41:20 ::     edit "sw1-trunk" 
2019-10-11 11:41:20 ::         set mode lacp-active 
2019-10-11 11:41:20 ::         set mclag enable 
2019-10-11 11:41:20 :: --More-- 
2019-10-11 11:41:22 ::                      set members "port13" 
2019-10-11 11:41:22 ::     next 
2019-10-11 11:41:22 ::     edit "_FlInK1_MLAG0_" 
2019-10-11 11:41:22 ::         set mode lacp-active 
2019-10-11 11:41:22 ::         set auto-isl 1 
2019-10-11 11:41:22 ::         set mclag enable 
2019-10-11 11:41:22 ::             set members stency-check 
2019-10-11 11:41:22 :: "port3" "port4" "port2" "port1" 
2019-10-11 11:41:22 ::     next 
2019-10-11 11:41:22 :: end 
2019-10-11 11:41:22 ::  
2019-10-11 11:41:22 :: S548DF4K17000028 # stency-check 
2019-10-11 11:41:22 :: Unknown action 0 
2019-10-11 11:41:22 ::  
2019-10-11 11:41:22 :: S548DF4K17000028 # 
2019-10-11 11:41:24 :: get switch lldp neighbors-summary 
2019-10-11 11:41:24 ::  
2019-10-11 11:41:24 :: Capability codes: 
2019-10-11 11:41:24 :: 	R:Router, B:Bridge, T:Telephone, C:DOCSIS Cable Device 
2019-10-11 11:41:24 :: 	W:WLAN Access Point, P:Repeater, S:Station, O:Other 
2019-10-11 11:41:24 :: MED type codes: 
2019-10-11 11:41:24 :: 	Generic:Generic Endpoint (Class 1), Media:Media Endpoint (Class 2) 
2019-10-11 11:41:24 :: 	Comms:Communications Endpoint (Class 3), Network:Network Connectivity Device 
2019-10-11 11:41:24 ::  
2019-10-11 11:41:24 ::   Portname    Status   Device-name                 TTL   Capability  MED-type  Port-ID 
2019-10-11 11:41:24 ::   __________  _______  __________________________  ____  __________  ________  _______ 
2019-10-11 11:41:24 ::   port1       Up       S548DN4K17000133            120   BR          -         port1 
2019-10-11 11:41:24 ::   port2       Up       S548DN4K17000133            120   BR          -         port2 
2019-10-11 11:41:24 ::   port3       Up       S548DF4K16000653            120   BR          -         port3 
2019-10-11 11:41:24 ::   port4       Up       S548DF4K16000653            120   BR          -         port4 
2019-10-11 11:41:24 ::   port5       Down     -                           -     -           -         - 
2019-10-11 11:41:24 ::   port6       Down     -                           -     -           -         - 
2019-10-11 11:41:24 ::   port7       Down     -                           -     -           -         - 
2019-10-11 11:41:24 ::   port8       Down     -                           -     -           -         - 
2019-10-11 11:41:24 ::   port9       Down     -                           -     -           -         - 
2019-10-11 11:41:24 ::   port10      Down     -                           -     -           -         - 
2019-10-11 11:41:24 ::   port11      Down     -                           -     -           -         - 
2019-10-11 11:41:24 ::   port12      Down     -                           -     -           -         - 
2019-10-11 11:41:24 ::   port13      Down     -                           -     -           -         - 
2019-10-11 11:41:24 ::   port14      Down     -                           -     -           -         - 
2019-10-11 11:41:24 ::   port15      Down     -                           -     -           -         - 
2019-10-11 11:41:24 ::   port16      Down     -                           -     -           -         - 
2019-10-11 11:41:24 ::   port17      Down     -                           -     -           -         - 
2019-10-11 11:41:24 ::   port18      Down     -                           -     -           -         - 
2019-10-11 11:41:24 ::   port19      Down     -                           -     -           -         - 
2019-10-11 11:41:24 ::   port20      Down     -                           -     -           -         - 
2019-10-11 11:41:24 ::   port21      Down     -                           -     -           -         - 
2019-10-11 11:41:24 ::   port22      Down     -                           -     -           -         - 
2019-10-11 11:41:24 ::   port23      Down     -                           -     -           -         - 
2019-10-11 11:41:24 ::   port24      Down     -                           -     -           -         - 
2019-10-11 11:41:24 ::   port25      Down     -                           -     -           -         - 
2019-10-11 11:41:24 ::   port26      Down     -                           -     -           -         - 
2019-10-11 11:41:24 ::   port27      Down     -                           -     -           -         - 
2019-10-11 11:41:24 ::   port28      Down     -                           -     -           -         - 
2019-10-11 11:41:24 ::   port29      Down     -                           -     -           -         - 
2019-10-11 11:41:24 ::   port30      Down     -                           -     -           -         - 
2019-10-11 11:41:24 ::   port31      Down     -                           -     -           -         - 
2019-10-11 11:41:24 ::   port32      Down     -                           -     -           -         - 
2019-10-11 11:41:24 ::   port33      Down     -                           -     -           -         - 
2019-10-11 11:41:24 ::   port34      Down     -                           -     -           -         - 
2019-10-11 11:41:24 ::   port35      Down     -                           -     -           -         - 
2019-10-11 11:41:24 ::   port36      Down     -                           -     -           -         - 
2019-10-11 11:41:24 ::   port37      Down     -                           -     -           -         - 
2019-10-11 11:41:24 ::   port38      Down     -                           -     -           -         - 
2019-10-11 11:41:24 ::   port39      Down     -                           -     -           -         - 
2019-10-11 11:41:24 ::   port40      Down     -                           -     -           -         - 
2019-10-11 11:41:24 ::   port41      Down     -                           -     -           -         - 
2019-10-11 11:41:24 ::   port42      Down     -                           -     -           -         - 
2019-10-11 11:41:24 ::   port43      Down     -                           -     -           -         - 
2019-10-11 11:41:24 ::   port44      Down     -                           -     -           -         - 
2019-10-11 11:41:24 ::   port45      Down     -                           -     -           -         - 
2019-10-11 11:41:24 ::   port46      Down     -                           -     -           -         - 
2019-10-11 11:41:24 ::   port47      Up       S548DF4K17000014            120   BR          -         port47 
2019-10-11 11:41:24 ::   port48      Up       S548DF4K17000014            120   BR          -         port48 
2019-10-11 11:41:24 ::   port49      Up       FortiGate-3960E             120   BR          -         70:4c:a5:a8:fc:c7 
2019-10-11 11:41:24 ::   port50      Up       FortiGate-3960E             120   BR          -         70:4c:a5:cb:c3:a9 
2019-10-11 11:41:24 ::   port51      Down     -                           -     -           -         - 
2019-10-11 11:41:24 ::   port52      Down     -                           -     -           -         - 
2019-10-11 11:41:24 ::   port53      Down     -                           -     -           -         - 
2019-10-11 11:41:24 ::   port54      Down     -                           -     -           -         - 
2019-10-11 11:41:24 ::  
2019-10-11 11:41:24 :: S548DF4K17000028 # 
2019-10-11 11:41:26 :: show switch interface port39 
2019-10-11 11:41:26 :: config switch interface 
2019-10-11 11:41:26 ::     edit "port39" 
2019-10-11 11:41:26 ::         set allowed-vlans 4093 
2019-10-11 11:41:26 ::         set untagged-vlans 4093 
2019-10-11 11:41:26 ::         set snmp-index 39 
2019-10-11 11:41:26 ::     next 
2019-10-11 11:41:26 :: end 
2019-10-11 11:41:26 ::  
2019-10-11 11:41:26 :: S548DF4K17000028 # 
########################################################################################
2019-10-11 11:41:28 ::  
2019-10-11 11:41:28 :: S548DF4K16000653 (internal) #     end 
2019-10-11 11:41:28 ::  
2019-10-11 11:41:28 :: S548DF4K16000653 #  
2019-10-11 11:41:28 :: S548DF4K16000653 #      
2019-10-11 11:41:28 :: S548DF4K16000653 #  
2019-10-11 11:41:28 :: S548DF4K16000653 # config router static 
2019-10-11 11:41:28 ::  
2019-10-11 11:41:28 :: S548DF4K16000653 (static) #  
2019-10-11 11:41:28 :: S548DF4K16000653 (static) #     edit 1 
2019-10-11 11:41:28 :: new entry '1' added 
2019-10-11 11:41:28 ::  
2019-10-11 11:41:28 :: S548DF4K16000653 (1) #  
2019-10-11 11:41:28 :: S548DF4K16000653 (1) #         set device "mgmt" 
2019-10-11 11:41:28 ::  
2019-10-11 11:41:28 :: S548DF4K16000653 (1) #  
2019-10-11 11:41:28 :: S548DF4K16000653 (1) #         set dst 0.0.0.0 0.0.0.0 
2019-10-11 11:41:28 ::  
2019-10-11 11:41:28 :: S548DF4K16000653 (1) #  
2019-10-11 11:41:28 :: S548DF4K16000653 (1) #         set gateway 10.105.50.254 
2019-10-11 11:41:28 ::  
2019-10-11 11:41:28 :: S548DF4K16000653 (1) #  
2019-10-11 11:41:28 :: S548DF4K16000653 (1) #     next 
2019-10-11 11:41:28 ::  
2019-10-11 11:41:28 :: S548DF4K16000653 (static) #  
2019-10-11 11:41:28 :: S548DF4K16000653 (static) # end 
2019-10-11 11:41:28 ::  
2019-10-11 11:41:28 :: S548DF4K16000653 #  
2019-10-11 11:41:28 :: S548DF4K16000653 # config system global 
2019-10-11 11:41:28 ::  
2019-10-11 11:41:28 :: S548DF4K16000653 (global) #  
2019-10-11 11:41:28 :: S548DF4K16000653 (global) #      set admintimeout 480 
2019-10-11 11:41:28 ::  
2019-10-11 11:41:28 :: S548DF4K16000653 (global) #  
2019-10-11 11:41:28 :: S548DF4K16000653 (global) # end 
2019-10-11 11:41:28 ::  
2019-10-11 11:41:28 :: S548DF4K16000653 # get system status 
2019-10-11 11:41:28 :: Version: FortiSwitch-548D-FPOE v6.2.0,build0192,191005 (Interim) 
2019-10-11 11:41:28 :: Serial-Number: S548DF4K16000653 
2019-10-11 11:41:28 :: BIOS version: 04000013 
2019-10-11 11:41:28 :: System Part-Number: P18049-04 
2019-10-11 11:41:28 :: Burn in MAC: 90:6c:ac:62:14:3e 
2019-10-11 11:41:28 :: Hostname: S548DF4K16000653 
2019-10-11 11:41:28 :: Distribution: International 
2019-10-11 11:41:28 :: Branch point: 192 
2019-10-11 11:41:28 :: System time: Fri Oct 11 11:41:26 2019 
2019-10-11 11:41:28 ::  
2019-10-11 11:41:28 :: S548DF4K16000653 # 
2019-10-11 11:41:30 :: show switch trunk 
2019-10-11 11:41:30 :: config switch trunk 
2019-10-11 11:41:30 ::     edit "8DN4K17000133-0" 
2019-10-11 11:41:30 ::         set mode lacp-active 
2019-10-11 11:41:30 ::         set auto-isl 1 
2019-10-11 11:41:30 ::         set mclag-icl enable 
2019-10-11 11:41:30 ::             set members "port47" "port48" 
2019-10-11 11:41:30 ::     next 
2019-10-11 11:41:30 ::     edit "trunk1" 
2019-10-11 11:41:30 ::         set mode lacp-active 
2019-10-11 11:41:30 ::         set mclag enable 
2019-10-11 11:41:30 ::             set members "port13" 
2019-10-11 11:41:30 ::     next 
2019-10-11 11:41:30 ::     edit "_FlInK1_MLAG0_" 
2019-10-11 11:41:30 ::         set mode lacp-active 
2019-10-11 11:41:30 ::         set auto-isl 1 
2019-10-11 11:41:30 ::         set mclag enable 
2019-10-11 11:41:30 ::             set members "port1" "port2" "port3" "port4" 
2019-10-11 11:41:30 ::     next 
2019-10-11 11:41:30 :: end 
2019-10-11 11:41:30 ::  
2019-10-11 11:41:30 :: S548DF4K16000653 # 
2019-10-11 11:41:32 :: diagnose switch mclag peer-consistency-check 
2019-10-11 11:41:32 ::  
2019-10-11 11:41:32 ::     Running diagnostic, it may take sometime... 
2019-10-11 11:41:32 ::  
2019-10-11 11:41:32 ::     mclag-trunk-name    peer-config lacp-state   stp-state   local-ports            remote-ports 
2019-10-11 11:41:32 ::     __________________  ___________ __________   _________   _____________          _____________ 
2019-10-11 11:41:32 ::  
2019-10-11 11:41:32 ::     8DN4K17000133-0*    OK         UP           OK           port47    port48        port47    port48 
2019-10-11 11:41:32 ::     _FlInK1_MLAG0_      OK         UP           OK           port1     port2         port1     port2 
2019-10-11 11:41:32 ::                                                              port3     port4         port3     port4 
2019-10-11 11:41:32 ::  
2019-10-11 11:41:32 ::     trunk1              OK         UP           OK           port13                  port13 
2019-10-11 11:41:32 ::  
2019-10-11 11:41:32 :: S548DF4K16000653 # 
2019-10-11 11:41:34 :: get switch lldp neighbors-summary 
2019-10-11 11:41:34 ::  
2019-10-11 11:41:34 :: Capability codes: 
2019-10-11 11:41:34 :: 	R:Router, B:Bridge, T:Telephone, C:DOCSIS Cable Device 
2019-10-11 11:41:34 :: 	W:WLAN Access Point, P:Repeater, S:Station, O:Other 
2019-10-11 11:41:34 :: MED type codes: 
2019-10-11 11:41:34 :: 	Generic:Generic Endpoint (Class 1), Media:Media Endpoint (Class 2) 
2019-10-11 11:41:34 :: 	Comms:Communications Endpoint (Class 3), Network:Network Connectivity Device 
2019-10-11 11:41:34 ::  
2019-10-11 11:41:34 ::   Portname    Status   Device-name                 TTL   Capability  MED-type  Port-ID 
2019-10-11 11:41:34 ::   __________  _______  __________________________  ____  __________  ________  _______ 
2019-10-11 11:41:34 ::   port1       Up       S548DF4K17000014            120   BR          -         port1 
2019-10-11 11:41:34 ::   port2       Up       S548DF4K17000014            120   BR          -         port2 
2019-10-11 11:41:34 ::   port3       Up       S548DF4K17000028            120   BR          -         port3 
2019-10-11 11:41:34 ::   port4       Up       S548DF4K17000028            120   BR          -         port4 
2019-10-11 11:41:34 ::   port5       Down     -                           -     -           -         - 
2019-10-11 11:41:34 ::   port6       Down     -                           -     -           -         - 
2019-10-11 11:41:34 ::   port7       Down     -                           -     -           -         - 
2019-10-11 11:41:34 ::   port8       Down     -                           -     -           -         - 
2019-10-11 11:41:34 ::   port9       Down     -                           -     -           -         - 
2019-10-11 11:41:34 ::   port10      Down     -                           -     -           -         - 
2019-10-11 11:41:34 ::   port11      Down     -                           -     -           -         - 
2019-10-11 11:41:34 ::   port12      Down     -                           -     -           -         - 
2019-10-11 11:41:34 ::   port13      Up       SW2                         120   BR          Network   port13 
2019-10-11 11:41:34 ::   port14      Down     -                           -     -           -         - 
2019-10-11 11:41:34 ::   port15      Down     -                           -     -           -         - 
2019-10-11 11:41:34 ::   port16      Down     -                           -     -           -         - 
2019-10-11 11:41:34 ::   port17      Down     -                           -     -           -         - 
2019-10-11 11:41:34 ::   port18      Down     -                           -     -           -         - 
2019-10-11 11:41:34 ::   port19      Down     -                           -     -           -         - 
2019-10-11 11:41:34 ::   port20      Down     -                           -     -           -         - 
2019-10-11 11:41:34 ::   port21      Down     -                           -     -           -         - 
2019-10-11 11:41:34 ::   port22      Down     -                           -     -           -         - 
2019-10-11 11:41:34 ::   port23      Down     -                           -     -           -         - 
2019-10-11 11:41:34 ::   port24      Down     -                           -     -           -         - 
2019-10-11 11:41:34 ::   port25      Down     -                           -     -           -         - 
2019-10-11 11:41:34 ::   port26      Down     -                           -     -           -         - 
2019-10-11 11:41:34 ::   port27      Down     -                           -     -           -         - 
2019-10-11 11:41:34 ::   port28      Down     -                           -     -           -         - 
2019-10-11 11:41:34 ::   port29      Down     -                           -     -           -         - 
2019-10-11 11:41:34 ::   port30      Down     -                           -     -           -         - 
2019-10-11 11:41:34 ::   port31      Down     -                           -     -           -         - 
2019-10-11 11:41:34 ::   port32      Down     -                           -     -           -         - 
2019-10-11 11:41:34 ::   port33      Down     -                           -     -           -         - 
2019-10-11 11:41:34 ::   port34      Down     -                           -     -           -         - 
2019-10-11 11:41:34 ::   port35      Down     -                           -     -           -         - 
2019-10-11 11:41:34 ::   port36      Down     -                           -     -           -         - 
2019-10-11 11:41:34 ::   port37      Down     -                           -     -           -         - 
2019-10-11 11:41:34 ::   port38      Down     -                           -     -           -         - 
2019-10-11 11:41:34 ::   port39      Up       -                           -     -           -         - 
2019-10-11 11:41:34 ::   port40      Down     -                           -     -           -         - 
2019-10-11 11:41:34 ::   port41      Down     -                           -     -           -         - 
2019-10-11 11:41:34 ::   port42      Down     -                           -     -           -         - 
2019-10-11 11:41:34 ::   port43      Down     -                           -     -           -         - 
2019-10-11 11:41:34 ::   port44      Down     -                           -     -           -         - 
2019-10-11 11:41:34 ::   port45      Down     -                           -     -           -         - 
2019-10-11 11:41:34 ::   port46      Down     -                           -     -           -         - 
2019-10-11 11:41:34 ::   port47      Up       S548DN4K17000133            120   BR          -         port47 
2019-10-11 11:41:34 ::   port48      Up       S548DN4K17000133            120   BR          -         port48 
2019-10-11 11:41:34 ::   port49      Down     -                           -     -           -         - 
2019-10-11 11:41:34 ::   port50      Down     -                           -     -           -         - 
2019-10-11 11:41:34 ::   port51      Down     -                           -     -           -         - 
2019-10-11 11:41:34 ::   port52      Down     -                           -     -           -         - 
2019-10-11 11:41:34 ::   port53      Down     -                           -     -           -         - 
2019-10-11 11:41:34 ::   port54      Down     -                           -     -           -         - 
2019-10-11 11:41:34 ::  
2019-10-11 11:41:34 :: S548DF4K16000653 # 
2019-10-11 11:41:36 :: show switch interface port39 
2019-10-11 11:41:36 :: config switch interface 
2019-10-11 11:41:36 ::     edit "port39" 
2019-10-11 11:41:36 ::         set allowed-vlans 4093 
2019-10-11 11:41:36 ::         set untagged-vlans 4093 
2019-10-11 11:41:36 ::         set snmp-index 39 
2019-10-11 11:41:36 ::     next 
2019-10-11 11:41:36 :: end 
2019-10-11 11:41:36 ::  
2019-10-11 11:41:36 :: S548DF4K16000653 # 
########################################################################################
2019-10-11 11:41:38 ::  
2019-10-11 11:41:38 :: S548DN4K17000133 (internal) #     end 
2019-10-11 11:41:38 ::  
2019-10-11 11:41:38 :: S548DN4K17000133 #  
2019-10-11 11:41:38 :: S548DN4K17000133 #      
2019-10-11 11:41:38 :: S548DN4K17000133 #  
2019-10-11 11:41:38 :: S548DN4K17000133 # config router static 
2019-10-11 11:41:38 ::  
2019-10-11 11:41:38 :: S548DN4K17000133 (static) #  
2019-10-11 11:41:38 :: S548DN4K17000133 (static) #     edit 1 
2019-10-11 11:41:38 :: new entry '1' added 
2019-10-11 11:41:38 ::  
2019-10-11 11:41:38 :: S548DN4K17000133 (1) #  
2019-10-11 11:41:38 :: S548DN4K17000133 (1) #         set device "mgmt" 
2019-10-11 11:41:38 ::  
2019-10-11 11:41:38 :: S548DN4K17000133 (1) #  
2019-10-11 11:41:38 :: S548DN4K17000133 (1) #         set dst 0.0.0.0 0.0.0.0 
2019-10-11 11:41:38 ::  
2019-10-11 11:41:38 :: S548DN4K17000133 (1) #  
2019-10-11 11:41:38 :: S548DN4K17000133 (1) #         set gateway 10.105.50.254 
2019-10-11 11:41:38 ::  
2019-10-11 11:41:38 :: S548DN4K17000133 (1) #  
2019-10-11 11:41:38 :: S548DN4K17000133 (1) #     next 
2019-10-11 11:41:38 ::  
2019-10-11 11:41:38 :: S548DN4K17000133 (static) #  
2019-10-11 11:41:38 :: S548DN4K17000133 (static) # end 
2019-10-11 11:41:38 ::  
2019-10-11 11:41:38 :: S548DN4K17000133 #  
2019-10-11 11:41:38 :: S548DN4K17000133 #  
2019-10-11 11:41:38 :: S548DN4K17000133 #  
2019-10-11 11:41:38 :: S548DN4K17000133 # config system global 
2019-10-11 11:41:38 ::  
2019-10-11 11:41:38 :: S548DN4K17000133 (global) #  
2019-10-11 11:41:38 :: S548DN4K17000133 (global) #      set admintimeout 480 
2019-10-11 11:41:38 ::  
2019-10-11 11:41:38 :: S548DN4K17000133 (global) #  
2019-10-11 11:41:38 :: S548DN4K17000133 (global) # end 
2019-10-11 11:41:38 ::  
2019-10-11 11:41:38 :: S548DN4K17000133 # get system status 
2019-10-11 11:41:38 :: Version: FortiSwitch-548D v6.2.0,build0192,191005 (Interim) 
2019-10-11 11:41:38 :: Serial-Number: S548DN4K17000133 
2019-10-11 11:41:38 :: BIOS version: 04000013 
2019-10-11 11:41:38 :: System Part-Number: P18057-06 
2019-10-11 11:41:38 :: Burn in MAC: 70:4c:a5:79:22:5a 
2019-10-11 11:41:38 :: Hostname: S548DN4K17000133 
2019-10-11 11:41:38 :: Distribution: International 
2019-10-11 11:41:38 :: Branch point: 192 
2019-10-11 11:41:38 :: System time: Fri Oct 11 11:41:36 2019 
2019-10-11 11:41:38 ::  
2019-10-11 11:41:38 :: S548DN4K17000133 # 
2019-10-11 11:41:40 :: show switch trunk 
2019-10-11 11:41:40 :: config switch trunk 
2019-10-11 11:41:40 ::     edit "8DF4K16000653-0" 
2019-10-11 11:41:40 ::         set mode lacp-active 
2019-10-11 11:41:40 ::         set auto-isl 1 
2019-10-11 11:41:40 ::         set mclag-icl enable 
2019-10-11 11:41:40 ::             set members "port47" "port48" 
2019-10-11 11:41:40 ::     next 
2019-10-11 11:41:40 ::     edit "trunk1" 
2019-10-11 11:41:40 ::         set mode lacp-active 
2019-10-11 11:41:40 ::         set mclag enable 
2019-10-11 11:41:40 ::             set members "port13" 
2019-10-11 11:41:40 ::     next 
2019-10-11 11:41:40 ::     edit "_FlInK1_MLAG0_" 
2019-10-11 11:41:40 ::         set mode lacp-active 
2019-10-11 11:41:40 ::         set auto-isl 1 
2019-10-11 11:41:40 ::         set mclag enable 
2019-10-11 11:41:40 ::             set members "port1" "port2" "port3" "port4" 
2019-10-11 11:41:40 ::     next 
2019-10-11 11:41:40 :: end 
2019-10-11 11:41:40 ::  
2019-10-11 11:41:40 :: S548DN4K17000133 # 
2019-10-11 11:41:42 :: diagnose switch mclag peer-consistency-check 
2019-10-11 11:41:42 ::  
2019-10-11 11:41:42 ::     Running diagnostic, it may take sometime... 
2019-10-11 11:41:42 ::  
2019-10-11 11:41:42 ::     mclag-trunk-name    peer-config lacp-state   stp-state   local-ports            remote-ports 
2019-10-11 11:41:42 ::     __________________  ___________ __________   _________   _____________          _____________ 
2019-10-11 11:41:42 ::  
2019-10-11 11:41:42 ::     8DF4K16000653-0*    OK         UP           OK           port47    port48        port47    port48 
2019-10-11 11:41:42 ::     _FlInK1_MLAG0_      OK         UP           OK           port1     port2         port1     port2 
2019-10-11 11:41:42 ::                                                              port3     port4         port3     port4 
2019-10-11 11:41:42 ::  
2019-10-11 11:41:42 ::     trunk1              OK         UP           OK           port13                  port13 
2019-10-11 11:41:42 ::  
2019-10-11 11:41:42 :: S548DN4K17000133 # 
2019-10-11 11:41:44 :: get switch lldp neighbors-summary 
2019-10-11 11:41:44 ::  
2019-10-11 11:41:44 :: Capability codes: 
2019-10-11 11:41:44 :: 	R:Router, B:Bridge, T:Telephone, C:DOCSIS Cable Device 
2019-10-11 11:41:44 :: 	W:WLAN Access Point, P:Repeater, S:Station, O:Other 
2019-10-11 11:41:44 :: MED type codes: 
2019-10-11 11:41:44 :: 	Generic:Generic Endpoint (Class 1), Media:Media Endpoint (Class 2) 
2019-10-11 11:41:44 :: 	Comms:Communications Endpoint (Class 3), Network:Network Connectivity Device 
2019-10-11 11:41:44 ::  
2019-10-11 11:41:44 ::   Portname    Status   Device-name                 TTL   Capability  MED-type  Port-ID 
2019-10-11 11:41:44 ::   __________  _______  __________________________  ____  __________  ________  _______ 
2019-10-11 11:41:44 ::   port1       Up       S548DF4K17000028            120   BR          -         port1 
2019-10-11 11:41:44 ::   port2       Up       S548DF4K17000028            120   BR          -         port2 
2019-10-11 11:41:44 ::   port3       Up       S548DF4K17000014            120   BR          -         port3 
2019-10-11 11:41:44 ::   port4       Up       S548DF4K17000014            120   BR          -         port4 
2019-10-11 11:41:44 ::   port5       Down     -                           -     -           -         - 
2019-10-11 11:41:44 ::   port6       Down     -                           -     -           -         - 
2019-10-11 11:41:44 ::   port7       Down     -                           -     -           -         - 
2019-10-11 11:41:44 ::   port8       Down     -                           -     -           -         - 
2019-10-11 11:41:44 ::   port9       Down     -                           -     -           -         - 
2019-10-11 11:41:44 ::   port10      Down     -                           -     -           -         - 
2019-10-11 11:41:44 ::   port11      Down     -                           -     -           -         - 
2019-10-11 11:41:44 ::   port12      Down     -                           -     -           -         - 
2019-10-11 11:41:44 ::   port13      Up       SW2                         120   BR          Network   port14 
2019-10-11 11:41:44 ::   port14      Down     -                           -     -           -         - 
2019-10-11 11:41:44 ::   port15      Down     -                           -     -           -         - 
2019-10-11 11:41:44 ::   port16      Down     -                           -     -           -         - 
2019-10-11 11:41:44 ::   port17      Down     -                           -     -           -         - 
2019-10-11 11:41:44 ::   port18      Down     -                           -     -           -         - 
2019-10-11 11:41:44 ::   port19      Down     -                           -     -           -         - 
2019-10-11 11:41:44 ::   port20      Down     -                           -     -           -         - 
2019-10-11 11:41:44 ::   port21      Down     -                           -     -           -         - 
2019-10-11 11:41:44 ::   port22      Down     -                           -     -           -         - 
2019-10-11 11:41:44 ::   port23      Down     -                           -     -           -         - 
2019-10-11 11:41:44 ::   port24      Down     -                           -     -           -         - 
2019-10-11 11:41:44 ::   port25      Down     -                           -     -           -         - 
2019-10-11 11:41:44 ::   port26      Down     -                           -     -           -         - 
2019-10-11 11:41:44 ::   port27      Down     -                           -     -           -         - 
2019-10-11 11:41:44 ::   port28      Down     -                           -     -           -         - 
2019-10-11 11:41:44 ::   port29      Down     -                           -     -           -         - 
2019-10-11 11:41:44 ::   port30      Down     -                           -     -           -         - 
2019-10-11 11:41:44 ::   port31      Down     -                           -     -           -         - 
2019-10-11 11:41:44 ::   port32      Down     -                           -     -           -         - 
2019-10-11 11:41:44 ::   port33      Down     -                           -     -           -         - 
2019-10-11 11:41:44 ::   port34      Down     -                           -     -           -         - 
2019-10-11 11:41:44 ::   port35      Down     -                           -     -           -         - 
2019-10-11 11:41:44 ::   port36      Down     -                           -     -           -         - 
2019-10-11 11:41:44 ::   port37      Down     -                           -     -           -         - 
2019-10-11 11:41:44 ::   port38      Down     -                           -     -           -         - 
2019-10-11 11:41:44 ::   port39      Up       -                           -     -           -         - 
2019-10-11 11:41:44 ::   port40      Down     -                           -     -           -         - 
2019-10-11 11:41:44 ::   port41      Down     -                           -     -           -         - 
2019-10-11 11:41:44 ::   port42      Down     -                           -     -           -         - 
2019-10-11 11:41:44 ::   port43      Down     -                           -     -           -         - 
2019-10-11 11:41:44 ::   port44      Down     -                           -     -           -         - 
2019-10-11 11:41:44 ::   port45      Down     -                           -     -           -         - 
2019-10-11 11:41:44 ::   port46      Down     -                           -     -           -         - 
2019-10-11 11:41:44 ::   port47      Up       S548DF4K16000653            120   BR          -         port47 
2019-10-11 11:41:44 ::   port48      Up       S548DF4K16000653            120   BR          -         port48 
2019-10-11 11:41:44 ::   port49      Down     -                           -     -           -         - 
2019-10-11 11:41:44 ::   port50      Down     -                           -     -           -         - 
2019-10-11 11:41:44 ::   port51      Down     -                           -     -           -         - 
2019-10-11 11:41:44 ::   port52      Down     -                           -     -           -         - 
2019-10-11 11:41:44 ::   port53      Down     -                           -     -           -         - 
2019-10-11 11:41:44 ::   port54      Down     -                           -     -           -         - 
2019-10-11 11:41:44 ::  
2019-10-11 11:41:44 :: S548DN4K17000133 # 
2019-10-11 11:41:46 :: show switch interface port39 
2019-10-11 11:41:46 :: config switch interface 
2019-10-11 11:41:46 ::     edit "port39" 
2019-10-11 11:41:46 ::         set allowed-vlans 4093 
2019-10-11 11:41:46 ::         set untagged-vlans 4093 
2019-10-11 11:41:46 ::         set snmp-index 39 
2019-10-11 11:41:46 ::     next 
2019-10-11 11:41:46 :: end 
2019-10-11 11:41:46 ::  
2019-10-11 11:41:46 :: S548DN4K17000133 # 
2019-10-11 11:41:48 :: configuring: config switch interface 
2019-10-11 11:41:48 :: configuring: edit 704CA5CBC3DC-0 
2019-10-11 11:41:49 :: configuring: set log-mac-event enable 
2019-10-11 11:41:49 :: configuring: end 
2019-10-11 11:41:50 :: configuring: config switch interface 
2019-10-11 11:41:50 :: configuring: edit 8DF4K17000028-0 
2019-10-11 11:41:51 :: configuring: set log-mac-event enable 
2019-10-11 11:41:51 :: configuring: end 
2019-10-11 11:41:52 :: configuring: config switch interface 
2019-10-11 11:41:52 :: configuring: edit 704CA5A8FCFA-0 
2019-10-11 11:41:53 :: configuring: set log-mac-event enable 
2019-10-11 11:41:53 :: configuring: end 
2019-10-11 11:41:54 :: configuring: config switch interface 
2019-10-11 11:41:54 :: configuring: edit sw1-trunk 
2019-10-11 11:41:55 :: configuring: set log-mac-event enable 
2019-10-11 11:41:55 :: configuring: end 
2019-10-11 11:41:56 :: configuring: config switch interface 
2019-10-11 11:41:56 :: configuring: edit core1 
2019-10-11 11:41:57 :: configuring: set log-mac-event enable 
2019-10-11 11:41:57 :: configuring: end 
2019-10-11 11:42:00 :: configuring: config switch interface 
2019-10-11 11:42:00 :: configuring: edit 8DF4K17000014-0 
2019-10-11 11:42:01 :: configuring: set log-mac-event enable 
2019-10-11 11:42:01 :: configuring: end 
2019-10-11 11:42:02 :: configuring: config switch interface 
2019-10-11 11:42:02 :: configuring: edit 704CA5A8FCFA-0 
2019-10-11 11:42:03 :: configuring: set log-mac-event enable 
2019-10-11 11:42:03 :: configuring: end 
2019-10-11 11:42:04 :: configuring: config switch interface 
2019-10-11 11:42:04 :: configuring: edit 704CA5CBC3DC-0 
2019-10-11 11:42:05 :: configuring: set log-mac-event enable 
2019-10-11 11:42:05 :: configuring: end 
2019-10-11 11:42:06 :: configuring: config switch interface 
2019-10-11 11:42:06 :: configuring: edit sw1-trunk 
2019-10-11 11:42:07 :: configuring: set log-mac-event enable 
2019-10-11 11:42:07 :: configuring: end 
2019-10-11 11:42:08 :: configuring: config switch interface 
2019-10-11 11:42:08 :: configuring: edit _FlInK1_MLAG0_ 
2019-10-11 11:42:09 :: configuring: set log-mac-event enable 
2019-10-11 11:42:09 :: configuring: end 
2019-10-11 11:42:12 :: configuring: config switch interface 
2019-10-11 11:42:12 :: configuring: edit port39 
2019-10-11 11:42:13 :: configuring: set log-mac-event enable 
2019-10-11 11:42:13 :: configuring: end 
2019-10-11 11:42:14 :: configuring: config switch interface 
2019-10-11 11:42:14 :: configuring: edit 8DN4K17000133-0 
2019-10-11 11:42:15 :: configuring: set log-mac-event enable 
2019-10-11 11:42:15 :: configuring: end 
2019-10-11 11:42:16 :: configuring: config switch interface 
2019-10-11 11:42:16 :: configuring: edit trunk1 
2019-10-11 11:42:17 :: configuring: set log-mac-event enable 
2019-10-11 11:42:17 :: configuring: end 
2019-10-11 11:42:18 :: configuring: config switch interface 
2019-10-11 11:42:18 :: configuring: edit _FlInK1_MLAG0_ 
2019-10-11 11:42:19 :: configuring: set log-mac-event enable 
2019-10-11 11:42:19 :: configuring: end 
2019-10-11 11:42:22 :: configuring: config switch interface 
2019-10-11 11:42:22 :: configuring: edit port39 
2019-10-11 11:42:23 :: configuring: set log-mac-event enable 
2019-10-11 11:42:23 :: configuring: end 
2019-10-11 11:42:24 :: configuring: config switch interface 
2019-10-11 11:42:24 :: configuring: edit 8DF4K16000653-0 
2019-10-11 11:42:25 :: configuring: set log-mac-event enable 
2019-10-11 11:42:26 :: configuring: end 
2019-10-11 11:42:26 :: configuring: config switch interface 
2019-10-11 11:42:27 :: configuring: edit trunk1 
2019-10-11 11:42:27 :: configuring: set log-mac-event enable 
2019-10-11 11:42:28 :: configuring: end 
2019-10-11 11:42:28 :: configuring: config switch interface 
2019-10-11 11:42:29 :: configuring: edit _FlInK1_MLAG0_ 
2019-10-11 11:42:29 :: configuring: set log-mac-event enable 
2019-10-11 11:42:30 :: configuring: end 
2019-10-11 11:42:30 :: Test Case #3: Start executing test case and generating activites 
########################################################################################
2019-10-11 11:42:32 :: get system status 
2019-10-11 11:42:32 :: Version: FortiSwitch-548D-FPOE v6.2.0,build0192,191005 (Interim) 
2019-10-11 11:42:32 :: Serial-Number: S548DF4K17000014 
2019-10-11 11:42:32 :: BIOS version: 04000016 
2019-10-11 11:42:32 :: System Part-Number: P18049-05 
2019-10-11 11:42:32 :: Burn in MAC: 70:4c:a5:82:96:72 
2019-10-11 11:42:32 :: Hostname: S548DF4K17000014 
2019-10-11 11:42:32 :: Distribution: International 
2019-10-11 11:42:32 :: Branch point: 192 
2019-10-11 11:42:32 :: System time: Fri Oct 11 11:42:31 2019 
2019-10-11 11:42:32 ::  
2019-10-11 11:42:32 :: S548DF4K17000014 # 
2019-10-11 11:42:36 :: show switch trunk 
2019-10-11 11:42:36 :: config switch trunk 
2019-10-11 11:42:36 ::     edit "704CA5CBC3DC-0" 
2019-10-11 11:42:36 ::         set mode lacp-active 
2019-10-11 11:42:36 ::         set auto-isl 1 
2019-10-11 11:42:36 ::         set isl-fortilink 1 
2019-10-11 11:42:36 ::         set mclag enable 
2019-10-11 11:42:36 ::             set members "port50" 
2019-10-11 11:42:36 ::     next 
2019-10-11 11:42:36 ::     edit "8DF4K17000028-0" 
2019-10-11 11:42:36 ::         set mode lacp-active 
2019-10-11 11:42:36 ::         set auto-isl 1 
2019-10-11 11:42:36 ::         set mclag-icl enable 
2019-10-11 11:42:36 ::             set members "port47" "port48" 
2019-10-11 11:42:36 ::     next 
2019-10-11 11:42:36 ::     edit "704CA5A8FCFA-0" 
2019-10-11 11:42:36 ::         set mode lacp-active 
2019-10-11 11:42:36 ::         set auto-isl 1 
2019-10-11 11:42:36 ::         set isl-fortilink 1 
2019-10-11 11:42:36 ::         set mclag enable 
2019-10-11 11:42:36 ::             set members "port49" 
2019-10-11 11:42:36 ::     next 
2019-10-11 11:42:36 ::     edit "sw1-trunk" 
2019-10-11 11:42:36 ::         set mode lacp-active 
2019-10-11 11:42:36 ::         set mclag enable 
2019-10-11 11:42:36 :: --More--                      set members "port13" 
2019-10-11 11:42:36 ::     next 
2019-10-11 11:42:36 ::     edit "core1" 
2019-10-11 11:42:36 ::         set mode lacp-active 
2019-10-11 11:42:36 ::         set auto-isl 1 
2019-10-11 11:42:36 ::         set mclag enable 
2019-10-11 11:42:36 ::             set members "port1" "port2" "port3" "port4" 
2019-10-11 11:42:36 ::     next 
2019-10-11 11:42:36 :: end 
2019-10-11 11:42:36 ::  
2019-10-11 11:42:36 :: S548DF4K17000014 # 
2019-10-11 11:42:40 :: diagnose switch mclag peer-consistency-check 
2019-10-11 11:42:40 ::  
2019-10-11 11:42:40 ::     Running diagnostic, it may take sometime... 
2019-10-11 11:42:40 ::  
2019-10-11 11:42:40 ::     mclag-trunk-name    peer-config lacp-state   stp-state   local-ports            remote-ports 
2019-10-11 11:42:40 ::     __________________  ___________ __________   _________   _____________          _____________ 
2019-10-11 11:42:40 ::  
2019-10-11 11:42:40 ::     8DF4K17000028-0*    OK         UP           OK           port47    port48        port47    port48 
2019-10-11 11:42:40 ::     704CA5A8FCFA-0      OK         UP           OK           port49                  port49 
2019-10-11 11:42:40 ::     704CA5CBC3DC-0      OK         UP           OK           port50                  port50 
2019-10-11 11:42:40 ::     core1               NOT-FOUND  UP           OK           port1     port2 
2019-10-11 11:42:40 ::                                                              port3     port4 
2019-10-11 11:42:40 ::  
2019-10-11 11:42:40 ::     sw1-trunk           OK         UP           OK           port13                  port13 
2019-10-11 11:42:40 ::  
2019-10-11 11:42:40 :: S548DF4K17000014 # 
2019-10-11 11:42:44 :: get switch lldp neighbors-summary 
2019-10-11 11:42:44 ::  
2019-10-11 11:42:44 :: Capability codes: 
2019-10-11 11:42:44 :: 	R:Router, B:Bridge, T:Telephone, C:DOCSIS Cable Device 
2019-10-11 11:42:44 :: 	W:WLAN Access Point, P:Repeater, S:Station, O:Other 
2019-10-11 11:42:44 :: MED type codes: 
2019-10-11 11:42:44 :: 	Generic:Generic Endpoint (Class 1), Media:Media Endpoint (Class 2) 
2019-10-11 11:42:44 :: 	Comms:Communications Endpoint (Class 3), Network:Network Connectivity Device 
2019-10-11 11:42:44 ::  
2019-10-11 11:42:44 ::   Portname    Status   Device-name                 TTL   Capability  MED-type  Port-ID 
2019-10-11 11:42:44 ::   __________  _______  __________________________  ____  __________  ________  _______ 
2019-10-11 11:42:44 ::   port1       Up       S548DF4K16000653            120   BR          -         port1 
2019-10-11 11:42:44 ::   port2       Up       S548DF4K16000653            120   BR          -         port2 
2019-10-11 11:42:44 ::   port3       Up       S548DN4K17000133            120   BR          -         port3 
2019-10-11 11:42:44 ::   port4       Up       S548DN4K17000133            120   BR          -         port4 
2019-10-11 11:42:44 ::   port5       Down     -                           -     -           -         - 
2019-10-11 11:42:44 ::   port6       Down     -                           -     -           -         - 
2019-10-11 11:42:44 ::   port7       Down     -                           -     -           -         - 
2019-10-11 11:42:44 ::   port8       Down     -                           -     -           -         - 
2019-10-11 11:42:44 ::   port9       Down     -                           -     -           -         - 
2019-10-11 11:42:44 ::   port10      Down     -                           -     -           -         - 
2019-10-11 11:42:44 ::   port11      Down     -                           -     -           -         - 
2019-10-11 11:42:44 ::   port12      Down     -                           -     -           -         - 
2019-10-11 11:42:44 ::   port13      Down     -                           -     -           -         - 
2019-10-11 11:42:44 ::   port14      Down     -                           -     -           -         - 
2019-10-11 11:42:44 ::   port15      Down     -                           -     -           -         - 
2019-10-11 11:42:44 ::   port16      Down     -                           -     -           -         - 
2019-10-11 11:42:44 ::   port17      Down     -                           -     -           -         - 
2019-10-11 11:42:44 ::   port18      Down     -                           -     -           -         - 
2019-10-11 11:42:44 ::   port19      Down     -                           -     -           -         - 
2019-10-11 11:42:44 ::   port20      Down     -                           -     -           -         - 
2019-10-11 11:42:44 ::   port21      Down     -                           -     -           -         - 
2019-10-11 11:42:44 ::   port22      Down     -                           -     -           -         - 
2019-10-11 11:42:44 ::   port23      Down     -                           -     -           -         - 
2019-10-11 11:42:44 ::   port24      Down     -                           -     -           -         - 
2019-10-11 11:42:44 ::   port25      Down     -                           -     -           -         - 
2019-10-11 11:42:44 ::   port26      Down     -                           -     -           -         - 
2019-10-11 11:42:44 ::   port27      Down     -                           -     -           -         - 
2019-10-11 11:42:44 ::   port28      Down     -                           -     -           -         - 
2019-10-11 11:42:44 ::   port29      Down     -                           -     -           -         - 
2019-10-11 11:42:44 ::   port30      Down     -                           -     -           -         - 
2019-10-11 11:42:44 ::   port31      Down     -                           -     -           -         - 
2019-10-11 11:42:44 ::   port32      Down     -                           -     -           -         - 
2019-10-11 11:42:44 ::   port33      Down     -                           -     -           -         - 
2019-10-11 11:42:44 ::   port34      Down     -                           -     -           -         - 
2019-10-11 11:42:44 ::   port35      Down     -                           -     -           -         - 
2019-10-11 11:42:44 ::   port36      Down     -                           -     -           -         - 
2019-10-11 11:42:44 ::   port37      Down     -                           -     -           -         - 
2019-10-11 11:42:44 ::   port38      Down     -                           -     -           -         - 
2019-10-11 11:42:44 ::   port39      Down     -                           -     -           -         - 
2019-10-11 11:42:44 ::   port40      Down     -                           -     -           -         - 
2019-10-11 11:42:44 ::   port41      Down     -                           -     -           -         - 
2019-10-11 11:42:44 ::   port42      Down     -                           -     -           -         - 
2019-10-11 11:42:44 ::   port43      Down     -                           -     -           -         - 
2019-10-11 11:42:44 ::   port44      Down     -                           -     -           -         - 
2019-10-11 11:42:44 ::   port45      Down     -                           -     -           -         - 
2019-10-11 11:42:44 ::   port46      Down     -                           -     -           -         - 
2019-10-11 11:42:44 ::   port47      Up       S548DF4K17000028            120   BR          -         port47 
2019-10-11 11:42:44 ::   port48      Up       S548DF4K17000028            120   BR          -         port48 
2019-10-11 11:42:44 ::   port49      Up       FortiGate-3960E             120   BR          -         70:4c:a5:a8:fc:c6 
2019-10-11 11:42:44 ::   port50      Up       FortiGate-3960E             120   BR          -         70:4c:a5:cb:c3:a8 
2019-10-11 11:42:44 ::   port51      Down     -                           -     -           -         - 
2019-10-11 11:42:44 ::   port52      Down     -                           -     -           -         - 
2019-10-11 11:42:44 ::   port53      Down     -                           -     -           -         - 
2019-10-11 11:42:44 ::   port54      Down     -                           -     -           -         - 
2019-10-11 11:42:44 ::  
2019-10-11 11:42:44 :: S548DF4K17000014 # 
2019-10-11 11:42:48 :: show switch interface port39 
2019-10-11 11:42:48 :: config switch interface 
2019-10-11 11:42:48 ::     edit "port39" 
2019-10-11 11:42:48 ::         set allowed-vlans 4093 
2019-10-11 11:42:48 ::         set untagged-vlans 4093 
2019-10-11 11:42:48 ::         set snmp-index 39 
2019-10-11 11:42:48 ::     next 
2019-10-11 11:42:48 :: end 
2019-10-11 11:42:48 ::  
2019-10-11 11:42:48 :: S548DF4K17000014 # 
########################################################################################
2019-10-11 11:42:52 :: get system status 
2019-10-11 11:42:52 :: Version: FortiSwitch-548D-FPOE v6.2.0,build0192,191005 (Interim) 
2019-10-11 11:42:52 :: Serial-Number: S548DF4K17000028 
2019-10-11 11:42:52 :: BIOS version: 04000016 
2019-10-11 11:42:52 :: System Part-Number: P18049-05 
2019-10-11 11:42:52 :: Burn in MAC: 70:4c:a5:82:99:82 
2019-10-11 11:42:52 :: Hostname: S548DF4K17000028 
2019-10-11 11:42:52 :: Distribution: International 
2019-10-11 11:42:52 :: Branch point: 192 
2019-10-11 11:42:52 :: System time: Fri Oct 11 11:42:51 2019 
2019-10-11 11:42:52 ::  
2019-10-11 11:42:52 :: S548DF4K17000028 # 
2019-10-11 11:42:56 :: show switch trunk 
2019-10-11 11:42:56 :: config switch trunk 
2019-10-11 11:42:56 ::     edit "8DF4K17000014-0" 
2019-10-11 11:42:56 ::         set mode lacp-active 
2019-10-11 11:42:56 ::         set auto-isl 1 
2019-10-11 11:42:56 ::         set mclag-icl enable 
2019-10-11 11:42:56 ::             set members "port47" "port48" 
2019-10-11 11:42:56 ::     next 
2019-10-11 11:42:56 ::     edit "704CA5A8FCFA-0" 
2019-10-11 11:42:56 ::         set mode lacp-active 
2019-10-11 11:42:56 ::         set auto-isl 1 
2019-10-11 11:42:56 ::         set isl-fortilink 1 
2019-10-11 11:42:56 ::         set mclag enable 
2019-10-11 11:42:56 ::             set members "port49" 
2019-10-11 11:42:56 ::     next 
2019-10-11 11:42:56 ::     edit "704CA5CBC3DC-0" 
2019-10-11 11:42:56 ::         set mode lacp-active 
2019-10-11 11:42:56 ::         set auto-isl 1 
2019-10-11 11:42:56 ::         set isl-fortilink 1 
2019-10-11 11:42:56 ::         set mclag enable 
2019-10-11 11:42:56 ::             set members "port50" 
2019-10-11 11:42:56 ::     next 
2019-10-11 11:42:56 ::     edit "sw1-trunk" 
2019-10-11 11:42:56 ::         set mode lacp-active 
2019-10-11 11:42:56 ::         set mclag enable 
2019-10-11 11:42:56 :: --More--                      set members "port13" 
2019-10-11 11:42:56 ::     next 
2019-10-11 11:42:56 ::     edit "_FlInK1_MLAG0_" 
2019-10-11 11:42:56 ::         set mode lacp-active 
2019-10-11 11:42:56 ::         set auto-isl 1 
2019-10-11 11:42:56 ::         set mclag enable 
2019-10-11 11:42:56 ::             set members "port3" "port4" "port2" "port1" 
2019-10-11 11:42:56 ::     next 
2019-10-11 11:42:56 :: end 
2019-10-11 11:42:56 ::  
2019-10-11 11:42:56 :: S548DF4K17000028 # 
2019-10-11 11:43:00 :: diagnose switch mclag peer-consistency-check 
2019-10-11 11:43:00 ::  
2019-10-11 11:43:00 ::     Running diagnostic, it may take sometime... 
2019-10-11 11:43:00 ::  
2019-10-11 11:43:00 ::     mclag-trunk-name    peer-config lacp-state   stp-state   local-ports            remote-ports 
2019-10-11 11:43:00 ::     __________________  ___________ __________   _________   _____________          _____________ 
2019-10-11 11:43:00 ::  
2019-10-11 11:43:00 ::     8DF4K17000014-0*    OK         UP           OK           port47    port48        port47    port48 
2019-10-11 11:43:00 ::     704CA5A8FCFA-0      OK         UP           OK           port49                  port49 
2019-10-11 11:43:00 ::     704CA5CBC3DC-0      OK         UP           OK           port50                  port50 
2019-10-11 11:43:00 ::     _FlInK1_MLAG0_      NOT-FOUND  UP           OK           port1     port2 
2019-10-11 11:43:00 ::                                                              port3     port4 
2019-10-11 11:43:00 ::  
2019-10-11 11:43:00 ::     sw1-trunk           OK         UP           OK           port13                  port13 
2019-10-11 11:43:00 ::  
2019-10-11 11:43:00 :: S548DF4K17000028 # 
2019-10-11 11:43:04 :: get switch lldp neighbors-summary 
2019-10-11 11:43:04 ::  
2019-10-11 11:43:04 :: Capability codes: 
2019-10-11 11:43:04 :: 	R:Router, B:Bridge, T:Telephone, C:DOCSIS Cable Device 
2019-10-11 11:43:04 :: 	W:WLAN Access Point, P:Repeater, S:Station, O:Other 
2019-10-11 11:43:04 :: MED type codes: 
2019-10-11 11:43:04 :: 	Generic:Generic Endpoint (Class 1), Media:Media Endpoint (Class 2) 
2019-10-11 11:43:04 :: 	Comms:Communications Endpoint (Class 3), Network:Network Connectivity Device 
2019-10-11 11:43:04 ::  
2019-10-11 11:43:04 ::   Portname    Status   Device-name                 TTL   Capability  MED-type  Port-ID 
2019-10-11 11:43:04 ::   __________  _______  __________________________  ____  __________  ________  _______ 
2019-10-11 11:43:04 ::   port1       Up       S548DN4K17000133            120   BR          -         port1 
2019-10-11 11:43:04 ::   port2       Up       S548DN4K17000133            120   BR          -         port2 
2019-10-11 11:43:04 ::   port3       Up       S548DF4K16000653            120   BR          -         port3 
2019-10-11 11:43:04 ::   port4       Up       S548DF4K16000653            120   BR          -         port4 
2019-10-11 11:43:04 ::   port5       Down     -                           -     -           -         - 
2019-10-11 11:43:04 ::   port6       Down     -                           -     -           -         - 
2019-10-11 11:43:04 ::   port7       Down     -                           -     -           -         - 
2019-10-11 11:43:04 ::   port8       Down     -                           -     -           -         - 
2019-10-11 11:43:04 ::   port9       Down     -                           -     -           -         - 
2019-10-11 11:43:04 ::   port10      Down     -                           -     -           -         - 
2019-10-11 11:43:04 ::   port11      Down     -                           -     -           -         - 
2019-10-11 11:43:04 ::   port12      Down     -                           -     -           -         - 
2019-10-11 11:43:04 ::   port13      Down     -                           -     -           -         - 
2019-10-11 11:43:04 ::   port14      Down     -                           -     -           -         - 
2019-10-11 11:43:04 ::   port15      Down     -                           -     -           -         - 
2019-10-11 11:43:04 ::   port16      Down     -                           -     -           -         - 
2019-10-11 11:43:04 ::   port17      Down     -                           -     -           -         - 
2019-10-11 11:43:04 ::   port18      Down     -                           -     -           -         - 
2019-10-11 11:43:04 ::   port19      Down     -                           -     -           -         - 
2019-10-11 11:43:04 ::   port20      Down     -                           -     -           -         - 
2019-10-11 11:43:04 ::   port21      Down     -                           -     -           -         - 
2019-10-11 11:43:04 ::   port22      Down     -                           -     -           -         - 
2019-10-11 11:43:04 ::   port23      Down     -                           -     -           -         - 
2019-10-11 11:43:04 ::   port24      Down     -                           -     -           -         - 
2019-10-11 11:43:04 ::   port25      Down     -                           -     -           -         - 
2019-10-11 11:43:04 ::   port26      Down     -                           -     -           -         - 
2019-10-11 11:43:04 ::   port27      Down     -                           -     -           -         - 
2019-10-11 11:43:04 ::   port28      Down     -                           -     -           -         - 
2019-10-11 11:43:04 ::   port29      Down     -                           -     -           -         - 
2019-10-11 11:43:04 ::   port30      Down     -                           -     -           -         - 
2019-10-11 11:43:04 ::   port31      Down     -                           -     -           -         - 
2019-10-11 11:43:04 ::   port32      Down     -                           -     -           -         - 
2019-10-11 11:43:04 ::   port33      Down     -                           -     -           -         - 
2019-10-11 11:43:04 ::   port34      Down     -                           -     -           -         - 
2019-10-11 11:43:04 ::   port35      Down     -                           -     -           -         - 
2019-10-11 11:43:04 ::   port36      Down     -                           -     -           -         - 
2019-10-11 11:43:04 ::   port37      Down     -                           -     -           -         - 
2019-10-11 11:43:04 ::   port38      Down     -                           -     -           -         - 
2019-10-11 11:43:04 ::   port39      Down     -                           -     -           -         - 
2019-10-11 11:43:04 ::   port40      Down     -                           -     -           -         - 
2019-10-11 11:43:04 ::   port41      Down     -                           -     -           -         - 
2019-10-11 11:43:04 ::   port42      Down     -                           -     -           -         - 
2019-10-11 11:43:04 ::   port43      Down     -                           -     -           -         - 
2019-10-11 11:43:04 ::   port44      Down     -                           -     -           -         - 
2019-10-11 11:43:04 ::   port45      Down     -                           -     -           -         - 
2019-10-11 11:43:04 ::   port46      Down     -                           -     -           -         - 
2019-10-11 11:43:04 ::   port47      Up       S548DF4K17000014            120   BR          -         port47 
2019-10-11 11:43:04 ::   port48      Up       S548DF4K17000014            120   BR          -         port48 
2019-10-11 11:43:04 ::   port49      Up       FortiGate-3960E             120   BR          -         70:4c:a5:a8:fc:c7 
2019-10-11 11:43:04 ::   port50      Up       FortiGate-3960E             120   BR          -         70:4c:a5:cb:c3:a9 
2019-10-11 11:43:04 ::   port51      Down     -                           -     -           -         - 
2019-10-11 11:43:04 ::   port52      Down     -                           -     -           -         - 
2019-10-11 11:43:04 ::   port53      Down     -                           -     -           -         - 
2019-10-11 11:43:04 ::   port54      Down     -                           -     -           -         - 
2019-10-11 11:43:04 ::  
2019-10-11 11:43:04 :: S548DF4K17000028 # 
2019-10-11 11:43:08 :: show switch interface port39 
2019-10-11 11:43:08 :: config switch interface 
2019-10-11 11:43:08 ::     edit "port39" 
2019-10-11 11:43:08 ::         set allowed-vlans 4093 
2019-10-11 11:43:08 ::         set untagged-vlans 4093 
2019-10-11 11:43:08 ::         set snmp-index 39 
2019-10-11 11:43:08 ::     next 
2019-10-11 11:43:08 :: end 
2019-10-11 11:43:08 ::  
2019-10-11 11:43:08 :: S548DF4K17000028 # 
########################################################################################
2019-10-11 11:43:12 :: get system status 
2019-10-11 11:43:12 :: Version: FortiSwitch-548D-FPOE v6.2.0,build0192,191005 (Interim) 
2019-10-11 11:43:12 :: Serial-Number: S548DF4K16000653 
2019-10-11 11:43:12 :: BIOS version: 04000013 
2019-10-11 11:43:12 :: System Part-Number: P18049-04 
2019-10-11 11:43:12 :: Burn in MAC: 90:6c:ac:62:14:3e 
2019-10-11 11:43:12 :: Hostname: S548DF4K16000653 
2019-10-11 11:43:12 :: Distribution: International 
2019-10-11 11:43:12 :: Branch point: 192 
2019-10-11 11:43:12 :: System time: Fri Oct 11 11:43:11 2019 
2019-10-11 11:43:12 ::  
2019-10-11 11:43:12 :: S548DF4K16000653 # 
2019-10-11 11:43:16 :: show switch trunk 
2019-10-11 11:43:16 :: config switch trunk 
2019-10-11 11:43:16 ::     edit "8DN4K17000133-0" 
2019-10-11 11:43:16 ::         set mode lacp-active 
2019-10-11 11:43:16 ::         set auto-isl 1 
2019-10-11 11:43:16 ::         set mclag-icl enable 
2019-10-11 11:43:16 ::             set members "port47" "port48" 
2019-10-11 11:43:16 ::     next 
2019-10-11 11:43:16 ::     edit "trunk1" 
2019-10-11 11:43:16 ::         set mode lacp-active 
2019-10-11 11:43:16 ::         set mclag enable 
2019-10-11 11:43:16 ::             set members "port13" 
2019-10-11 11:43:16 ::     next 
2019-10-11 11:43:16 ::     edit "_FlInK1_MLAG0_" 
2019-10-11 11:43:16 ::         set mode lacp-active 
2019-10-11 11:43:16 ::         set auto-isl 1 
2019-10-11 11:43:16 ::         set mclag enable 
2019-10-11 11:43:16 ::             set members "port1" "port2" "port3" "port4" 
2019-10-11 11:43:16 ::     next 
2019-10-11 11:43:16 :: end 
2019-10-11 11:43:16 ::  
2019-10-11 11:43:16 :: S548DF4K16000653 # 
2019-10-11 11:43:20 :: diagnose switch mclag peer-consistency-check 
2019-10-11 11:43:20 ::  
2019-10-11 11:43:20 ::     Running diagnostic, it may take sometime... 
2019-10-11 11:43:20 ::  
2019-10-11 11:43:20 ::     mclag-trunk-name    peer-config lacp-state   stp-state   local-ports            remote-ports 
2019-10-11 11:43:20 ::     __________________  ___________ __________   _________   _____________          _____________ 
2019-10-11 11:43:20 ::  
2019-10-11 11:43:20 ::     8DN4K17000133-0*    OK         UP           OK           port47    port48        port47    port48 
2019-10-11 11:43:20 ::     _FlInK1_MLAG0_      OK         UP           OK           port1     port2         port1     port2 
2019-10-11 11:43:20 ::                                                              port3     port4         port3     port4 
2019-10-11 11:43:20 ::  
2019-10-11 11:43:20 ::     trunk1              OK         UP           OK           port13                  port13 
2019-10-11 11:43:20 ::  
2019-10-11 11:43:20 :: S548DF4K16000653 # 
2019-10-11 11:43:24 :: get switch lldp neighbors-summary 
2019-10-11 11:43:24 ::  
2019-10-11 11:43:24 :: Capability codes: 
2019-10-11 11:43:24 :: 	R:Router, B:Bridge, T:Telephone, C:DOCSIS Cable Device 
2019-10-11 11:43:24 :: 	W:WLAN Access Point, P:Repeater, S:Station, O:Other 
2019-10-11 11:43:24 :: MED type codes: 
2019-10-11 11:43:24 :: 	Generic:Generic Endpoint (Class 1), Media:Media Endpoint (Class 2) 
2019-10-11 11:43:24 :: 	Comms:Communications Endpoint (Class 3), Network:Network Connectivity Device 
2019-10-11 11:43:24 ::  
2019-10-11 11:43:24 ::   Portname    Status   Device-name                 TTL   Capability  MED-type  Port-ID 
2019-10-11 11:43:24 ::   __________  _______  __________________________  ____  __________  ________  _______ 
2019-10-11 11:43:24 ::   port1       Up       S548DF4K17000014            120   BR          -         port1 
2019-10-11 11:43:24 ::   port2       Up       S548DF4K17000014            120   BR          -         port2 
2019-10-11 11:43:24 ::   port3       Up       S548DF4K17000028            120   BR          -         port3 
2019-10-11 11:43:24 ::   port4       Up       S548DF4K17000028            120   BR          -         port4 
2019-10-11 11:43:24 ::   port5       Down     -                           -     -           -         - 
2019-10-11 11:43:24 ::   port6       Down     -                           -     -           -         - 
2019-10-11 11:43:24 ::   port7       Down     -                           -     -           -         - 
2019-10-11 11:43:24 ::   port8       Down     -                           -     -           -         - 
2019-10-11 11:43:24 ::   port9       Down     -                           -     -           -         - 
2019-10-11 11:43:24 ::   port10      Down     -                           -     -           -         - 
2019-10-11 11:43:24 ::   port11      Down     -                           -     -           -         - 
2019-10-11 11:43:24 ::   port12      Down     -                           -     -           -         - 
2019-10-11 11:43:24 ::   port13      Up       SW2                         120   BR          Network   port13 
2019-10-11 11:43:24 ::   port14      Down     -                           -     -           -         - 
2019-10-11 11:43:24 ::   port15      Down     -                           -     -           -         - 
2019-10-11 11:43:24 ::   port16      Down     -                           -     -           -         - 
2019-10-11 11:43:24 ::   port17      Down     -                           -     -           -         - 
2019-10-11 11:43:24 ::   port18      Down     -                           -     -           -         - 
2019-10-11 11:43:24 ::   port19      Down     -                           -     -           -         - 
2019-10-11 11:43:24 ::   port20      Down     -                           -     -           -         - 
2019-10-11 11:43:24 ::   port21      Down     -                           -     -           -         - 
2019-10-11 11:43:24 ::   port22      Down     -                           -     -           -         - 
2019-10-11 11:43:24 ::   port23      Down     -                           -     -           -         - 
2019-10-11 11:43:24 ::   port24      Down     -                           -     -           -         - 
2019-10-11 11:43:24 ::   port25      Down     -                           -     -           -         - 
2019-10-11 11:43:24 ::   port26      Down     -                           -     -           -         - 
2019-10-11 11:43:24 ::   port27      Down     -                           -     -           -         - 
2019-10-11 11:43:24 ::   port28      Down     -                           -     -           -         - 
2019-10-11 11:43:24 ::   port29      Down     -                           -     -           -         - 
2019-10-11 11:43:24 ::   port30      Down     -                           -     -           -         - 
2019-10-11 11:43:24 ::   port31      Down     -                           -     -           -         - 
2019-10-11 11:43:24 ::   port32      Down     -                           -     -           -         - 
2019-10-11 11:43:24 ::   port33      Down     -                           -     -           -         - 
2019-10-11 11:43:24 ::   port34      Down     -                           -     -           -         - 
2019-10-11 11:43:24 ::   port35      Down     -                           -     -           -         - 
2019-10-11 11:43:24 ::   port36      Down     -                           -     -           -         - 
2019-10-11 11:43:24 ::   port37      Down     -                           -     -           -         - 
2019-10-11 11:43:24 ::   port38      Down     -                           -     -           -         - 
2019-10-11 11:43:24 ::   port39      Up       -                           -     -           -         - 
2019-10-11 11:43:24 ::   port40      Down     -                           -     -           -         - 
2019-10-11 11:43:24 ::   port41      Down     -                           -     -           -         - 
2019-10-11 11:43:24 ::   port42      Down     -                           -     -           -         - 
2019-10-11 11:43:24 ::   port43      Down     -                           -     -           -         - 
2019-10-11 11:43:24 ::   port44      Down     -                           -     -           -         - 
2019-10-11 11:43:24 ::   port45      Down     -                           -     -           -         - 
2019-10-11 11:43:24 ::   port46      Down     -                           -     -           -         - 
2019-10-11 11:43:24 ::   port47      Up       S548DN4K17000133            120   BR          -         port47 
2019-10-11 11:43:24 ::   port48      Up       S548DN4K17000133            120   BR          -         port48 
2019-10-11 11:43:24 ::   port49      Down     -                           -     -           -         - 
2019-10-11 11:43:24 ::   port50      Down     -                           -     -           -         - 
2019-10-11 11:43:24 ::   port51      Down     -                           -     -           -         - 
2019-10-11 11:43:24 ::   port52      Down     -                           -     -           -         - 
2019-10-11 11:43:24 ::   port53      Down     -                           -     -           -         - 
2019-10-11 11:43:24 ::   port54      Down     -                           -     -           -         - 
2019-10-11 11:43:24 ::  
2019-10-11 11:43:24 :: S548DF4K16000653 # 
2019-10-11 11:43:28 :: show switch interface port39 
2019-10-11 11:43:28 :: config switch interface 
2019-10-11 11:43:28 ::     edit "port39" 
2019-10-11 11:43:28 ::         set allowed-vlans 4093 
2019-10-11 11:43:28 ::         set untagged-vlans 4093 
2019-10-11 11:43:28 ::         set snmp-index 39 
2019-10-11 11:43:28 ::         set log-mac-event enable 
2019-10-11 11:43:28 ::     next 
2019-10-11 11:43:28 :: end 
2019-10-11 11:43:28 ::  
2019-10-11 11:43:28 :: S548DF4K16000653 # 
########################################################################################
2019-10-11 11:43:32 :: get system status 
2019-10-11 11:43:32 :: Version: FortiSwitch-548D v6.2.0,build0192,191005 (Interim) 
2019-10-11 11:43:32 :: Serial-Number: S548DN4K17000133 
2019-10-11 11:43:32 :: BIOS version: 04000013 
2019-10-11 11:43:32 :: System Part-Number: P18057-06 
2019-10-11 11:43:32 :: Burn in MAC: 70:4c:a5:79:22:5a 
2019-10-11 11:43:32 :: Hostname: S548DN4K17000133 
2019-10-11 11:43:32 :: Distribution: International 
2019-10-11 11:43:32 :: Branch point: 192 
2019-10-11 11:43:32 :: System time: Fri Oct 11 11:43:31 2019 
2019-10-11 11:43:32 ::  
2019-10-11 11:43:32 :: S548DN4K17000133 # 
2019-10-11 11:43:36 :: show switch trunk 
2019-10-11 11:43:36 :: config switch trunk 
2019-10-11 11:43:36 ::     edit "8DF4K16000653-0" 
2019-10-11 11:43:36 ::         set mode lacp-active 
2019-10-11 11:43:36 ::         set auto-isl 1 
2019-10-11 11:43:36 ::         set mclag-icl enable 
2019-10-11 11:43:36 ::             set members "port47" "port48" 
2019-10-11 11:43:36 ::     next 
2019-10-11 11:43:36 ::     edit "trunk1" 
2019-10-11 11:43:36 ::         set mode lacp-active 
2019-10-11 11:43:36 ::         set mclag enable 
2019-10-11 11:43:36 ::             set members "port13" 
2019-10-11 11:43:36 ::     next 
2019-10-11 11:43:36 ::     edit "_FlInK1_MLAG0_" 
2019-10-11 11:43:36 ::         set mode lacp-active 
2019-10-11 11:43:36 ::         set auto-isl 1 
2019-10-11 11:43:36 ::         set mclag enable 
2019-10-11 11:43:36 ::             set members "port1" "port2" "port3" "port4" 
2019-10-11 11:43:36 ::     next 
2019-10-11 11:43:36 :: end 
2019-10-11 11:43:36 ::  
2019-10-11 11:43:36 :: S548DN4K17000133 # 
2019-10-11 11:43:40 :: diagnose switch mclag peer-consistency-check 
2019-10-11 11:43:40 ::  
2019-10-11 11:43:40 ::     Running diagnostic, it may take sometime... 
2019-10-11 11:43:40 ::  
2019-10-11 11:43:40 ::     mclag-trunk-name    peer-config lacp-state   stp-state   local-ports            remote-ports 
2019-10-11 11:43:40 ::     __________________  ___________ __________   _________   _____________          _____________ 
2019-10-11 11:43:40 ::  
2019-10-11 11:43:40 ::     8DF4K16000653-0*    OK         UP           OK           port47    port48        port47    port48 
2019-10-11 11:43:40 ::     _FlInK1_MLAG0_      OK         UP           OK           port1     port2         port1     port2 
2019-10-11 11:43:40 ::                                                              port3     port4         port3     port4 
2019-10-11 11:43:40 ::  
2019-10-11 11:43:40 ::     trunk1              OK         UP           OK           port13                  port13 
2019-10-11 11:43:40 ::  
2019-10-11 11:43:40 :: S548DN4K17000133 # 
2019-10-11 11:43:44 :: get switch lldp neighbors-summary 
2019-10-11 11:43:44 ::  
2019-10-11 11:43:44 :: Capability codes: 
2019-10-11 11:43:44 :: 	R:Router, B:Bridge, T:Telephone, C:DOCSIS Cable Device 
2019-10-11 11:43:44 :: 	W:WLAN Access Point, P:Repeater, S:Station, O:Other 
2019-10-11 11:43:44 :: MED type codes: 
2019-10-11 11:43:44 :: 	Generic:Generic Endpoint (Class 1), Media:Media Endpoint (Class 2) 
2019-10-11 11:43:44 :: 	Comms:Communications Endpoint (Class 3), Network:Network Connectivity Device 
2019-10-11 11:43:44 ::  
2019-10-11 11:43:44 ::   Portname    Status   Device-name                 TTL   Capability  MED-type  Port-ID 
2019-10-11 11:43:44 ::   __________  _______  __________________________  ____  __________  ________  _______ 
2019-10-11 11:43:44 ::   port1       Up       S548DF4K17000028            120   BR          -         port1 
2019-10-11 11:43:44 ::   port2       Up       S548DF4K17000028            120   BR          -         port2 
2019-10-11 11:43:44 ::   port3       Up       S548DF4K17000014            120   BR          -         port3 
2019-10-11 11:43:44 ::   port4       Up       S548DF4K17000014            120   BR          -         port4 
2019-10-11 11:43:44 ::   port5       Down     -                           -     -           -         - 
2019-10-11 11:43:44 ::   port6       Down     -                           -     -           -         - 
2019-10-11 11:43:44 ::   port7       Down     -                           -     -           -         - 
2019-10-11 11:43:44 ::   port8       Down     -                           -     -           -         - 
2019-10-11 11:43:44 ::   port9       Down     -                           -     -           -         - 
2019-10-11 11:43:44 ::   port10      Down     -                           -     -           -         - 
2019-10-11 11:43:44 ::   port11      Down     -                           -     -           -         - 
2019-10-11 11:43:44 ::   port12      Down     -                           -     -           -         - 
2019-10-11 11:43:44 ::   port13      Up       SW2                         120   BR          Network   port14 
2019-10-11 11:43:44 ::   port14      Down     -                           -     -           -         - 
2019-10-11 11:43:44 ::   port15      Down     -                           -     -           -         - 
2019-10-11 11:43:44 ::   port16      Down     -                           -     -           -         - 
2019-10-11 11:43:44 ::   port17      Down     -                           -     -           -         - 
2019-10-11 11:43:44 ::   port18      Down     -                           -     -           -         - 
2019-10-11 11:43:44 ::   port19      Down     -                           -     -           -         - 
2019-10-11 11:43:44 ::   port20      Down     -                           -     -           -         - 
2019-10-11 11:43:44 ::   port21      Down     -                           -     -           -         - 
2019-10-11 11:43:44 ::   port22      Down     -                           -     -           -         - 
2019-10-11 11:43:44 ::   port23      Down     -                           -     -           -         - 
2019-10-11 11:43:44 ::   port24      Down     -                           -     -           -         - 
2019-10-11 11:43:44 ::   port25      Down     -                           -     -           -         - 
2019-10-11 11:43:44 ::   port26      Down     -                           -     -           -         - 
2019-10-11 11:43:44 ::   port27      Down     -                           -     -           -         - 
2019-10-11 11:43:44 ::   port28      Down     -                           -     -           -         - 
2019-10-11 11:43:44 ::   port29      Down     -                           -     -           -         - 
2019-10-11 11:43:44 ::   port30      Down     -                           -     -           -         - 
2019-10-11 11:43:44 ::   port31      Down     -                           -     -           -         - 
2019-10-11 11:43:44 ::   port32      Down     -                           -     -           -         - 
2019-10-11 11:43:44 ::   port33      Down     -                           -     -           -         - 
2019-10-11 11:43:44 ::   port34      Down     -                           -     -           -         - 
2019-10-11 11:43:44 ::   port35      Down     -                           -     -           -         - 
2019-10-11 11:43:44 ::   port36      Down     -                           -     -           -         - 
2019-10-11 11:43:44 ::   port37      Down     -                           -     -           -         - 
2019-10-11 11:43:44 ::   port38      Down     -                           -     -           -         - 
2019-10-11 11:43:44 ::   port39      Up       -                           -     -           -         - 
2019-10-11 11:43:44 ::   port40      Down     -                           -     -           -         - 
2019-10-11 11:43:44 ::   port41      Down     -                           -     -           -         - 
2019-10-11 11:43:44 ::   port42      Down     -                           -     -           -         - 
2019-10-11 11:43:44 ::   port43      Down     -                           -     -           -         - 
2019-10-11 11:43:44 ::   port44      Down     -                           -     -           -         - 
2019-10-11 11:43:44 ::   port45      Down     -                           -     -           -         - 
2019-10-11 11:43:44 ::   port46      Down     -                           -     -           -         - 
2019-10-11 11:43:44 ::   port47      Up       S548DF4K16000653            120   BR          -         port47 
2019-10-11 11:43:44 ::   port48      Up       S548DF4K16000653            120   BR          -         port48 
2019-10-11 11:43:44 ::   port49      Down     -                           -     -           -         - 
2019-10-11 11:43:44 ::   port50      Down     -                           -     -           -         - 
2019-10-11 11:43:44 ::   port51      Down     -                           -     -           -         - 
2019-10-11 11:43:44 ::   port52      Down     -                           -     -           -         - 
2019-10-11 11:43:44 ::   port53      Down     -                           -     -           -         - 
2019-10-11 11:43:44 ::   port54      Down     -                           -     -           -         - 
2019-10-11 11:43:44 ::  
2019-10-11 11:43:44 :: S548DN4K17000133 # 
2019-10-11 11:43:48 :: show switch interface port39 
2019-10-11 11:43:48 :: config switch interface 
2019-10-11 11:43:48 ::     edit "port39" 
2019-10-11 11:43:48 ::         set allowed-vlans 4093 
2019-10-11 11:43:48 ::         set untagged-vlans 4093 
2019-10-11 11:43:48 ::         set snmp-index 39 
2019-10-11 11:43:48 ::         set log-mac-event enable 
2019-10-11 11:43:48 ::     next 
2019-10-11 11:43:48 :: end 
2019-10-11 11:43:48 ::  
2019-10-11 11:43:48 :: S548DN4K17000133 # 
