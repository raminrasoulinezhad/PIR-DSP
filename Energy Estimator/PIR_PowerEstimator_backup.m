function [Power_Rimp, Power_Ours] = PIR_PowerEstimator(Power_Rimp, Power_Ours, functionality, index, N, kernel, stride, MAC)
    Pb = 4.5;
    Psr = 1;
    Prf = 1;
    Pc = 0.75;
    PRFe = 0.5;
    Pf = 0.5;
    RFs = 4;
    
    
     
    Pb = 205;
    Psr = 44;
    Prf = 40;
    Pc = 23;
    PRFe = 12.5;
    PSRe = 2;
    Pf = 1;
    RFs = 4;
    
    


    switch functionality
        case '3D' 
            if ((stride == 1) && (kernel == 3))
                Power_Rimp(1) = Power_Rimp(1) + ((Pb/(kernel*kernel)) + Psr + Pf   +   (Pb/(index*index)) + Pf) * MAC;
                Power_Ours(1) = Power_Ours(1) + (( Pb + 2*Pc ) / (RFs*kernel*kernel) + PSRe    +     Pb/(index*index) + PRFe) * MAC;
            elseif ((stride == 2) && (kernel == 3))
                Power_Rimp(1) = Power_Rimp(1) + ((Pb/(kernel*kernel)) + Psr + Pf   +   (Pb/(index*index)) + Pf) * MAC;
                Power_Ours(1) = Power_Ours(1) + ((Pb+Pc)/(RFs*2*2) + PSRe   +   (Pb/(index*index)) + PRFe) * MAC;
            elseif ((stride == 2) && (kernel == 5))
                Power_Rimp(1) = Power_Rimp(1) + ((Pb/(kernel*kernel)) + Psr + Pf   +   (Pb/(index*index)) + Pf) * MAC;
                Power_Ours(1) = Power_Ours(1) + ((Pb+2*Pc)/(RFs*3*3) + PSRe   +   (Pb/(index*index)) + PRFe ) * MAC;
            elseif ((stride == 2) && (kernel == 7))
                Power_Rimp(1) = Power_Rimp(1) + ((Pb/(kernel*kernel)) + Psr + Pf   +   (Pb/(index*index)) + Pf) * MAC;
                Power_Ours(1) = Power_Ours(1) + ((Pb+6*Pc)/(RFs*4*4) + PSRe   +   (Pb/(index*index)) + PRFe ) * MAC;
            else 
                disp ('$$$ PIR_PowerEstimator: Error $$')
            end
        case 'DW'
            if ((stride == 1) && (kernel == 3))
                Power_Rimp(2) = Power_Rimp(2) + ((Pb/(kernel*kernel)) + Psr + Pf   +   (Pb/(index*index)) + Pf) * MAC;
                Power_Ours(2) = Power_Ours(2) + (( Pb + 2*Pc ) / (kernel*kernel) + PSRe    +     PRFe + Pb/(index*index)) * MAC;
            elseif ((stride == 1) && (kernel == 5))
                Power_Rimp(2) = Power_Rimp(2) + ((Pb/(kernel*kernel)) + Psr + Pf   +   (Pb/(index*index)) + Pf) * MAC;
                Power_Ours(2) = Power_Ours(2) + (( Pb + 6*Pc ) / (kernel*kernel) + PSRe    +     PRFe + Pb/(index*index)) * MAC;
            elseif ((stride == 1) && (kernel == 7))
                Power_Rimp(2) = Power_Rimp(2) + ((Pb/(kernel*kernel)) + Psr + Pf   +   (Pb/(index*index)) + Pf) * MAC;
                Power_Ours(2) = Power_Ours(2) + (( Pb + 12*Pc ) / (kernel*kernel) + PSRe    +     PRFe + Pb/(index*index)) * MAC;
            
            elseif ((stride == 2) && (kernel == 3))
                Power_Rimp(2) = Power_Rimp(2) + ((Pb/(kernel*kernel)) + Psr + Pf   +   (Pb/(index*index)) + Pf) * MAC;
                Power_Ours(2) = Power_Ours(2) + ((Pb+Pc)/(2*2) + PSRe   +   (Pb/(index*index)) + PRFe) * MAC;
            elseif ((stride == 2) && (kernel == 5))
                Power_Rimp(2) = Power_Rimp(2) + ((Pb/(kernel*kernel)) + Psr + Pf   +   (Pb/(index*index)) + Pf) * MAC;
                Power_Ours(2) = Power_Ours(2) + ((Pb+2*Pc)/(3*3) + PSRe   +   (Pb/(index*index)) + PRFe ) * MAC;
            elseif ((stride == 2) && (kernel == 7))
                Power_Rimp(2) = Power_Rimp(2) + ((Pb/(kernel*kernel)) + Psr + Pf   +   (Pb/(index*index)) + Pf) * MAC;
                Power_Ours(2) = Power_Ours(2) + ((Pb+6*Pc)/(4*4) + PSRe   +   (Pb/(index*index)) + PRFe ) * MAC;
            else 
                disp ('$$$ PIR_PowerEstimator: Error $$')
            end
            
        case 'PW'
                Power_Rimp(3) = Power_Rimp(3) + (Pb/N + Psr + Pf      +     (Pb/(index*index)) + Pf) * MAC;
                Power_Ours(3) = Power_Ours(3) + ((Pb/N + Pc)/RFs + PSRe      +     (Pb/(index*index)) + PRFe) * MAC;
        case 'FC'
                Power_Rimp(4) = Power_Rimp(4) + ((Pb/(N)) + Pf + Pb + Pf) * MAC;
                Power_Ours(4) = Power_Ours(4) + ((Pb/(N)) + PSRe + Pb + PRFe) * MAC;
        otherwise 
            disp ('$$$ PIR_PowerEstimator: Error $$')
    end    
    
    
    
%     switch functionality
%         case '3D' 
%             if ((stride == 1) && (kernel == 3))
%                 Power_Rimp(1) = Power_Rimp(1) + ((Pb/kernel) + Psr + Pf   +   (Pb/index) + Pf) * MAC;
%                 Power_Ours(1) = Power_Ours(1) + (( Pb + (kernel-1)*Pc ) / (RFs*kernel*kernel) + Pf    +     Pf + Pb/index) * MAC;
%             elseif ((stride == 2) && (kernel == 3))
%                 Power_Rimp(1) = Power_Rimp(1) + ((Pb/kernel) + Psr + Pf   +   (Pb/index) + Pf) * MAC;
%                 Power_Ours(1) = Power_Ours(1) + ((Pb+Pc)/(RFs*2*2) + Pf   +   (Pb/index) + Pf) * MAC;
%             elseif ((stride == 2) && (kernel == 5))
%                 Power_Rimp(1) = Power_Rimp(1) + ((Pb/kernel) + Psr + Pf   +   (Pb/index) + Pf) * MAC;
%                 Power_Ours(1) = Power_Ours(1) + ((Pb+3*Psr+2*Pc)/(RFs*3*3) + Pf   +   (Pb/index) + Pf ) * MAC;
%             elseif ((stride == 2) && (kernel == 7))
%                 Power_Rimp(1) = Power_Rimp(1) + ((Pb/kernel) + Psr + Pf   +   (Pb/index) + Pf) * MAC;
%                 Power_Ours(1) = Power_Ours(1) + ((Pb+8*Psr+6*Pc)/(RFs*4*4) + Pf   +   (Pb/index) + Pf ) * MAC;
%             else 
%                 disp ('$$$ PIR_PowerEstimator: Error $$')
%             end
%         case 'DW'
%             if ((stride == 1) && (kernel == 3))
%                 Power_Rimp(2) = Power_Rimp(2) + ((Pb/kernel) + Psr + Pf   +   (Pb/index) + Pf) * MAC;
%                 Power_Ours(2) = Power_Ours(2) + (( Pb + 2*Pc ) / (kernel*kernel) + Pf    +     Pf + Pb/index) * MAC;
%             elseif ((stride == 1) && (kernel == 5))
%                 Power_Rimp(2) = Power_Rimp(2) + ((Pb/kernel) + Psr + Pf   +   (Pb/index) + Pf) * MAC;
%                 Power_Ours(2) = Power_Ours(2) + (( Pb + 3*Psr + 6*Pc ) / (kernel*kernel) + Pf    +     Pf + Pb/index) * MAC;
%             elseif ((stride == 1) && (kernel == 7))
%                 Power_Rimp(2) = Power_Rimp(2) + ((Pb/kernel) + Psr + Pf   +   (Pb/index) + Pf) * MAC;
%                 Power_Ours(2) = Power_Ours(2) + (( Pb + 8*Psr + 12*Pc ) / (kernel*kernel) + Pf    +     Pf + Pb/index) * MAC;
%             
%             elseif ((stride == 2) && (kernel == 3))
%                 Power_Rimp(2) = Power_Rimp(2) + ((Pb/kernel) + Psr + Pf   +   (Pb/index) + Pf) * MAC;
%                 Power_Ours(2) = Power_Ours(2) + ((Pb+Pc)/(2*2) + Pf   +   (Pb/index) + Pf) * MAC;
%             elseif ((stride == 2) && (kernel == 5))
%                 Power_Rimp(2) = Power_Rimp(2) + ((Pb/kernel) + Psr + Pf   +   (Pb/index) + Pf) * MAC;
%                 Power_Ours(2) = Power_Ours(2) + ((Pb+3*Psr+2*Pc)/(3*3) + Pf   +   (Pb/index) + Pf ) * MAC;
%             elseif ((stride == 2) && (kernel == 7))
%                 Power_Rimp(2) = Power_Rimp(2) + ((Pb/kernel) + Psr + Pf   +   (Pb/index) + Pf) * MAC;
%                 Power_Ours(2) = Power_Ours(2) + ((Pb+8*Psr+6*Pc)/(4*4) + Pf   +   (Pb/index) + Pf ) * MAC;
%             else 
%                 disp ('$$$ PIR_PowerEstimator: Error $$')
%             end
%             
%         case 'PW'
%                 Power_Rimp(3) = Power_Rimp(3) + (Pb/N + Psr + Pf      +     (Pb/(index*index)) + Pf) * MAC;
%                 Power_Ours(3) = Power_Ours(3) + ((Pb/N + Psr)/RFs + Pf      +     (Pb/(index*index)) + Pf) * MAC;
%         case 'FC'
%                 Power_Rimp(4) = Power_Rimp(4) + ((Pb/(N)) + 1 + Pb + 1) * MAC;
%                 Power_Ours(4) = Power_Ours(4) + ((Pb/(N)) + 1 + Pb + 1) * MAC;
%         otherwise 
%             disp ('$$$ PIR_PowerEstimator: Error $$')
%     end    
end

