% it supports bias --> exact number
%https://github.com/EN10/NASNet
%https://github.com/EN10/NASNet/blob/master/nasnet.py
%%
clear 
clc

%% 
D3_num = 0;
D3_size= [];
D3_MAC = 0;
D3_Pa  = 0;

DW_num = 0;
DW_ch  = [];
DW_d  = [];
DW_MAC = 0;
DW_Pa  = 0;

PW_num = 0;
PW_ch  = [];
PW_MAC = 0;
PW_Pa  = 0;

%Power     = [3D,DW,PW,FC];
Power_Rimp = [0,0,0,0];
Power_Ours = [0,0,0,0];

%%
% Parameter & MAC counter
ImageNet_k = 1000;
num_classes = ImageNet_k;

%add_aux_output=aux_output;
%stem=ImagenetStem;
stem_filters=32;

N = 4;
num_cell_repeats = N;
num_reduction_cells = 2;               
penultimate_filters = 1056;

%% 
MACs_Conv = 0;
Parameters_Conv = 0;
Parameters_FC = 0;
MACs_FC = 0;
MACs_AP = 0;

% c = normal conv
% f = fire unit
% a = avgpool 13x13
% m = max pool 3x3/stride=2 
% p = pointwise (FC layer)
op_list =  ['i', 'c', 'R', 'n', 'r', 'n', 'r', 'n', 's'];
rep_list = [1, 1, 2, N, 1, N, 1, N, 1];

for index = 1 : length(op_list)
  switch op_list(index)
      case 'i'
          % input picture
          i = 224;
          c = 3;
      case 'c'
          %no bias, stride=2, 

          c_next = stem_filters;
          kernel = 3;
          i = i/2;

          parameter_temp = c_next * (kernel * kernel * c);
          mac_temp = parameter_temp * i * i;
          
          [Power_Rimp, Power_Ours] = PIR_PowerEstimator(Power_Rimp, Power_Ours, '3D', i, 0, kernel, 2, mac_temp);
          
          Parameters_Conv = Parameters_Conv + parameter_temp;
          MACs_Conv = MACs_Conv + mac_temp;
          
          c = c_next;

          D3_num = c_next;
          D3_size= kernel;
          D3_MAC = D3_MAC + mac_temp;
          D3_Pa  = D3_Pa + parameter_temp;
          
      case 'R'    
          filters = penultimate_filters / (pow2(num_reduction_cells) * 6);
          
          %%%prev = floor(filters/4)(None, x)
          
          %prev = x --> nothing
          
          %cur = sqeezed(x) --> floor(filter/4) pointwise on x --> 
          filters = floor(filters / 4);
          
          parameter_temp = filters * (1 * 1 * c);
          mac_temp = parameter_temp * i * i;
          
          [Power_Rimp, Power_Ours] = PIR_PowerEstimator(Power_Rimp, Power_Ours, 'PW', i, filters, 0, 1, mac_temp);
          
            PW_num = PW_num + filters;
            PW_ch  = [PW_ch, c];
            PW_MAC = PW_MAC + mac_temp;
            PW_Pa  = PW_Pa + parameter_temp;
    
          % prepare 
          i_p = i;
          c_p = c;
          
          i = i;
          c = filters;
          
          
          
          % first reduced layer 
          
          %[parameter, MAC] = sep(kernel, strides, i, c, filters)
          %[parameter, MAC] = avgpool(kernel, i, c, strides)
          
          % add0 -- sep5(cur) & sep7(prev)
          [parameter_temp0, mac_temp0, DW_num, DW_ch, DW_d, DW_MAC, DW_Pa, PW_num, PW_ch, PW_MAC, PW_Pa, Power_Rimp, Power_Ours] = sep(5, 2, i, c, filters, DW_num, DW_ch, DW_d, DW_MAC, DW_Pa, PW_num, PW_ch, PW_MAC, PW_Pa, Power_Rimp, Power_Ours);
          [parameter_temp1, mac_temp1, DW_num, DW_ch, DW_d, DW_MAC, DW_Pa, PW_num, PW_ch, PW_MAC, PW_Pa, Power_Rimp, Power_Ours] = sep(7, 2, i_p, c_p, filters, DW_num, DW_ch, DW_d, DW_MAC, DW_Pa, PW_num, PW_ch, PW_MAC, PW_Pa, Power_Rimp, Power_Ours);
          % add1 -- maxpool  sep7(prev)
          [parameter_temp2, mac_temp2, DW_num, DW_ch, DW_d, DW_MAC, DW_Pa, PW_num, PW_ch, PW_MAC, PW_Pa, Power_Rimp, Power_Ours] = sep(7, 2, i_p, c_p, filters, DW_num, DW_ch, DW_d, DW_MAC, DW_Pa, PW_num, PW_ch, PW_MAC, PW_Pa, Power_Rimp, Power_Ours);
          % add2 -- avgpool(cur)  sep5(prev)
          [parameter_temp3, mac_temp3] = avgpool(3, i, c, 1);
          [parameter_temp4, mac_temp4, DW_num, DW_ch, DW_d, DW_MAC, DW_Pa, PW_num, PW_ch, PW_MAC, PW_Pa, Power_Rimp, Power_Ours] = sep(5, 2, i_p, c_p, filters, DW_num, DW_ch, DW_d, DW_MAC, DW_Pa, PW_num, PW_ch, PW_MAC, PW_Pa, Power_Rimp, Power_Ours);
          % add3 -- avgpool(and0,cur)
          [parameter_temp5, mac_temp5] = avgpool(5, floor((i+1)/2), filters, 1);
          % add4 -- sep3(cur)  maxpool
          [parameter_temp6, mac_temp6, DW_num, DW_ch, DW_d, DW_MAC, DW_Pa, PW_num, PW_ch, PW_MAC, PW_Pa, Power_Rimp, Power_Ours] = sep(3, 1, floor((i+1)/2), filters, filters, DW_num, DW_ch, DW_d, DW_MAC, DW_Pa, PW_num, PW_ch, PW_MAC, PW_Pa, Power_Rimp, Power_Ours);
          
          
          
          % prepare
          i_p = i;
          c_p = c;
          
          i = floor((i+1)/2);
          c = filters * 4;
          
          Parameters_Conv = Parameters_Conv + parameter_temp +parameter_temp0+parameter_temp1+parameter_temp2+parameter_temp4+parameter_temp6;
          MACs_Conv = MACs_Conv + mac_temp+mac_temp0+mac_temp1+mac_temp2+mac_temp4+mac_temp6;
          MACs_AP = MACs_AP + mac_temp3 + mac_temp5;
          
          filters =  filters * 2;
          
          [parameter, MAC, MAC_A, i, c, i_p, c_p, DW_num, DW_ch, DW_d, DW_MAC, DW_Pa, PW_num, PW_ch, PW_MAC, PW_Pa, Power_Rimp, Power_Ours] = reduction_layer(i, c, i_p, c_p, filters, DW_num, DW_ch, DW_d, DW_MAC, DW_Pa, PW_num, PW_ch, PW_MAC, PW_Pa, Power_Rimp, Power_Ours);
          Parameters_Conv = Parameters_Conv + parameter;
          MACs_Conv = MACs_Conv + MAC;
          MACs_AP = MACs_AP + MAC_A;

          filters =  filters * 2;
      case 'r'
          
          filters = 2 * filters;
          [parameter, MAC, MAC_A, i, c, i_p, c_p, DW_num, DW_ch, DW_d, DW_MAC, DW_Pa, PW_num, PW_ch, PW_MAC, PW_Pa, Power_Rimp, Power_Ours] = reduction_layer(i, c, i_p, c_p, filters, DW_num, DW_ch, DW_d, DW_MAC, DW_Pa, PW_num, PW_ch, PW_MAC, PW_Pa, Power_Rimp, Power_Ours);
          Parameters_Conv = Parameters_Conv + parameter;
          MACs_Conv = MACs_Conv + MAC;
          MACs_AP = MACs_AP + MAC_A;
      case 'n'
          for iter = 1 : rep_list(index)
              [parameter, MAC, MAC_A, i, c, i_p, c_p, DW_num, DW_ch, DW_d, DW_MAC, DW_Pa, PW_num, PW_ch, PW_MAC, PW_Pa, Power_Rimp, Power_Ours] = normal_layer(i, c, i_p, c_p, filters, DW_num, DW_ch, DW_d, DW_MAC, DW_Pa, PW_num, PW_ch, PW_MAC, PW_Pa, Power_Rimp, Power_Ours);
              Parameters_Conv = Parameters_Conv + parameter;
              MACs_Conv = MACs_Conv + MAC;
              MACs_AP = MACs_AP + MAC_A;
          end
      case 's'
          
          [parameter1, MAC1] = avgpool(5, i, c, 3);
          i = floor(i/3)+1;
          MACs_AP = MACs_AP + MAC1;
          
          parameter2 = 128 * (1 * 1 * c);
          MAC2 = parameter2 * i * i;
          
          [Power_Rimp, Power_Ours] = PIR_PowerEstimator(Power_Rimp, Power_Ours, 'PW', i, 128, 0, 1, MAC2); 
          
            PW_num = PW_num + 128;
            PW_ch  = [PW_ch, c];
            PW_MAC = PW_MAC + MAC2;
            PW_Pa  = PW_Pa + parameter2;
            
          c = 128;
          
          parameter3 = 768 * (i * i * c);
          MAC3 = parameter3 * i * i;
          
          [Power_Rimp, Power_Ours] = PIR_PowerEstimator(Power_Rimp, Power_Ours, '3D', i, 0, i, 1, MAC3);
          
          D3_num = D3_num +  768;
          D3_size= i;
          D3_MAC = D3_MAC + MAC3;
          D3_Pa  = D3_Pa + parameter3;
          
          c = 768;
          
          parameter4 = 0;
          MAC4 = i * i * c;
          MACs_AP = MACs_AP + MAC4;
          
          i = 1;
          
          parameter5 = c * num_classes;
          MAC5 = parameter5;
          
          [Power_Rimp, Power_Ours] = PIR_PowerEstimator(Power_Rimp, Power_Ours, 'FC', 0, num_classes, 0, 0, MAC5);
          
          Parameters_Conv = Parameters_Conv + parameter2 + parameter3;
          MACs_Conv = MACs_Conv + MAC2 + MAC3;
 
          Parameters_FC = Parameters_FC + parameter5;
          MACs_FC = MACs_FC + MAC5;
      otherwise
          disp('eroor')
  end    
end
fprintf('--- Results fo NASNet  ---\n');
fprintf('Conv: \t#parameter=%d,\t #MAC=%d\n', Parameters_Conv, MACs_Conv);
fprintf('FC: \t#parameter=%d,\t #MAC=%d\n', Parameters_FC, MACs_FC);
Parameters_Total = Parameters_Conv + Parameters_FC;
MACs_Total = MACs_Conv + MACs_FC + MACs_AP;
fprintf('Total: \t#parameter=%d,\t #MAC=%d\n', Parameters_Total, MACs_Total);


fprintf('--------------------\n');
fprintf('D3_num:\t%d,\tD3_MAC:\t%3.1f,\tD3_Pa:\t%3.1f\n', D3_num, (D3_MAC/MACs_Total)*100, (D3_Pa/Parameters_Total)*100);
unique(sort(D3_size))

fprintf('DW_num:\t%d,\tDW_MAC:\t%3.1f,\tDW_Pa:\t%3.1f\n', DW_num, (DW_MAC/MACs_Total)*100, (DW_Pa/Parameters_Total)*100);
unique(sort(DW_ch))
unique(sort(DW_d))

fprintf('PW_num:\t%d,\tPW_MAC:\t%3.1f,\tPW_Pa:\t%3.1f\n', PW_num, (PW_MAC/MACs_Total)*100, (PW_Pa/Parameters_Total)*100);
unique(sort(PW_ch))

fprintf('Non 3d, DW, PW, FC computation is (percentage): %3.10f\n', (MACs_AP/MACs_Total)*100);

fprintf('--- Read Access Power estimation ---\n');
fprintf('Power_Rimp:\t\t\t%d,\nPower_Ours:\t\t\t%3.1f,\nReductionRatio:\t\t\t%5.3f,\nRatio:------------%5.3f,\nPowerFC/PowerOurs ratio:\t%5.3f\n', sum(Power_Rimp), sum(Power_Ours), (sum(Power_Rimp)-sum(Power_Ours))/sum(Power_Rimp), sum(Power_Ours)/sum(Power_Rimp), Power_Ours(4)/sum(Power_Ours));
fprintf('--- percentages: [3D,DW,PW,FC] ---\n');
Power_Rimp/sum(Power_Rimp)*100
Power_Ours/sum(Power_Ours)*100
fprintf('--- reductions: [3D,DW,PW,FC] ---\n');
((Power_Rimp - Power_Ours)./Power_Rimp)*100


