traffic_stats = {'status': '1', 'measure_mode': 'mixed', 'waiting_for_stats': '0', 'flow': {'2': {'rx': {'pkt_loss_duration': 'N/A', 'total_pkt_rate': '0.000', 'total_pkt_kbit_rate': '0.000', 'total_pkt_mbit_rate': '0.000', 'port': '1/1/1', 'total_pkt_byte_rate': '0.000', 'expected_pkts': 'N/A', 'last_tstamp': '00:00:32.459', 'misdirected_ports': 'N/A', 'reverse_error': 'N/A', 'total_pkt_bytes': '3732279000', 'loss_percent': '4.191', 'min_delay': '40300', 'loss_pkts': '163250', 'total_pkts_bytes': '3732279000', 'avg_delay': '41623', 'first_tstamp': '00:00:00.671', 'total_pkt_bit_rate': '0.000', 'l1_bit_rate': '0.000', 'total_pkts': '3732279', 'misdirected_rate': 'N/A', 'small_error': 'N/A', 'misdirected_pkts': 'N/A', 'big_error': 'N/A', 'max_delay': '45320'}, 'tx': {'total_pkt_rate': '0.000', 'total_pkt_kbit_rate': '0.000', 'total_pkt_mbit_rate': '0.000', 'total_pkt_byte_rate': '0.000', 'total_pkt_bit_rate': '0.000', 'total_pkts': '3895529', 'port': '1/1/2', 'l1_bit_rate': '0.000'}, 'pgid_value': 'N/A', 'tracking': {'2': {'tracking_value': '100.1.0.2-100.1.0.1', 'tracking_name': 'Source/Dest Endpoint Pair'}, '1': {'tracking_value': 'TI1-Traffic_Item_2', 'tracking_name': 'Traffic Item'}, 'count': '2'}, 'flow_name': '1/1/1 TI1-Traffic_Item_2 100.1.0.2-100.1.0.1'}, '1': {'tracking': {'1': {'tracking_value': 'TI0-Traffic_Item_1', 'tracking_name': 'Traffic Item'}, '2': {'tracking_name': 'Source/Dest Endpoint Pair', 'tracking_value': '100.1.0.1-100.1.0.2'}, 'count': '2'}, 'flow_name': '1/1/2 TI0-Traffic_Item_1 100.1.0.1-100.1.0.2', 'rx': {'expected_pkts': 'N/A', 'port': '1/1/2', 'reverse_error': 'N/A', 'total_pkt_kbit_rate': '0.000', 'total_pkt_mbit_rate': '0.000', 'misdirected_rate': 'N/A', 'big_error': 'N/A', 'max_delay': '44060', 'misdirected_pkts': 'N/A', 'total_pkt_byte_rate': '0.000', 'loss_percent': '0.050', 'last_tstamp': '00:00:32.459', 'pkt_loss_duration': 'N/A', 'first_tstamp': '00:00:00.671', 'misdirected_ports': 'N/A', 'l1_bit_rate': '0.000', 'loss_pkts': '1942', 'min_delay': '39840', 'total_pkt_bit_rate': '0.000', 'avg_delay': '41276', 'total_pkt_rate': '0.000', 'small_error': 'N/A', 'total_pkts_bytes': '3893587000', 'total_pkts': '3893587', 'total_pkt_bytes': '3893587000'}, 'tx': {'total_pkt_kbit_rate': '0.000', 'total_pkt_mbit_rate': '0.000', 'total_pkt_byte_rate': '0.000', 'port': '1/1/1', 'total_pkt_bit_rate': '0.000', 'total_pkt_rate': '0.000', 'total_pkts': '3895529', 'l1_bit_rate': '0.000'}, 'pgid_value': 'N/A'}}}

def print_flow_stats(stats_list):
	for flow in flow_list:
		print ("Flow ID:{}, RX_Port:{}, TX_Port:{}, TX packet rate:{}, Pkt Loss:{}, Pkt Loss time:{}". \
			format(flow['id'],flow['rx_port'],flow['tx_port'],flow['total_pkt_rate'], \
				flow['loss_pkts'],flow["loss_time"]))
		print ("\n")

		print("--------------------------------")
for k, v in traffic_stats.items():
	if k == "flow":
		flow_stats = v
		break
flow_num = list(flow_stats.keys())[0]

 
flow_stats_items = flow_stats[flow_num]
#print(flow_stats_items)
flow_list = []
for k, v in flow_stats.items():
	flow_info = {}
	flow_info['id'] = k
	flow_info['rx'] = rx_stats = v['rx']
	flow_info['tx'] = tx_stats = v['tx']
	flow_info['rx_port'] = rx_stats['port']
	flow_info['total_pkts'] = int(rx_stats['total_pkts'])
	flow_info['total_pkts_bytes'] = int(rx_stats['total_pkts_bytes'])

	flow_info['loss_pkts'] = int(rx_stats['loss_pkts'])
	flow_info['max_delay'] = int(rx_stats['max_delay'])
	flow_info['total_pkt_rate'] =float(tx_stats['total_pkt_rate'])
	if flow_info['total_pkt_rate'] != 0:
		flow_info["loss_time"] = str(flow_info['loss_pkts']/flow_info['total_pkt_rate']) + " " + "seconds"
	else:
		flow_info["loss_time"] = "0 seconds"
	flow_info['tx_port'] = tx_stats['port']
	flow_list.append(flow_info)

print_flow_stats(flow_list)
 