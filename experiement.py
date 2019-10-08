def dict_lacp_boot_update(**kwargs):
    '''
    create multivalue config
    Arguments:
     -topology_handle:
       ALPHA
     -nest_step:
       ANY
     -nest_owner:
       ANY
     -counter_start:
       NUMERIC
    return:
     -multivalue_handle
    '''
   
    tkwargs = {
    }
    for key, value in kwargs.items():
        tkwargs[key]=value
    print(tkwargs)

dict_lacp_boot_update(dir_list="abc",dut="dut1",mem=8,result="boot_result")