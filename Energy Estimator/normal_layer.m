function [parameter, MAC, MAC_A, i, c, i_p, c_p, DW_num, DW_ch, DW_d, DW_MAC, DW_Pa, PW_num, PW_ch, PW_MAC, PW_Pa, Power_Rimp, Power_Ours] = normal_layer(i, c, i_p, c_p, filters, DW_num, DW_ch, DW_d, DW_MAC, DW_Pa, PW_num, PW_ch, PW_MAC, PW_Pa, Power_Rimp, Power_Ours)

    %%%cur = floor(filters/2)(x, prev)
    if (i ~= i_p)%%%%%%%%%%%%%%%%%%%%%%%%% i am not sure maybe i ~= i_p
      parameter_temp0 = (filters/2) * (1 * 1 * c_p);
      mac_temp0 = parameter_temp0 * floor((i_p+1)/2) * floor((i_p+1)/2);  
      
      [Power_Rimp, Power_Ours] = PIR_PowerEstimator(Power_Rimp, Power_Ours, 'PW', floor((i_p+1)/2), (filters/2), 0, 1, mac_temp0);  
      
      parameter_temp1 = (filters/2) * (1 * 1 * c_p);
      mac_temp1 = parameter_temp1 * floor((i_p+1)/2) * floor((i_p+1)/2);  
      
      [Power_Rimp, Power_Ours] = PIR_PowerEstimator(Power_Rimp, Power_Ours, 'PW', floor((i_p+1)/2), (filters/2), 0, 1, mac_temp1);  

      
      PW_num = PW_num + filters;
      PW_ch  = [PW_ch, c_p];
      PW_MAC = PW_MAC + mac_temp0 + mac_temp1;
      PW_Pa  = PW_Pa + parameter_temp0 + parameter_temp1;
      
      c_p = filters;
      i_p = floor((i_p+1)/2);
    else
      parameter_temp0 = filters * (1 * 1 * c_p);
      mac_temp0 = parameter_temp0 * i_p * i_p; 
      
      [Power_Rimp, Power_Ours] = PIR_PowerEstimator(Power_Rimp, Power_Ours, 'PW', i_p, filters, 0, 1, mac_temp0); 
      
      parameter_temp1 = 0;
      mac_temp1 = 0;

      PW_num = PW_num + filters;
      PW_ch  = [PW_ch, c_p];
      PW_MAC = PW_MAC + mac_temp0 + mac_temp1;
      PW_Pa  = PW_Pa + parameter_temp0 + parameter_temp1;
      
      c_p = filters;
      i_p = i_p;
    end

    parameter_temp2 = filters * (1 * 1 * c);
    mac_temp2 = parameter_temp2 * i * i; 
    
    [Power_Rimp, Power_Ours] = PIR_PowerEstimator(Power_Rimp, Power_Ours, 'PW', i, filters, 0, 1, mac_temp2);
    
    PW_num = PW_num + filters;
    PW_ch  = [PW_ch, c];
    PW_MAC = PW_MAC + mac_temp2;
    PW_Pa  = PW_Pa + parameter_temp2;
    
    c = filters;
    i = i;
    
    parameter = parameter_temp0 + parameter_temp1 + parameter_temp2;
    MAC = mac_temp0 + mac_temp1 + mac_temp2;
    
    
    %[parameter, MAC] = sep(kernel, strides, i, c, filters)
    %[parameter, MAC] = avgpool(kernel, i, c, strides)

    % add0 -- sep5(cur) & sep3(prev)
    [parameter_temp0, mac_temp0, DW_num, DW_ch, DW_d, DW_MAC, DW_Pa, PW_num, PW_ch, PW_MAC, PW_Pa, Power_Rimp, Power_Ours] = sep(5, 1, i, c, filters, DW_num, DW_ch, DW_d, DW_MAC, DW_Pa, PW_num, PW_ch, PW_MAC, PW_Pa, Power_Rimp, Power_Ours);
    [parameter_temp1, mac_temp1, DW_num, DW_ch, DW_d, DW_MAC, DW_Pa, PW_num, PW_ch, PW_MAC, PW_Pa, Power_Rimp, Power_Ours] = sep(3, 1, i_p, c_p, filters, DW_num, DW_ch, DW_d, DW_MAC, DW_Pa, PW_num, PW_ch, PW_MAC, PW_Pa, Power_Rimp, Power_Ours);
    % add1 -- sep5(prev) & sep3(prev)
    [parameter_temp2, mac_temp2, DW_num, DW_ch, DW_d, DW_MAC, DW_Pa, PW_num, PW_ch, PW_MAC, PW_Pa, Power_Rimp, Power_Ours] = sep(5, 1, i_p, c_p, filters, DW_num, DW_ch, DW_d, DW_MAC, DW_Pa, PW_num, PW_ch, PW_MAC, PW_Pa, Power_Rimp, Power_Ours);
    [parameter_temp3, mac_temp3, DW_num, DW_ch, DW_d, DW_MAC, DW_Pa, PW_num, PW_ch, PW_MAC, PW_Pa, Power_Rimp, Power_Ours] = sep(3, 1, i_p, c_p, filters, DW_num, DW_ch, DW_d, DW_MAC, DW_Pa, PW_num, PW_ch, PW_MAC, PW_Pa, Power_Rimp, Power_Ours);
    % add2 -- avgpool(cur)  identical
    [parameter_temp4, mac_temp4] = avgpool(3, i, c, 1);
    % add3 -- avgpool(prev) avgpool(prev)
    [parameter_temp5, mac_temp5] = avgpool(3, i_p, c_p, 1);
    [parameter_temp6, mac_temp6] = avgpool(3, i_p, c_p, 1);
    % add4 -- sep3(cur)  maxpool
    [parameter_temp7, mac_temp7, DW_num, DW_ch, DW_d, DW_MAC, DW_Pa, PW_num, PW_ch, PW_MAC, PW_Pa, Power_Rimp, Power_Ours] = sep(3, 1, i, c, filters, DW_num, DW_ch, DW_d, DW_MAC, DW_Pa, PW_num, PW_ch, PW_MAC, PW_Pa, Power_Rimp, Power_Ours);
    
    parameter = parameter + parameter_temp0+parameter_temp1+parameter_temp2+parameter_temp3+parameter_temp7;
    MAC = MAC + mac_temp0+mac_temp1+mac_temp2+mac_temp3+mac_temp7;
    MAC = MAC + 5 * i * i * filters;
    MAC_A = mac_temp4 + mac_temp5 + mac_temp6;
    % prepare
    i_p = i;
    c_p = c;

    i = i;
    c = filters * 6;
end


