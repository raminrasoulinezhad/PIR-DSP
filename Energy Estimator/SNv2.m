%%
clear 
clc


% Parameter & MAC counter
ImageNet_k = 1000;

MACs_Conv = 0;
MACs_FC = 0;
MACs_PConv = 0;
MACs_AP = 0;
Parameters_Conv = 0;
Parameters_FC = 0;
Parameters_PConv = 0;


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
kernel = 3;

n_list = [1, 1, 1, 3, 1, 7, 1, 3, 1, 1, 1];
s_list = [2, 2, 2, 1, 2, 1, 2, 1, 1, 1, 1];

%c_list = [24, 24, 48, 48, 96, 96, 192, 192, 1024, 1024, ImageNet_k];        % 0.5x
c_list = [24, 24, 116, 116, 232, 232, 464, 464, 1024, 1024, ImageNet_k];    % 1x
%c_list = [24, 24, 176, 176, 352, 352, 704, 704, 1024, 1024, ImageNet_k];    % 1.5x
%c_list = [24, 24, 244, 244, 488, 488, 976, 976, 2048, 2048, ImageNet_k];    % 2x

% c = normal conv
% u = simple unit
% d = downsample unit
% a = avgpool 7x7
% p = point-wise conv
% m = max pool 3x3 
op_list = ['c', 'm', 'd', 'u', 'd', 'u', 'd', 'u', 'p', 'a', 'f'];

for index = 1 : length(op_list)
  switch op_list(index)
      case 'c'
          c_next = c_list(index);
          
          i = floor(i/s_list(index));

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
          
      case 'm'
          c_next = c_list(index);
          i = floor(i/s_list(index));
          c = c_next;
      case 'd'
           
          c_next = c_list(index);
          i_half = floor(i/s_list(index));

          % right side new
          parameter_temp1 = (1*1*c)*(c);
          mac_temp1 = parameter_temp1 * i * i;
          [Power_Rimp, Power_Ours] = PIR_PowerEstimator(Power_Rimp, Power_Ours, 'PW', i, c, 0, 1, mac_temp1);
          
          parameter_temp2 = (3*3*1) * (c);
          mac_temp2 = parameter_temp2 * i_half * i_half;
          [Power_Rimp, Power_Ours] = PIR_PowerEstimator(Power_Rimp, Power_Ours, 'DW', i_half, 0, 3, 2, mac_temp2);

          parameter_temp3 = (1*1*(c)) * (c_next/2);
          mac_temp3 = parameter_temp3 * i_half * i_half;
          [Power_Rimp, Power_Ours] = PIR_PowerEstimator(Power_Rimp, Power_Ours, 'PW', i_half, (c_next/2), 0, 1, mac_temp3);
          
          
          % left side new
          parameter_temp4 = (3*3*1) * c;
          mac_temp4 = parameter_temp4 * i_half * i_half;
          [Power_Rimp, Power_Ours] = PIR_PowerEstimator(Power_Rimp, Power_Ours, 'DW', i_half, 0, 3, 2, mac_temp4);

          parameter_temp5 = (1*1*c) * (c_next/2);
          mac_temp5 = parameter_temp5 * i_half * i_half;
          [Power_Rimp, Power_Ours] = PIR_PowerEstimator(Power_Rimp, Power_Ours, 'PW', i_half, (c_next/2), 0, 1, mac_temp5);
          
          % summation 
          Parameters_Conv = Parameters_Conv + parameter_temp1 + parameter_temp2 + parameter_temp3 + parameter_temp4 + parameter_temp5;
          MACs_Conv = MACs_Conv + mac_temp1 + mac_temp2 + mac_temp3 + mac_temp4 + mac_temp5;

          
          DW_num = DW_num + c + c;
          DW_ch  = [DW_ch, c, c];
          DW_d   = [DW_d , i_half, i_half];
          DW_MAC = DW_MAC + mac_temp2 + mac_temp4;
          DW_Pa  = DW_Pa + parameter_temp2 + parameter_temp4;

          PW_num = PW_num + c + (c_next/2) + (c_next/2);
          PW_ch  = [PW_ch, c, (c_next/2), (c_next/2)];
          PW_MAC = PW_MAC + mac_temp1 + mac_temp3 + mac_temp5;
          PW_Pa  = PW_Pa + parameter_temp1 + parameter_temp3 + parameter_temp5;


          c = c_next;
          i = i_half;
          
      case 'u'
          for index_in = 1 : n_list(index)
              c_right = c/2;

              % right side
              parameter_temp1 = (1*1*c_right) * c_right;
              mac_temp1 = parameter_temp1 * i * i;
              [Power_Rimp, Power_Ours] = PIR_PowerEstimator(Power_Rimp, Power_Ours, 'PW', i, c_right, 0, 1, mac_temp1);
              
              parameter_temp2 = (3*3*1) * c_right;
              mac_temp2 = parameter_temp2 * i * i;
              [Power_Rimp, Power_Ours] = PIR_PowerEstimator(Power_Rimp, Power_Ours, 'DW', i, 0, 3, 1, mac_temp2);

              parameter_temp3 = (1*1*c_right) * c_right;
              mac_temp3 = parameter_temp3 * i * i;
              [Power_Rimp, Power_Ours] = PIR_PowerEstimator(Power_Rimp, Power_Ours, 'PW', i, c_right, 0, 1, mac_temp3);
              
              % summation 
              Parameters_Conv = Parameters_Conv + parameter_temp1 + parameter_temp2 + parameter_temp3;
              MACs_Conv = MACs_Conv + mac_temp1 + mac_temp2 + mac_temp3;
              
              DW_num = DW_num + c_right;
              DW_ch  = [DW_ch, c_right];
              DW_d   = [DW_d , i];
              DW_MAC = DW_MAC + mac_temp2;
              DW_Pa  = DW_Pa + parameter_temp2;

              PW_num = PW_num + c_right + c_right;
              PW_ch  = [PW_ch, c_right, c_right];
              PW_MAC = PW_MAC + mac_temp1 + mac_temp3;
              PW_Pa  = PW_Pa + parameter_temp1 + parameter_temp3;

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
          [Power_Rimp, Power_Ours] = PIR_PowerEstimator(Power_Rimp, Power_Ours, 'PW', i, c_next, 0, 1, mac_temp);
          
              PW_num = PW_num + c_next;
              PW_ch  = [PW_ch, c_next];
              PW_MAC = PW_MAC + mac_temp;
              PW_Pa  = PW_Pa + parameter_temp;
              
          Parameters_PConv = Parameters_PConv + parameter_temp;
          MACs_PConv = MACs_PConv + mac_temp;
          c = c_next;    
      case 'f'
          c_next = c_list(index);
          
          parameter_temp = c_next * (1 * 1 * c);
          mac_temp = parameter_temp * i * i;
          [Power_Rimp, Power_Ours] = PIR_PowerEstimator(Power_Rimp, Power_Ours, 'FC', 0, c_next, 0, 0, mac_temp);
          
          Parameters_FC = Parameters_FC + parameter_temp;
          MACs_FC = MACs_FC + mac_temp;
          c = c_next; 
      otherwise
          disp('eroor')
  end    
end
fprintf('--- Results fo ShuffelNet v2 ---\n');
fprintf('Conv: \t#parameter=%d,\t #MAC=%d\n', Parameters_Conv, MACs_Conv);
fprintf('FC: \t#parameter=%d,\t #MAC=%d\n', Parameters_FC, MACs_FC);
fprintf('PConv: \t#parameter=%d,\t #MAC=%d\n', Parameters_PConv, MACs_PConv);
Parameters_Total = Parameters_Conv + Parameters_FC + Parameters_PConv;
MACs_Total = MACs_Conv + MACs_FC + MACs_PConv+MACs_AP;
fprintf('------\n');
fprintf('Total: \t\t\t#parameter=%d,\t #MAC=%d\n', Parameters_Total, MACs_Total);
fprintf('Total(Conv + ConvP): \t#parameter=%d,\t #MAC=%d\n', Parameters_Conv + Parameters_PConv, MACs_Conv + MACs_PConv);


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
