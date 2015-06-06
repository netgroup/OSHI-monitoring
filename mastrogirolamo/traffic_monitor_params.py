REQUEST_INTERVAL = 1    #Stats request time interval. MUST BE 1
DELTA_WINDOW = 20       #RATE WINDOWS

LLDP_NOISE_BYTE_S = 19
LLDP_NOISE_PACK_S = 0.365

'''
                                                                                                
                                                OUT=out+lldp        OUT=out+lldp                
                                                IN =in              IN =in                      

                                          +-------|vi0 |------|vi1 |------|vi2 |----------------+
                                          |                                                     |
                                          |                                                     |
    OUT=out+lldp                        ----                                                    |
    IN =in                              eth0                 SWITCH                             |
                                        ----                                                    |
    sdn_out=out-in(vi)=OUT-lldp-in(vi)    |                                                     |
    sdn_in =in-out(vi)=IN-OUT(vi)-lldp    |                                                     |
                                          |                                                     |
                                          |                                                     |
                                          +-------------------|eth1|------|eth2|----------------+

                                                            OUT=out+lldp                        
                                                            IN =in +lldp
                                                            sdn_out=out-in(vi)=OUT-lldp-IN(vi)
                                                            sdn_in =in-out(vi)=IN-lldp-OUT(vi)+lldp=IN-OUT(vi)

'''