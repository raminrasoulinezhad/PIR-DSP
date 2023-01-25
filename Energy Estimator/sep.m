function [parameter, MAC, DW_num, DW_ch, DW_d, DW_MAC, DW_Pa, PW_num, PW_ch, PW_MAC, PW_Pa, Power_Rimp, Power_Ours] = sep(kernel, strides, i, c, filters, DW_num, DW_ch, DW_d, DW_MAC, DW_Pa, PW_num, PW_ch, PW_MAC, PW_Pa, Power_Rimp, Power_Ours)
    
    i = floor((i+1)/strides);
    
    parameter_temp0 = c * (kernel * kernel * 1);
    mac_temp0 = parameter_temp0 * i * i;
    [Power_Rimp, Power_Ours] = PIR_PowerEstimator(Power_Rimp, Power_Ours, 'DW', i, 0, kernel, strides, mac_temp0);
    
    parameter_temp1 = filters * (1 * 1 * c);
    mac_temp1 = parameter_temp1 * i * i;
    [Power_Rimp, Power_Ours] = PIR_PowerEstimator(Power_Rimp, Power_Ours, 'PW', i, filters, 0, 1, mac_temp1);  
    
    PW_ch  = [PW_ch, c];
    
    c = filters;
    
    parameter_temp2 = c * (kernel * kernel * 1);
    mac_temp2 = parameter_temp2 * i * i;
    [Power_Rimp, Power_Ours] = PIR_PowerEstimator(Power_Rimp, Power_Ours, 'DW', i, 0, kernel, 1, mac_temp2);
    
    parameter_temp3 = filters * (1 * 1 * c);
    mac_temp3 = parameter_temp3 * i * i;
    [Power_Rimp, Power_Ours] = PIR_PowerEstimator(Power_Rimp, Power_Ours, 'PW', i, filters, 0, 1, mac_temp3);  
    
    PW_ch  = [PW_ch, c];
        
    parameter = parameter_temp0 + parameter_temp1 + parameter_temp2 + parameter_temp3;
    MAC = mac_temp0 + mac_temp1 + mac_temp2 + mac_temp3;
    
    DW_num = DW_num + c + c;
    DW_ch = [DW_ch, c, c];
    DW_d   = [DW_d , i];
    DW_MAC = DW_MAC + mac_temp0 + mac_temp2;
    DW_Pa  = DW_Pa + parameter_temp0 + parameter_temp2;

    PW_num = PW_num + filters + filters;
    %global PW_ch;
    %PW_ch  = [PW_ch, c, c*t_list(index)];
    PW_MAC = PW_MAC + mac_temp1 + mac_temp3;
    PW_Pa  = PW_Pa + parameter_temp1 + parameter_temp3;
end

