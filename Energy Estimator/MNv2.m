%%
clear 
clc

%% 
% Parameter & MAC counter
ImageNet_k = 1000;

MACs_Conv = 0;
MACs_FC = 0;
MACs_AP = 0;

Parameters_Conv = 0;
Parameters_FC = 0;

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
% input picture
i = 224;
c = 3;
kernel = 3;

n_list = [1, 1, 2, 3, 4, 3, 3, 1, 1, 1, 0];
s_list = [2, 1, 2, 2, 2, 1, 2, 1, 1, 0, 0];
t_list = [0, 1, 6, 6, 6, 6, 6, 6, 0, 0, 0];
c_list = [32, 16, 24, 32, 64, 96, 160, 320, 1280, 0, ImageNet_k];
% c = normal conv
% b = bottleneck
% a = avgpool 7x7
% p = point-wise conv
op_list = ['c', 'b', 'b', 'b', 'b', 'b', 'b', 'b', 'p', 'a', 'f'];

%%
for index = 1 : length(op_list)

  switch op_list(index)
      case 'c'
          c_next = c_list(index);
          i = floor(i/s_list(index));
          
          parameter_temp = c_next * (kernel * kernel * c);
          mac_temp = parameter_temp * i * i;
          
          %Power_Rimp = Power_Rimp + (2 + (4.5/kernel)+(4.5/i) ) * mac_temp;
          %Power_Ours = Power_Ours + (1+(4.5/i)+((4.5+(3/16))/(2*2))) * mac_temp;
          [Power_Rimp, Power_Ours] = PIR_PowerEstimator(Power_Rimp, Power_Ours, '3D', i, 0, kernel, 2, mac_temp);
          
          
          Parameters_Conv = Parameters_Conv + parameter_temp;
          MACs_Conv = MACs_Conv + mac_temp;
          c = c_next;
          
          
          D3_num = c_next;
          D3_size= kernel;
          D3_MAC = D3_MAC + mac_temp;
          D3_Pa  = D3_Pa + parameter_temp;
      case 'b'
          for index_in = 1 : n_list(index)
              
              if index_in == 1
                  s_local = s_list(index);
              else
                  s_local = 1;
              end
              c_next = c_list(index);
              
              parameter_temp1 = ((1*1*c)*c*t_list(index));
              mac_temp1 = parameter_temp1 * i * i;
              
              %Power_Rimp = Power_Rimp + ((4.5/(c*t_list(index))) + (4.5/(i*i)) + 2) * mac_temp1;
              %Power_Ours = Power_Ours + ((4.5/(c*t_list(index))) + (4.5/(i*i)) + 19/16) * mac_temp1;
              %[Power_Rimp, Power_Ours] = PIR_PowerEstimator(Power_Rimp, Power_Ours, functionality, index, N, kernel, stride, MAC)
              [Power_Rimp, Power_Ours] = PIR_PowerEstimator(Power_Rimp, Power_Ours, 'PW', i, c*t_list(index), 0, 1, mac_temp1);
              
              if index_in == 1
                  i = floor(i/s_list(index));
              end
              
              parameter_temp2 = (3*3*1) * c*t_list(index);
              %mac_temp2 = parameter_temp2 * floor(i/s_local) * floor(i/s_local);
              mac_temp2 = parameter_temp2 * i * i;
              
              %Power_Rimp = Power_Rimp + (2 + (4.5/3)+(4.5/i) ) * mac_temp2;
              %Power_Ours = Power_Ours + (1+(4.5/i)+((4.5+(3/4)*(3-1))/(3*3))) * mac_temp2;
              %[Power_Rimp, Power_Ours] = PIR_PowerEstimator(Power_Rimp, Power_Ours, functionality, index, N, kernel, stride, MAC)
              [Power_Rimp, Power_Ours] = PIR_PowerEstimator(Power_Rimp, Power_Ours, 'DW', i, 0, 3, s_local, mac_temp2);

              parameter_temp3 = ((1*1*c*t_list(index))*c_next);
              %mac_temp3 = parameter_temp3 * floor(i/s_local) * floor(i/s_local);
              mac_temp3 = parameter_temp3 * i * i;
              
              %Power_Rimp = Power_Rimp + ((4.5/(c_next)) + (4.5/(i*i)) + 2) * mac_temp3;
              %Power_Ours = Power_Ours + ((4.5/(c_next)) + (4.5/(i*i)) + 19/16) * mac_temp3;
              %[Power_Rimp, Power_Ours] = PIR_PowerEstimator(Power_Rimp, Power_Ours, functionality, index, N, kernel, stride, MAC)
              [Power_Rimp, Power_Ours] = PIR_PowerEstimator(Power_Rimp, Power_Ours, 'PW', i, c_next, 0, 1, mac_temp3);
              
              Parameters_Conv = Parameters_Conv + parameter_temp1+parameter_temp2+parameter_temp3;
              MACs_Conv = MACs_Conv + mac_temp1+mac_temp2+mac_temp3;
              
              DW_num = DW_num + c * t_list(index);
              DW_ch  = [DW_ch, c * t_list(index)];
              DW_d   = [DW_d , floor(i/s_local)];
              DW_MAC = DW_MAC + mac_temp2;
              DW_Pa  = DW_Pa + parameter_temp2;
              
              PW_num = PW_num + c*t_list(index) + c_next;
              PW_ch  = [PW_ch, c, c*t_list(index)];
              PW_MAC = PW_MAC + mac_temp1 + mac_temp3;
              PW_Pa  = PW_Pa + parameter_temp1 + parameter_temp3;
              
              c = c_next;
              
              
          end
      case 'a'
          mac_temp = i * i * c * 7 * 7;
          
          MACs_AP = MACs_AP + mac_temp;
          %MACs_FC = MACs_FC + mac_temp;
          i = 1;
      case 'p'
          c_next = c_list(index);
          
          parameter_temp = c_next * (1 * 1 * c);
          mac_temp = parameter_temp * i * i;
          
          %Power_Rimp = Power_Rimp + ((4.5/(c_next)) + (4.5/(i*i)) + 2) * mac_temp;
          %Power_Ours = Power_Ours + ((4.5/(c_next)) + (4.5/(i*i)) + 19/16) * mac_temp;
          %[Power_Rimp, Power_Ours] = PIR_PowerEstimator(Power_Rimp, Power_Ours, functionality, index, N, kernel, stride, MAC)
          [Power_Rimp, Power_Ours] = PIR_PowerEstimator(Power_Rimp, Power_Ours, 'PW', i, c_next, 0, 1, mac_temp);
              
          Parameters_Conv = Parameters_Conv + parameter_temp;
          MACs_Conv = MACs_Conv + mac_temp;
          
          PW_num = PW_num + c_next;
          PW_ch  = [PW_ch, c];
          PW_MAC = PW_MAC + mac_temp;
          PW_Pa  = PW_Pa + parameter_temp;

          c = c_next;    
      case 'f'
          c_next = c_list(index);
          
          parameter_temp = c_next * (1 * 1 * c);
          mac_temp = parameter_temp * i * i;
          
          %Power_FC = ((4.5/(c_next)) + 1 + 4.5 + 1) * mac_temp;
          %Power_Rimp = Power_Rimp + ((4.5/(c_next)) + 1 + 4.5 + 1) * mac_temp;
          %Power_Ours = Power_Ours + ((4.5/(c_next)) + 1 + 4.5 + 1) * mac_temp;
          %[Power_Rimp, Power_Ours] = PIR_PowerEstimator(Power_Rimp, Power_Ours, functionality, index, N, kernel, stride, MAC)
          [Power_Rimp, Power_Ours] = PIR_PowerEstimator(Power_Rimp, Power_Ours, 'FC', 0, c_next, 0, 0, mac_temp);
          
          Parameters_FC = Parameters_FC + parameter_temp;
          MACs_FC = MACs_FC + mac_temp;
          c = c_next; 
  end    
end

%%
fprintf('--- Results fo MobileNet v2 ---\n');
fprintf('Conv: \t#parameter=%d,\t #MAC=%d\n', Parameters_Conv, MACs_Conv);
fprintf('FC: \t#parameter=%d,\t #MAC=%d\n', Parameters_FC, MACs_FC);
Parameters_Total = Parameters_Conv + Parameters_FC;
MACs_Total = MACs_Conv + MACs_FC + MACs_AP;
fprintf('Total: \t#parameter=%d,\t #MAC=%d\n', Parameters_Total, MACs_Total);

fprintf('------\n');
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

