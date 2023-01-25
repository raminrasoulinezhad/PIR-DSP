% it supports bias --> exact number

%%
clear 
clc

% Parameter & MAC counter
ImageNet_k = 1000;

MACs_Conv = 0;
Parameters_Conv = 0;
MACs_AP = 0;

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

% input picture
i = 224;
c = 3;

% c = normal conv
% f = fire unit
% a = avgpool 13x13
% m = max pool 3x3/stride=2 
% p = pointwise (FC layer)
op_list = ['c', 'm', 'f', 'f', 'f', 'm', 'f', 'f', 'f', 'f', 'm', 'f', 'p', 'a'];
squeez_list = [0,0,16,16, 32,0, 32, 48, 48, 64,0, 64,0,0];
expand_list = [0,0,64,64,128,0,128,192,192,256,0,256,0,0];      % for both 1x1 and 3x3

for index = 1 : length(op_list)
  switch op_list(index)
      case 'c'
          c_next = 96;
          kernel = 7;
          i = (i/2) - 1 ;

          parameter_temp = c_next * (kernel * kernel * c);
          bias_temp = c_next;
          mac_temp = parameter_temp * i * i;
          
          [Power_Rimp, Power_Ours] = PIR_PowerEstimator(Power_Rimp, Power_Ours, '3D', i, 0, kernel, 2, mac_temp);
          
          
          Parameters_Conv = Parameters_Conv + parameter_temp + bias_temp;
          MACs_Conv = MACs_Conv + mac_temp;
          c = c_next;
          
          D3_num = c_next;
          D3_size= kernel;
          D3_MAC = D3_MAC + mac_temp;
          D3_Pa  = D3_Pa + parameter_temp + bias_temp;
       
      case 'm'
          i = floor(i/2);
      case 'f'
          s_local = squeez_list(index);
          e_local = expand_list(index);
          
          parameter_temp1 = (1*1*c)*s_local;
          mac_temp1 = parameter_temp1 * i * i;
          [Power_Rimp, Power_Ours] = PIR_PowerEstimator(Power_Rimp, Power_Ours, 'PW', i, s_local, 0, 1, mac_temp1);  
          
          PW_ch  = [PW_ch, c];
          
          c = s_local;
          
          parameter_temp2 = (1*1*c) * e_local;
          mac_temp2 = parameter_temp2 * i * i;
          [Power_Rimp, Power_Ours] = PIR_PowerEstimator(Power_Rimp, Power_Ours, 'PW', i, e_local, 0, 1, mac_temp2);  
          
          parameter_temp3 = (3*3*c) * e_local;
          mac_temp3 = parameter_temp3 * i * i;
          [Power_Rimp, Power_Ours] = PIR_PowerEstimator(Power_Rimp, Power_Ours, '3D', i, 0, 3, 1, mac_temp3);
          
          PW_ch  = [PW_ch, c];
          c = 2 * e_local;
          
          bias_temp = s_local + e_local + e_local;
          
          Parameters_Conv = Parameters_Conv + parameter_temp1 + parameter_temp2 + parameter_temp3 + bias_temp;
          MACs_Conv = MACs_Conv + mac_temp1 + mac_temp2 + mac_temp3;
          
          D3_num = D3_num + e_local;
          D3_size= [D3_size, 3];
          D3_MAC = D3_MAC + mac_temp3;
          D3_Pa  = D3_Pa + parameter_temp3 + e_local;

          PW_num = PW_num  + s_local + e_local;
          %PW_ch  = [PW_ch, ]; % calculated among up lines --> distributed
          PW_MAC = PW_MAC + mac_temp1 + mac_temp2;
          PW_Pa  = PW_Pa + parameter_temp1 + parameter_temp2 + s_local + e_local;
          
          
      case 'a'
          mac_temp = i * i * c * 13 * 13;
          MACs_AP = MACs_AP + mac_temp;
          %MACs_Conv = MACs_Conv + mac_temp;
          i = 1;
      case 'p'          
          c_next = ImageNet_k;
          parameter_temp = c_next * (1 * 1 * c);
          bias_temp = c_next;
          mac_temp = parameter_temp * i * i;
          
          [Power_Rimp, Power_Ours] = PIR_PowerEstimator(Power_Rimp, Power_Ours, 'PW', i, c_next, 0, 1, mac_temp); 
          
          Parameters_Conv = Parameters_Conv + parameter_temp + bias_temp;
          MACs_Conv = MACs_Conv + mac_temp;
          
          PW_num = PW_num  + c_next;
          PW_ch  = [PW_ch, c]; 
          PW_MAC = PW_MAC + mac_temp;
          PW_Pa  = PW_Pa + parameter_temp + bias_temp;
          
          c = c_next;    
      otherwise
          disp('eroor')
  end    
end
fprintf('--- Results fo SqueezNet ---\n');
fprintf('Conv: \t#parameter=%d,\t #MAC=%d\n', Parameters_Conv, MACs_Conv);
Parameters_Total = Parameters_Conv;
MACs_Total = MACs_Conv + MACs_AP;
fprintf('------\n');
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


